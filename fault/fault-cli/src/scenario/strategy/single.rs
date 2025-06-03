use std::sync::Arc;
use std::time::Instant;

use anyhow::Result;
use chrono::Utc;
use kanal::AsyncReceiver;
use tokio::sync::watch;
use uuid::Uuid;

use crate::config::ProxyConfig;
use crate::event::TaskProgressEvent;
use crate::fault::FaultInjector;
use crate::scenario::event::ScenarioEvent;
use crate::scenario::event::ScenarioItemLifecycle;
use crate::scenario::executor::http::execute_request;
use crate::scenario::executor::set_proxy_config_from_item;
use crate::scenario::types::ItemExpectation;
use crate::scenario::types::ItemExpectationDecision;
use crate::scenario::types::ItemHttpExpectation;
use crate::scenario::types::ItemHttpResult;
use crate::scenario::types::ItemProtocol;
use crate::scenario::types::ItemResult;
use crate::scenario::types::ItemResultData;
use crate::scenario::types::ItemTarget;
use crate::scenario::types::ScenarioGlobalConfig;
use crate::scenario::types::ScenarioItem;

pub async fn execute(
    proxy_address: String,
    item: ScenarioItem,
    global_config: Option<ScenarioGlobalConfig>,
    config_tx: watch::Sender<(ProxyConfig, Vec<Box<dyn FaultInjector>>)>,
    addr_id_map: Arc<scc::HashMap<String, Uuid>>,
    id_events_map: Arc<scc::HashMap<Uuid, ScenarioItemLifecycle>>,
    event: Arc<ScenarioEvent>,
) -> Result<ItemResult> {
    let mut metrics = None;
    let mut expect = None;
    let mut errors = Vec::new();
    let mut failure_counts = 0;

    set_proxy_config_from_item(&item, config_tx.clone()).await;

    let url = item.call.url.clone();
    let _ = event.on_item_started(url.clone(), item.clone());

    let start_instant = Instant::now();
    let start = Utc::now();

    match execute_request(
        item.call.clone(),
        global_config.clone(),
        proxy_address.clone(),
        addr_id_map.clone(),
        id_events_map.clone(),
    )
    .await
    {
        Ok(m) => {
            metrics = Some(m.clone());
            match item.expect.clone() {
                Some(r) => {
                    let mut met = None;

                    let mut result = ItemHttpResult {
                        status_code: None,
                        response_time: None,
                        all_slo_are_valid: None,
                        decision: ItemExpectationDecision::Unknown,
                    };

                    match m.protocol {
                        Some(ItemProtocol::Http { code, body_length: _ }) => {
                            met = match r.status {
                                Some(v) => {
                                    result.status_code = Some(code);
                                    Some(v == code)
                                }
                                None => met,
                            };
                        }
                        None => {}
                    };

                    if met.is_none() || met == Some(true) {
                        met = match r.response_time_under {
                            Some(v) => {
                                result.response_time = Some(m.total_time);
                                Some(m.total_time <= v)
                            }
                            None => met,
                        };
                    }

                    if met == Some(true) {
                        result.decision = ItemExpectationDecision::Success;
                    } else {
                        result.decision = ItemExpectationDecision::Failure;
                        failure_counts = failure_counts + 1;
                    }

                    expect = Some(ItemExpectation::Http {
                        wanted: ItemHttpExpectation {
                            status_code: r.status,
                            response_time_under: r.response_time_under,
                            all_slo_are_valid: None,
                        },
                        got: Some(result),
                    });

                    met
                }
                None => None,
            };
        }
        Err(e) => errors.push(e),
    };

    let mut data = Vec::new();
    data.push(ItemResultData {
        expect: expect.clone(),
        faults: item.context.faults.clone(),
        metrics,
        errors,
        start,
    });

    let result = ItemResult {
        target: ItemTarget { address: item.call.url.clone() },
        results: data,
        requests_count: 1,
        failure_counts,
        total_time: start_instant.elapsed(),

        #[cfg(feature = "discovery")]
        resources: None,
    };

    let _ = event.on_item_terminated(&item, expect);

    Ok(result)
}
