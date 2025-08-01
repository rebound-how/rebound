use std::net::IpAddr;
use std::net::Ipv4Addr;
use std::net::SocketAddr;
use std::str::FromStr;
use std::sync::Arc;
use std::sync::Mutex;
use std::time::Duration;
use std::time::Instant;

use anyhow::Result;
use arc_swap::ArcSwap;
use chrono::Utc;
use kanal::AsyncReceiver;
use parse_duration;
use tokio::sync::watch;
use url::Url;
use uuid::Uuid;

use super::ScenarioItem;
use super::event::ScenarioEvent;
use super::event::ScenarioItemLifecycle;
use super::strategy::load;
use super::strategy::repeat;
use super::strategy::single;
use super::types::ItemResult;
use super::types::ScenarioGlobalConfig;
use crate::config::FaultConfig;
use crate::config::ProxyConfig;
use crate::errors::ProxyError;
use crate::event::TaskManager;
use crate::event::TaskProgressReceiver;
use crate::fault::FaultInjector;
use crate::plugin::load_injectors;
use crate::proxy;
use crate::proxy::ProxyState;
use crate::proxy::monitor_and_update_proxy_config;
use crate::proxy::protocols::http::proxy::init::initialize_http_proxy;
use crate::proxy::protocols::tcp::init::initialize_tcp_proxies;
use crate::scenario::event::ScenarioEventManager;
use crate::scenario::types::Scenario;
use crate::scenario::types::ScenarioResult;
use crate::scenario::types::ScenariosResults;
use crate::sched;
use crate::sched::run_fault_schedule;
use crate::types::ProxyAddrConfig;
use crate::types::ProxyMap;
use crate::types::RemoteAddrConfig;

pub(crate) mod http;

pub async fn execute_item(
    item: ScenarioItem,
    event: Arc<ScenarioEvent>,
    global_config: Option<ScenarioGlobalConfig>,
    addr_id_map: Arc<scc::HashMap<String, Uuid>>,
    id_events_map: Arc<scc::HashMap<Uuid, ScenarioItemLifecycle>>,
    task_manager: Arc<TaskManager>,
) -> Result<ItemResult> {
    let (proxy_shutdown_tx, proxy_shutdown_rx) = kanal::bounded_async(5);

    let proxy_state = Arc::new(ProxyState::new(false));
    set_upstream_hosts_from_item(&item.clone(), proxy_state.clone()).await;

    let (config_tx, config_rx) = watch::channel((
        ProxyConfig::default(),
        Vec::<Box<dyn FaultInjector>>::new(),
    ));

    let remote_target = item.call.url.clone();

    let url = Url::parse(remote_target.as_str()).unwrap();
    let remote_host = url.host_str().ok_or("Missing host").unwrap().to_string();
    let remote_port = url.port_or_known_default().unwrap();

    let _ = ProxyMap::parse_side(
        &format!("{}://{}:{}", url.scheme(), remote_host, remote_port),
        None,
    )
    .map_err(|s| ProxyError::Other(s))?;

    let _proxy_updater_handle = tokio::spawn(monitor_and_update_proxy_config(
        proxy_state.clone(),
        config_rx,
    ));

    let mut enable_http_proxies = true;
    let _proxy_handle;

    if let Some(proxying) = item.context.proxy.clone() {
        enable_http_proxies = !proxying.disable_http_proxies;

        let proxy_map = ProxyMap::parse_many(proxying.proxies)
            .map_err(|s| ProxyError::Other(s))?;
        _proxy_handle = initialize_tcp_proxies(
            proxy_map,
            proxy_state.clone(),
            proxy_shutdown_rx.clone(),
            task_manager.clone(),
        )
        .await;
    }

    let proxy_address = format!("127.0.0.1:{}", "3180");
    let _proxy_handle;

    let mut set_proxy = false;
    if enable_http_proxies {
        tracing::debug!("Enabling HTTP proxy {} on scenario", proxy_address);

        set_proxy = true;

        let proxy_config = ProxyAddrConfig {
            proxy_ip: Ipv4Addr::from_str("127.0.0.1")?,
            proxy_port: 3180,
        };

        _proxy_handle = initialize_http_proxy(
            &proxy_config,
            proxy_state.clone(),
            proxy_shutdown_rx.clone(),
            task_manager.clone(),
        )
        .await;
    }

    let result;

    if let Some(strategy) = item.context.strategy.clone() {
        result = match strategy {
            super::types::ScenarioItemCallStrategy::Repeat {
                failfast,
                step,
                count,
                wait,
                add_baseline_call,
            } => Ok(repeat::execute(
                proxy_address,
                item,
                global_config,
                event,
                config_tx,
                addr_id_map,
                id_events_map,
                step,
                failfast.is_some_and(|x| x),
                count,
                add_baseline_call.is_some_and(|x| x),
                wait,
            )
            .await?),
            super::types::ScenarioItemCallStrategy::Load {
                duration,
                clients,
                rps,
                ..
            } => {
                let duration = parse_duration::parse(&duration)?;

                Ok(load::execute(
                    proxy_address,
                    item,
                    global_config,
                    event,
                    proxy_state.clone(),
                    addr_id_map,
                    id_events_map,
                    duration,
                    clients,
                    rps,
                    set_proxy,
                )
                .await?)
            }
            super::types::ScenarioItemCallStrategy::Single {} => {
                Ok(single::execute(
                    proxy_address,
                    item,
                    global_config,
                    config_tx,
                    addr_id_map,
                    id_events_map,
                    event,
                )
                .await?)
            }
        };
    } else {
        result = Ok(single::execute(
            proxy_address,
            item,
            global_config,
            config_tx,
            addr_id_map,
            id_events_map,
            event,
        )
        .await?);
    }

    tracing::debug!("Shutting down scenario item proxy");
    let _ = proxy_shutdown_tx.send(()).await;

    result
}

pub async fn set_proxy_config_from_item(
    item: &ScenarioItem,
    config_tx: watch::Sender<(ProxyConfig, Vec<Box<dyn FaultInjector>>)>,
) {
    let faults = item.context.faults.clone();
    let fault_config: Vec<FaultConfig> =
        faults.iter().map(|f| f.build().unwrap()).collect();
    let new_config =
        ProxyConfig { faults: Arc::new(ArcSwap::from_pointee(fault_config)) };

    let injectors: Vec<Box<dyn FaultInjector>> = load_injectors(&new_config);

    tracing::debug!("{:?} {:?}", new_config, injectors);

    if config_tx.send((new_config, injectors)).is_err() {
        tracing::error!("Proxy task has been shut down.");
    }
}

pub async fn update_proxy_from_fault_schedule(
    item: ScenarioItem,
    starting_point: tokio::time::Instant,
    total_duration: Duration,
    proxy_state: Arc<ProxyState>,
) {
    let faults = item.context.faults.clone();
    let fault_config: Vec<FaultConfig> =
        faults.iter().map(|f| f.build().unwrap()).collect();
    let new_config =
        ProxyConfig { faults: Arc::new(ArcSwap::from_pointee(fault_config)) };

    let injectors: Vec<Box<dyn FaultInjector>> = load_injectors(&new_config);

    let fault_schedule = sched::build_schedule_events_from_scenario_item(
        &item.context.faults,
        starting_point,
        total_duration,
    );

    run_fault_schedule(fault_schedule, proxy_state.clone(), injectors).await;
}

pub async fn set_upstream_hosts_from_item(
    item: &ScenarioItem,
    proxy_state: Arc<ProxyState>,
) {
    let upstream_hosts = item.context.upstreams.clone();
    let upstreams: Vec<String> =
        upstream_hosts.iter().map(|h| upstream_to_addr(h).unwrap()).collect();
    proxy_state.set_upstream_hosts(upstreams).await;
}

fn upstream_to_addr(
    host: &String,
) -> Result<String, Box<dyn std::error::Error>> {
    let url_str = if host.contains("://") {
        host.to_string()
    } else {
        format!("scheme://{}", host)
    };

    let url = Url::parse(&url_str)?;
    let host = url.host_str().ok_or("Missing host")?.to_string();
    let port = url.port_or_known_default().unwrap();

    Ok(format!("{}:{}", host, port))
}

pub async fn run_one(item: &ScenarioItem) -> Result<ItemResult> {
    let task_manager = TaskManager::new();
    let (event_manager, _) = ScenarioEventManager::new(500);

    let addr_id_map: Arc<scc::HashMap<String, Uuid>> =
        Arc::new(scc::HashMap::default());

    let id_events_map: Arc<scc::HashMap<Uuid, ScenarioItemLifecycle>> =
        Arc::new(scc::HashMap::default());

    let event = Arc::new(event_manager.new_event().await.unwrap());

    let scenario_config = ScenarioGlobalConfig::default();

    Ok(execute_item(
        item.clone(),
        event.clone(),
        Some(scenario_config),
        addr_id_map.clone(),
        id_events_map.clone(),
        task_manager.clone(),
    )
    .await?)
}

pub async fn run_scenario_first_item(
    scenario: Scenario,
) -> Result<ScenariosResults> {
    let start = Utc::now();
    let mut results = Vec::new();

    if let Some(item) = scenario.items.first() {
        let item_result = run_one(&item).await?;
        results.push(item_result);
    }

    let final_results = ScenariosResults {
        start,
        end: Utc::now(),
        results: vec![ScenarioResult { scenario: scenario, results: results }],
    };

    Ok(final_results)
}
