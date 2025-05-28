use std::sync::Arc;
use std::time::Duration;
use std::time::Instant;

use anyhow::Result;
use chrono::Utc;
use kanal::AsyncReceiver;
use tokio::time::interval;
use uuid::Uuid;

use crate::event::TaskProgressEvent;
use crate::proxy::ProxyState;
use crate::report;
use crate::scenario::event::ScenarioEvent;
use crate::scenario::event::ScenarioItemLifecycle;
use crate::scenario::executor::http::execute_request;
use crate::scenario::executor::update_proxy_from_fault_schedule;
use crate::scenario::types::ItemExpectation;
use crate::scenario::types::ItemExpectationDecision;
use crate::scenario::types::ItemHttpExpectation;
use crate::scenario::types::ItemHttpResult;
use crate::scenario::types::ItemResult;
use crate::scenario::types::ItemResultData;
use crate::scenario::types::ItemTarget;
use crate::scenario::types::ScenarioGlobalConfig;
use crate::scenario::types::ScenarioItem;

pub async fn execute(
    proxy_address: String,
    item: ScenarioItem,
    global_config: Option<ScenarioGlobalConfig>,
    event: Arc<ScenarioEvent>,
    proxy_state: Arc<ProxyState>,
    addr_id_map: Arc<scc::HashMap<String, Uuid>>,
    id_events_map: Arc<scc::HashMap<Uuid, ScenarioItemLifecycle>>,
    duration: Duration,
    clients: usize,
    rps: usize,
) -> Result<ItemResult> {
    run_load_test(
        proxy_address,
        item,
        global_config,
        event,
        proxy_state,
        addr_id_map,
        id_events_map,
        duration,
        clients,
        rps,
    )
    .await
}

// This isn't a very capable load test machine.
// If you want something fancier, you should! :)
// But convenience sometimes beat raw capabilities.
pub async fn run_load_test(
    proxy_address: String,
    item: ScenarioItem,
    global_config: Option<ScenarioGlobalConfig>,
    event: Arc<ScenarioEvent>,
    proxy_state: Arc<ProxyState>,
    addr_id_map: Arc<scc::HashMap<String, Uuid>>,
    id_events_map: Arc<scc::HashMap<Uuid, ScenarioItemLifecycle>>,
    duration: Duration,
    clients: usize,
    rps: usize,
) -> Result<ItemResult> {
    tracing::debug!("Running load test for {:?}", duration);
    let cloned_item = item.clone();
    let url = cloned_item.call.url.clone();
    let _ = event.on_item_started(url.clone(), cloned_item.clone());

    // Each client will push its measured latencies (in ms) into its own vector.
    let mut tasks = Vec::new();
    let failure_counts = 0;

    let start_instant = Instant::now();

    tokio::spawn(update_proxy_from_fault_schedule(
        item.clone(),
        tokio::time::Instant::now(),
        duration,
        proxy_state,
    ));

    tokio::time::sleep(Duration::from_millis(100)).await;

    for _ in 0..clients {
        let cloned_item = cloned_item.clone();
        let proxy_address = proxy_address.clone();
        let global_config = global_config.clone();
        let addr_id_map = addr_id_map.clone();
        let id_events_map = id_events_map.clone();

        let task = tokio::spawn(async move {
            let mut data = Vec::new();
            // Create an interval that ticks at a rate of rps times per second.
            let period = Duration::from_secs_f64(1.0 / rps as f64);
            let mut ticker = interval(period);

            let start = Instant::now();
            while Instant::now().duration_since(start) < duration {
                let item = cloned_item.clone();

                ticker.tick().await;

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
                let mut errors = Vec::new();

                match res {
                    Ok(m) => {
                        metrics = Some(m.clone());
                    }
                    Err(e) => errors.push(e),
                }

                data.push(ItemResultData {
                    start,
                    expect: None,
                    metrics: metrics,
                    faults: item.context.faults.clone(),
                    errors,
                });
            }
            data
        });
        tasks.push(task);
    }

    // Wait for all clients to complete their task
    let mut all_data = Vec::new();
    for task in tasks {
        if let Ok(data) = task.await {
            all_data.extend(data);
        }
    }

    let total_requests = all_data.len();

    all_data.sort_by_key(|item| item.start);

    let item_result = ItemResult {
        target: ItemTarget { address: url },
        results: all_data,
        requests_count: total_requests,
        failure_counts,
        total_time: start_instant.elapsed(),
    };

    if let Some(expect) = item.expect.clone() {
        if let Some(needs_all_valid) = expect.all_slo_are_valid {
            let summary =
                report::builder::build_item_summary(&item, &item_result);

            let mut all_valid = None;
            let mut decision = ItemExpectationDecision::Unknown;

            if needs_all_valid
                && summary.final_status == report::types::ItemStatus::Pass
            {
                all_valid = Some(true);
                decision = ItemExpectationDecision::Success;
            } else if (needs_all_valid == false)
                && (summary.final_status == report::types::ItemStatus::Pass)
            {
                all_valid = Some(true);
                decision = ItemExpectationDecision::Failure;
            } else if (needs_all_valid == true)
                && (summary.final_status == report::types::ItemStatus::Fail)
            {
                all_valid = Some(false);
                decision = ItemExpectationDecision::Failure;
            } else if (needs_all_valid == false)
                && (summary.final_status == report::types::ItemStatus::Fail)
            {
                all_valid = Some(false);
                decision = ItemExpectationDecision::Success;
            } else if (needs_all_valid == false)
                && (summary.final_status == report::types::ItemStatus::Unknown)
            {
                all_valid = None;
                decision = ItemExpectationDecision::Unknown;
            }

            let expectation = ItemExpectation::Http {
                wanted: ItemHttpExpectation {
                    status_code: expect.status,
                    response_time_under: expect.response_time_under,
                    all_slo_are_valid: expect.all_slo_are_valid,
                },
                got: Some(ItemHttpResult {
                    status_code: expect.status,
                    response_time: expect.response_time_under,
                    all_slo_are_valid: all_valid,
                    decision,
                }),
            };

            let _ = event.on_item_terminated(&item, Some(expectation));
        } else {
            let _ = event.on_item_terminated(&item, None);
        }
    } else {
        let _ = event.on_item_terminated(&item, None);
    }

    Ok(item_result)
}
