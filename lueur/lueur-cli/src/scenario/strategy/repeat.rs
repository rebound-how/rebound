use std::sync::Arc;
use std::time::Duration;
use std::time::Instant;

use anyhow::Result;
use chrono::Utc;
use tokio::sync::watch;
use uuid::Uuid;

use crate::config::ProxyConfig;
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
use crate::types::FaultConfiguration;

pub async fn execute(
    proxy_address: String,
    item: ScenarioItem,
    global_config: Option<ScenarioGlobalConfig>,
    event: Arc<ScenarioEvent>,
    config_tx: watch::Sender<(ProxyConfig, Vec<Box<dyn FaultInjector>>)>,
    addr_id_map: Arc<scc::HashMap<String, Uuid>>,
    id_events_map: Arc<scc::HashMap<Uuid, ScenarioItemLifecycle>>,
    step: f64,
    failfast: bool,
    count: usize,
    add_baseline_call: bool,
    wait: Option<f64>,
) -> Result<ItemResult> {
    let cloned_item = item.clone();
    let url = cloned_item.call.url.clone();

    let mut total_count = count;
    if add_baseline_call {
        total_count += 1;
    }

    let mut failure_counts = 0;
    let start_instant = Instant::now();

    let mut data = Vec::new();

    for i in 0..total_count {
        let _ = event.on_item_started(url.clone(), cloned_item.clone());

        // increase faults with the step amount, where it makes sense
        let item = adjust_to_next_step(cloned_item.clone(), step, i);

        tracing::debug!("Item iteration {} updated to {:?}", i, item);

        // with this strategy, we must warn the proxy we have a new config
        set_proxy_config_from_item(&item, config_tx.clone()).await;

        let start = Utc::now();

        let res = execute_request(
            item.call.clone(),
            global_config.clone(),
            proxy_address.clone(),
            addr_id_map.clone(),
            id_events_map.clone(),
        )
        .await;

        let mut metrics = None;
        let mut expect = None;
        let mut errors = Vec::new();

        match res {
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
                            Some(ItemProtocol::Http {
                                code,
                                body_length: _,
                            }) => {
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
        }

        data.push(ItemResultData {
            start,
            expect: expect.clone(),
            metrics: metrics,
            faults: item.context.faults.clone(),
            errors,
        });

        let _ = event.on_item_terminated(&item, expect);

        if let Some(w) = wait {
            tokio::time::sleep(Duration::from_millis(w as u64)).await;
        }
    }

    Ok(ItemResult {
        target: ItemTarget { address: url },
        results: data,
        requests_count: total_count,
        failure_counts,
        total_time: start_instant.elapsed(),
    })
}

fn adjust_to_next_step(
    item: ScenarioItem,
    step: f64,
    iteration: usize,
) -> ScenarioItem {
    let mut next_item = item.clone();
    let mut next_faults = Vec::new();

    for fault in item.context.faults {
        next_faults.push(match fault {
            FaultConfiguration::Latency {
                distribution,
                global,
                side,
                mean,
                stddev,
                min,
                max,
                shape,
                scale,
                direction,
                period,
            } => FaultConfiguration::Latency {
                distribution,
                global,
                side,
                mean: Some(mean.unwrap() + (step * iteration as f64)),
                stddev,
                min,
                max,
                shape,
                scale,
                direction,
                period,
            },
            FaultConfiguration::PacketLoss { direction, side, period } => {
                FaultConfiguration::PacketLoss { direction, side, period }
            }
            FaultConfiguration::Bandwidth {
                rate,
                unit,
                direction,
                side,
                period,
            } => FaultConfiguration::Bandwidth {
                rate,
                unit,
                direction,
                side,
                period,
            },
            FaultConfiguration::Jitter {
                amplitude: jitter_amplitude,
                frequency: jitter_frequency,
                direction,
                side,
                period,
            } => FaultConfiguration::Jitter {
                amplitude: jitter_amplitude,
                frequency: jitter_frequency,
                direction,
                period,
                side,
            },
            FaultConfiguration::Dns { period, rate: dns_rate } => {
                FaultConfiguration::Dns { rate: dns_rate, period }
            }
            FaultConfiguration::HttpError {
                status_code,
                body,
                probability,
                period,
            } => FaultConfiguration::HttpError {
                status_code,
                body,
                probability,
                period,
            },
            FaultConfiguration::Blackhole { direction, side, period } => {
                FaultConfiguration::Blackhole { direction, side, period }
            }
        })
    }

    next_item.context.faults = next_faults;

    next_item
}
