use super::types::ItemStatus;
use super::types::ItemSummary;
use super::types::LatencyPercentile;
use super::types::Report;
use super::types::RunOverview;
use super::types::ScenarioSummary;
use super::types::SloImpactRow;
use crate::scenario::types::ItemResult;
use crate::scenario::types::Scenario;
use crate::scenario::types::ScenarioItem;
use crate::scenario::types::ScenarioItemCallStrategy;
use crate::scenario::types::ScenariosResults;

pub fn to_report(exec_results: &ScenariosResults) -> Report {
    let mut scenario_summaries = Vec::new();

    for scenario_result in &exec_results.results {
        let scenario_start_time = exec_results.start; // or scenario_result could store its start
        let item_count = count_items_per_scenario(&scenario_result.scenario);
        let mut item_summaries = Vec::new();

        let mut scenario_total_time = 0.0_f64;

        // For each item in the scenario, we find the corresponding `ItemResult`
        // in scenario_result.results and produce an `ItemSummary`.
        for (idx, item) in scenario_result.scenario.items.iter().enumerate() {
            let item_result = &scenario_result.results[idx];

            let sum = build_item_summary(item, item_result);
            scenario_total_time += sum
                .run_overview
                .iter()
                .map(|r| r.total_time)
                .fold(0.0, f64::max); // or sum, depends on your logic

            item_summaries.push(sum);
        }

        let scenario_summary = ScenarioSummary {
            title: scenario_result.scenario.title.clone(),
            description: scenario_result
                .scenario
                .description
                .clone()
                .unwrap_or_default(),
            scenario_start_time,
            item_count,
            total_duration_ms: scenario_total_time,
            item_summaries,
        };

        scenario_summaries.push(scenario_summary);
    }

    Report {
        start_time: exec_results.start,
        end_time: Some(chrono::Utc::now()), // or track from your run code
        scenario_summaries,
    }
}

pub fn build_item_summary(
    item: &ScenarioItem,
    result: &ItemResult,
) -> ItemSummary {
    let (_, url) = (item.call.method.clone(), item.call.url.clone());

    let strategy_mode = match item.context.strategy.clone() {
        Some(s) => s,
        None => ScenarioItemCallStrategy::Single {},
    };

    let mut run_overview = Vec::new();
    let mut failure_count = 0;
    let mut error_count = 0;
    let final_status;

    let mut min_latency = 0.0;
    let mut max_latency = 0.0;
    let mut p50_latency = LatencyPercentile::new(0.0, 0.0, 0);
    let mut latency_percentiles = Vec::new();

    let mut latencies = result.latencies();
    latencies.sort_by(|a, b| a.partial_cmp(b).unwrap());

    if !latencies.is_empty() {
        let latencies = latencies.clone();
        min_latency = latencies[0];
        max_latency = latencies[latencies.len() - 1];
        let percentiles = result.latency_percentiles(latencies);

        p50_latency = percentiles[1];

        latency_percentiles.push(percentiles[0]);
        latency_percentiles.push(p50_latency.clone());
        latency_percentiles.push(percentiles[2]);
        latency_percentiles.push(percentiles[3]);
        latency_percentiles.push(percentiles[4]);
    }

    let overview = RunOverview {
        iteration: None,
        requests_count: result.requests_count,
        latency_percentiles,
        min_latency,
        max_latency,
        failure_count: result.failure_counts,
        error_count: result
            .results
            .iter()
            .map(|i| {
                i.metrics
                    .iter()
                    .map(|m| if m.errored { 1usize } else { 0usize })
                    .sum::<usize>()
            })
            .sum(),
        total_time: result.total_time.as_millis_f64(),
    };
    error_count = overview.error_count;
    run_overview.push(overview);

    failure_count = result.failure_counts;
    final_status = if result.failure_counts == 0 {
        ItemStatus::Pass
    } else {
        ItemStatus::Fail
    };

    // Build the SLO impact table (slo_impact_table).
    let mut slo_impact_table = Vec::new();
    if let Some(slos) = &item.context.slo {
        for user_slo in slos {
            if user_slo.slo_type == "latency" {
                let p_lat =
                    result.latency_percentile(user_slo.objective, &latencies);
                let buffer = user_slo.threshold - p_lat.latency;
                let pass = buffer >= 0.0;
                let margin_text = if pass {
                    format!("Below by {:.1}ms", buffer)
                } else {
                    format!("Above by {:.1}ms", -buffer)
                };
                let over_threshold = result
                    .results
                    .iter()
                    .filter_map(|item| {
                        item.metrics
                            .as_ref()
                            .filter(|m| m.total_time > user_slo.threshold)
                    })
                    .count();

                let row = SloImpactRow {
                    title: user_slo.title.clone(),
                    pass,
                    margin_text,
                    calls_over_threshold: over_threshold,
                    calls_over_threshold_percent: (over_threshold * 100) as f64
                        / result.requests_count as f64,
                    objective: user_slo.objective,
                    threshold: user_slo.threshold,
                    unit: "ms".to_string(),
                };
                slo_impact_table.push(row);
            }
            if user_slo.slo_type == "error" {
                let percent_errored =
                    (error_count * 100) as f64 / result.requests_count as f64;
                let pass = percent_errored < user_slo.threshold;
                let buffer = user_slo.threshold - percent_errored;
                let margin_text = if pass {
                    format!("Below by {:.1}", buffer)
                } else {
                    format!("Above by {:.1}", -buffer)
                };
                let over_threshold = result
                    .results
                    .iter()
                    .map(|i| {
                        i.metrics
                            .iter()
                            .map(|m| if m.errored { 1usize } else { 0usize })
                            .sum::<usize>()
                    })
                    .sum();

                let row = SloImpactRow {
                    title: user_slo.title.clone(),
                    pass,
                    margin_text,
                    calls_over_threshold: over_threshold,
                    calls_over_threshold_percent: (over_threshold * 100) as f64
                        / result.requests_count as f64,
                    objective: user_slo.objective,
                    threshold: user_slo.threshold,
                    unit: "%".to_string(),
                };
                slo_impact_table.push(row);
            }
        }
    }

    // Step 5: Return
    ItemSummary {
        url,
        call: item.call.clone(),
        faults: item.context.faults.clone(),
        expectation: item.expect.clone(),
        meta: item.call.meta.clone(),
        strategy_mode,
        run_overview,
        slo_impact_table,
        failure_count,
        error_count,
        final_status,
    }
}

fn count_items_per_scenario(scenario: &Scenario) -> usize {
    scenario
        .items
        .iter()
        .map(|i| match i.context.strategy.clone() {
            Some(s) => match s {
                ScenarioItemCallStrategy::Repeat {
                    count,
                    add_baseline_call,
                    ..
                } => {
                    let mut total = count;
                    if add_baseline_call.is_some_and(|x| x) {
                        total += 1;
                    }
                    total
                }
                ScenarioItemCallStrategy::Load { .. } => 1,
                ScenarioItemCallStrategy::Single { .. } => 1,
            },
            None => 1,
        })
        .sum::<usize>()
}
