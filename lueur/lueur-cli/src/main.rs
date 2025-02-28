// used by duration to access as_millis_f64() which is available in edition2024
#![feature(duration_millis_float)]

mod cli;
mod config;
mod demo;
#[cfg(all(target_os = "linux", feature = "stealth"))]
mod ebpf;
mod errors;
mod event;
mod fault;
mod logging;
#[cfg(all(target_os = "linux", feature = "stealth"))]
mod nic;
mod plugin;
mod proxy;
mod reporting;
mod resolver;
mod scenario;
mod termui;
mod types;

use std::collections::HashMap;
use std::env;
use std::fs::File;
use std::io::Write;
use std::net::IpAddr;
use std::net::SocketAddr;
use std::path::Path;
use std::path::PathBuf;
use std::sync::Arc;
use std::sync::Mutex;
use std::time::Duration;
use std::time::Instant;

use anyhow::Result;
#[cfg(all(target_os = "linux", feature = "stealth"))]
use aya::Ebpf;
use clap::Parser;
use cli::Cli;
use cli::Commands;
use cli::DemoCommands;
use cli::ProxyAwareCommandCommon;
use cli::ScenarioCommands;
use colored::Colorize;
use colorful::Color;
use colorful::Colorful;
use colorful::ExtraColorInterface;
use config::ProxyConfig;
use errors::ProxyError;
use event::TaskManager;
use indicatif::MultiProgress;
use indicatif::ProgressBar;
use indicatif::ProgressStyle;
use logging::init_meter_provider;
use logging::init_subscriber;
use logging::init_tracer_provider;
use logging::setup_logging;
use logging::shutdown_tracer;
use opentelemetry_sdk::metrics::SdkMeterProvider;
use opentelemetry_sdk::trace::TracerProvider;
use proxy::ProxyState;
use proxy::run_proxy;
use reporting::OutputFormat;
use reporting::Report;
use reporting::ReportItem;
use reporting::ReportItemExpectation;
use reporting::ReportItemExpectationDecision;
use reporting::ReportItemMetrics;
use reporting::ReportItemMetricsFaults;
use reporting::build_report_output;
use reporting::pretty_report;
use scenario::ScenarioEventManager;
use scenario::ScenarioItemLifecycle;
use scenario::ScenarioItemLifecycleFaults;
use scenario::build_item_list;
use scenario::count_scenario_items;
use scenario::execute_item;
use scenario::handle_scenario_events;
use scenario::load_scenarios;
use termui::handle_displayable_events;
use tokio::sync::broadcast;
use tokio::sync::watch;
use tokio::task;
use tokio_stream::StreamExt;
use tracing::error;
use types::ProxyAddrConfig;
use url::Url;

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    let (_file_guard, _stdout_guard, log_layers) = setup_logging(
        cli.log_file, cli.log_stdout, cli.log_level
    ).unwrap();

    let mut meter_provider: Option<SdkMeterProvider> = None;
    let mut tracer_provider: Option<TracerProvider> = None;
    
    if cli.with_otel {
        meter_provider = Some(init_meter_provider());
        tracer_provider = Some(init_tracer_provider());
    }

    let _ = init_subscriber(log_layers, &tracer_provider, &meter_provider);

    let (shutdown_tx, shutdown_rx) = broadcast::channel::<()>(1); // Capacity of 1

    let (task_manager, receiver) = TaskManager::new(1000);

    match &cli.command {
        Commands::Run { options } => {
            let _progress_guard =
                task::spawn(handle_displayable_events(receiver));

            let proxy_nic_config = get_proxy_address(&options.common);

            let app_state = initialize_proxy(
                &options.common,
                &proxy_nic_config,
                shutdown_rx,
                task_manager.clone(),
            )
            .await;

            let cmd_config: ProxyConfig = options.into();

            if app_state.config_tx.send(cmd_config).is_err() {
                error!("Proxy configuration listener has been shut down.");
            }

            proxy_prelude(app_state.proxy_address);

            tokio::signal::ctrl_c().await.map_err(|e| {
                ProxyError::Internal(format!(
                    "Failed to listen for shutdown signal: {}",
                    e
                ))
            }).unwrap();

            tracing::info!("Shutdown signal received. Initiating shutdown.");
        }
        Commands::Demo(demo_cmd) => match demo_cmd {
            DemoCommands::Run(demo_config) => {
                demo_prelude(format!(
                    "{}:{}",
                    demo_config.address, demo_config.port
                ));

                let _ = demo::run((*demo_config).clone()).await;
            }
        },
        Commands::Scenario { scenario, common } => match scenario {
            ScenarioCommands::Run(config) => {
                let start = Instant::now();

                let proxy_nic_config = get_proxy_address(common);

                let m = MultiProgress::new();

                let app_state = initialize_proxy(
                    common,
                    &proxy_nic_config,
                    shutdown_rx,
                    task_manager.clone(),
                )
                .await;

                let mut scenarios = load_scenarios(Path::new(&config.scenario));

                println!(
                    "\n{}\n",
                    "================ Running Scenarios ================"
                        .dimmed()
                );

                let queue =
                    Arc::new(Mutex::new(Vec::<ScenarioItemLifecycle>::new()));

                let (event_manager, scenario_event_receiver) =
                    ScenarioEventManager::new(500);

                let _scenario_event_progress_guard =
                    tokio::spawn(handle_scenario_events(
                        scenario_event_receiver,
                        receiver,
                        queue.clone(),
                    ));

                let mut results = Vec::new();

                while let Some(candidate) = scenarios.next().await {
                    match candidate {
                        Ok(scenario) => {
                            let mut progress_state = String::new();

                            let title = scenario.clone().title;

                            let n = count_scenario_items(&scenario); //scenario.scenarios.len() as u64;

                            let pb = m.add(ProgressBar::new(n));
                            pb.enable_steady_tick(Duration::from_millis(80));
                            pb.set_style(
                                ProgressStyle::with_template(
                                    "{spinner:.green} {pos:>2}/{len:2} {msg}",
                                )
                                .unwrap()
                                .tick_strings(
                                    &[
                                        "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧",
                                        "⠇", "⠏",
                                    ],
                                ),
                            );
                            pb.set_message(title.clone());

                            let key = title.clone();
                            let msg = format!("{} ", key.clone());

                            for item in scenario.scenarios.into_iter() {
                                let items = build_item_list(item);

                                for i in items {
                                    let report = execute_item(
                                        i,
                                        app_state.clone(),
                                        event_manager.clone(),
                                    )
                                    .await;

                                    let mut events = queue.lock().unwrap();
                                    let event = events.pop();

                                    let metrics = match event {
                                        Some(e) => {
                                            match report.metrics.clone() {
                                                Some(m) => {
                                                    Some(ReportItemMetrics {
                                                        dns: e.dns_timing,
                                                        protocol: m.protocol,
                                                        ttfb: m.ttfb,
                                                        total_time: m
                                                            .total_time,
                                                        faults: map_faults(
                                                            &e.faults,
                                                        ),
                                                    })
                                                }
                                                None => None,
                                            }
                                        }
                                        None => None,
                                    };

                                    match &report.expect {
                                        Some(expect) => {
                                            match expect {
                                                ReportItemExpectation::Http { wanted: _, got } => {
                                                    match got {
                                                        Some(status) => {
                                                            if status.decision == ReportItemExpectationDecision::Failure {
                                                                progress_state = format!("{}{}", progress_state, "▮".to_string().red());
                                                            } else if status.decision == ReportItemExpectationDecision::Success {
                                                                progress_state = format!("{}{}", progress_state, "▮".to_string().green());
                                                            } else {
                                                                progress_state = format!("{}{}", progress_state, "▮".to_string().grey0());
                                                            }
                                                        },
                                                        None => progress_state = format!("{}{}", progress_state, "▮".to_string().grey0())
                                                    }
                                                }
                                            }
                                        }
                                        None => progress_state = format!("{} {}", progress_state, "▮".to_string().grey0())
                                    }

                                    results.push(ReportItem::new(title.clone(), metrics, report));

                                    pb.inc(1);
                                    pb.set_message(format!(
                                        "{} {}",
                                        msg.clone(),
                                        progress_state
                                    ));
                                }
                            }

                            pb.finish();
                        }
                        Err(e) => error!("Failed to load scenario: {:?}", e),
                    }
                }

                let final_report =
                    Report { plugins: Vec::new(), items: results };

                final_report.save("results.json").unwrap();

                let report_output = build_report_output(&final_report).unwrap();

                println!("\n");
                println!(
                    "{}\n",
                    "===================== Summary ====================="
                        .dimmed()
                );

                println!(
                    "Tests run: {}, Tests failed: {}",
                    report_output.summary.total_tests.to_string().bright_cyan(),
                    report_output
                        .summary
                        .total_failures
                        .to_string()
                        .bright_red()
                );
                println!("Total time: {:.1}s", start.elapsed().as_secs_f64());

                match get_output_format_result(config.report.as_str()) {
                    Ok(fmt) => match pretty_report(&report_output, &fmt) {
                        Ok(computed_report) => {
                            let path = &config.report;
                            let mut file = File::create(path).unwrap();
                            let _ = write!(file, "{}", computed_report);
                            println!(
                                "\nReport saved as {}",
                                config.report.bright_yellow()
                            );
                        }
                        Err(e) => {
                            tracing::error!("Failed to generated report: {}", e)
                        }
                    },
                    Err(_) => tracing::error!("Unsupported report format"),
                }
            }
        },
    }

    match shutdown_tx.send(()) {
        Ok(_) => tracing::debug!("Shutdown notified."),
        Err(e) => tracing::warn!("Failed to notify shutdown {}", e),
    }

    drop(task_manager);

    shutdown_tracer(tracer_provider, meter_provider);

    Ok(())
}

fn map_faults(
    original_faults: &HashMap<usize, ScenarioItemLifecycleFaults>,
) -> Vec<ReportItemMetricsFaults> {
    original_faults
        .iter()
        .map(|(_key, value)| value.to_report_metrics_faults())
        .collect()
}

#[derive(Debug, Clone)]
struct AppState {
    pub proxy_state: Arc<ProxyState>,
    pub config_tx: watch::Sender<ProxyConfig>,
    pub proxy_address: String,
}

#[cfg(all(target_os = "linux", feature = "stealth"))]
fn is_stealth(cli: &ProxyAwareCommandCommon) -> bool {
    cli.ebpf
}

#[cfg(all(not(target_os = "linux"), feature = "stealth"))]
fn is_stealth(cli: &ProxyAwareCommandCommon) -> bool {
    false
}

#[cfg(all(target_os = "linux", not(feature = "stealth")))]
fn is_stealth(cli: &ProxyAwareCommandCommon) -> bool {
    false
}

#[cfg(not(target_os = "linux"))]
fn is_stealth(cli: &ProxyAwareCommandCommon) -> bool {
    false
}

async fn initialize_proxy(
    cli: &ProxyAwareCommandCommon,
    proxy_nic_config: &ProxyAddrConfig,
    shutdown_rx: broadcast::Receiver<()>,
    task_manager: Arc<TaskManager>,
) -> AppState {
    let stealth_mode = is_stealth(&cli);

    // Initialize shared state with empty configuration
    let state = Arc::new(ProxyState::new(stealth_mode));

    // Create a watch channel for configuration updates
    let (config_tx, config_rx) = watch::channel(ProxyConfig::default());

    // Create a oneshot channel for readiness signaling
    let (readiness_tx, readiness_rx) = oneshot::channel::<()>();

    let upstream_hosts = cli.upstream_hosts.clone();
    let upstreams: Vec<String> =
        upstream_hosts.iter().map(|h| upstream_to_addr(h).unwrap()).collect();

    let proxy_state = state.clone();
    let proxy_address = proxy_nic_config.proxy_address();

    //let rpc_plugin = load_remote_plugins(cli.grpc_plugins.clone()).await;
    //state.update_plugins(vec![rpc_plugin]).await;

    state.update_upstream_hosts(upstreams).await;

    tokio::spawn(run_proxy(
        proxy_address.clone(),
        proxy_state,
        shutdown_rx,
        readiness_tx,
        config_rx,
        task_manager,
    ));

    // Wait for the proxy to signal readiness
    let _ = readiness_rx.await.map_err(|e| {
        ProxyError::Internal(format!(
            "Failed to receive readiness signal: {}",
            e
        ))
    });

    tracing::info!("Proxy server is listening on {}", proxy_address);

    AppState { proxy_address, proxy_state: state, config_tx }
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

fn proxy_prelude(proxy_address: String) {
    let g = "lueur".gradient(Color::LightYellow3);
    let r = "Your Resiliency Exploration Tool".gradient(Color::Purple3);
    let a = format!("http://{}", proxy_address).cyan();
    println!(
        "
    Welcome to {} — {}!

    To get started, route your HTTP/HTTPS requests through:
    {}

    As you send requests, lueur will simulate network conditions
    so you can see how your application copes.

    Ready when you are — go ahead and make some requests!
        ",
        g, r, a
    );
}

fn demo_prelude(demo_address: String) {
    let g = "lueur".gradient(Color::Plum4);
    println!(
        "
    Welcome to {}, this demo application is here to let you explore lueur's capabilities.

    Here are a few examples:

    export HTTP_PROXY=http://localhost:8080
    export HTTPS_PROXY=http://localhost:8080

    curl -x ${{HTTP_PROXY}} http://{demo_address}/
    curl -x ${{HTTP_PROXY}} http://{demo_address}/ping
    curl -x ${{HTTP_PROXY}} http://{demo_address}/ping/myself
    curl -x ${{HTTP_PROXY}} --json '{{\"content\": \"hello\"}}' http://{demo_address}/uppercase

        ", g,
    );
}

#[cfg(all(target_os = "linux", feature = "stealth_auto_build"))]
fn initialize_stealth(
    cli: &ProxyAwareCommandCommon,
    proxy_nic_config: ProxyAddrConfig,
) -> Option<Ebpf> {
    let upstream_hosts = cli.upstream_hosts.clone();

    #[allow(unused_variables)]
    let ebpf_guard = match cli.ebpf {
        true => {
            let cargo_bin_dir = get_cargo_bin_dir();
            if cargo_bin_dir.is_none() {
                tracing::warn!(
                    "No cargo bin directory could be detected, please set CARGO_HOME"
                );
                return None;
            }
            let bin_dir = cargo_bin_dir.unwrap();
            let mut bpf = aya::Ebpf::load(aya::include_bytes_aligned!(
                concat!(bin_dir.to_string(), "/lueur-ebpf")
            ))
            .unwrap();

            if let Err(e) = aya_log::EbpfLogger::init(&mut bpf) {
                tracing::warn!("failed to initialize eBPF logger: {}", e);
            }

            let _ = ebpf::install_and_run(
                &mut bpf,
                &proxy_nic_config,
                upstream_hosts.clone(),
            );

            tracing::info!("Ebpf has been loaded");

            Some(bpf)
        }
        false => None,
    };

    ebpf_guard
}

#[cfg(all(target_os = "linux", feature = "stealth_auto_build"))]
fn get_cargo_bin_dir() -> Option<PathBuf> {
    // Try to read CARGO_HOME first.
    if let Ok(cargo_home) = env::var("CARGO_HOME") {
        let mut path = PathBuf::from(cargo_home);
        path.push("bin");
        return Some(path);
    }
    // Fallback for Unix-like systems: use HOME/.cargo/bin
    #[cfg(unix)]
    {
        if let Ok(home) = env::var("HOME") {
            let mut path = PathBuf::from(home);
            path.push(".cargo/bin");
            return Some(path);
        }
    }
    None
}


fn get_output_format_result(file_path: &str) -> Result<OutputFormat, String> {
    Path::new(file_path)
        .extension()
        .and_then(|ext| ext.to_str())
        .ok_or_else(|| "File extension is missing or invalid.".to_string())
        .and_then(|ext_str| match ext_str.to_lowercase().as_str() {
            "md" | "markdown" => Ok(OutputFormat::Markdown),
            "txt" => Ok(OutputFormat::Text),
            "html" | "htm" => Ok(OutputFormat::Html),
            "json" => Ok(OutputFormat::Json),
            "yaml" | "yml" => Ok(OutputFormat::Yaml),
            other => Err(format!("Unrecognized file extension: '{}'", other)),
        })
}

#[cfg(all(target_os = "linux", feature = "stealth"))]
fn get_proxy_address(common: &ProxyAwareCommandCommon) -> ProxyAddrConfig {
    let proxy_address = common.proxy_address.clone();

    nic::determine_proxy_and_ebpf_config(
        proxy_address,
        common.iface.clone(),
    )
    .unwrap()
}

#[cfg(all(target_os = "linux", not(feature = "stealth")))]
fn get_proxy_address(common: &ProxyAwareCommandCommon) -> ProxyAddrConfig {
    let proxy_address = common.proxy_address.clone();

    let addr = proxy_address.unwrap();
    let socket_addr: SocketAddr = addr.parse().map_err(|e| {
        format!("Invalid proxy address '{}': {}", addr, e)
    }).unwrap();
    let sock_proxy_ip = socket_addr.ip();
    let proxy_port = socket_addr.port();

    let proxy_ip = match sock_proxy_ip {
        IpAddr::V4(ipv4) => ipv4,
        IpAddr::V6(_ipv6) => {
            panic!("IPV6 addresses are not supported for proxy");
        }
    };

    ProxyAddrConfig {
        proxy_ip: proxy_ip,
        proxy_port: proxy_port,
        proxy_ifindex: 0,
        ebpf_ifindex: 0,
        ebpf_ifname: "".to_string(),
    }
}

#[cfg(all(feature = "stealth", not(target_os = "linux")))]
fn get_proxy_address(common: &ProxyAwareCommandCommon) -> ProxyAddrConfig {
    let proxy_address = common.proxy_address.clone();

    let addr = proxy_address.unwrap();
    let socket_addr: SocketAddr = addr.parse().map_err(|e| {
        format!("Invalid proxy address '{}': {}", addr, e)
    }).unwrap();
    let sock_proxy_ip = socket_addr.ip();
    let proxy_port = socket_addr.port();

    let proxy_ip = match sock_proxy_ip {
        IpAddr::V4(ipv4) => ipv4,
        IpAddr::V6(_ipv6) => {
            panic!("IPV6 addresses are not supported for proxy");
        }
    };

    ProxyAddrConfig {
        proxy_ip: proxy_ip,
        proxy_port: proxy_port,
        proxy_ifindex: 0,
        ebpf_ifindex: 0,
        ebpf_ifname: "".to_string(),
    }
}


#[cfg(all(not(feature = "stealth"), not(target_os = "linux")))]
fn get_proxy_address(common: &ProxyAwareCommandCommon) -> ProxyAddrConfig {
    let proxy_address = common.proxy_address.clone();

    let addr = proxy_address.unwrap();
    let socket_addr: SocketAddr = addr.parse().map_err(|e| {
        format!("Invalid proxy address '{}': {}", addr, e)
    }).unwrap();
    let sock_proxy_ip = socket_addr.ip();
    let proxy_port = socket_addr.port();

    let proxy_ip = match sock_proxy_ip {
        IpAddr::V4(ipv4) => ipv4,
        IpAddr::V6(_ipv6) => {
            panic!("IPV6 addresses are not supported for proxy");
        }
    };

    ProxyAddrConfig {
        proxy_ip: proxy_ip,
        proxy_port: proxy_port,
        proxy_ifindex: 0,
        ebpf_ifindex: 0,
        ebpf_ifname: "".to_string(),
    }
}

