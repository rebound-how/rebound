use chrono::Duration;
use chrono_humanize::Accuracy;
use chrono_humanize::HumanTime;

use crate::report::types::Report;
use crate::scenario::types::ScenarioItemCallStrategy;
use crate::types::Direction;
use crate::types::FaultConfiguration;
use crate::types::StreamSide;

pub fn render(report: &Report) -> String {
    let mut md = String::new();

    md.push_str(&format!("# Scenarios Report\n\n"));
    md.push_str(&format!("Start: {}\n\n", report.start_time));
    if let Some(end) = &report.end_time {
        md.push_str(&format!("End: {}\n\n", end));
    } else {
        md.push_str("\n");
    }

    for scenario_summary in &report.scenario_summaries {
        md.push_str(&format!(
            "## Scenario: {}  (items: {})\n\n",
            scenario_summary.title, scenario_summary.item_count
        ));

        if !scenario_summary.description.is_empty() {
            md.push_str(&format!(
                "_Description:_ {}\n\n",
                scenario_summary.description
            ));
        }

        // Then each item
        for item in &scenario_summary.item_summaries {
            md.push_str(&format!(
                "### 🎯 `{}` {} | {}\n\n",
                item.call.method.clone(),
                item.url,
                item.final_status
            ));

            md.push_str("**Call**:\n\n");

            let r = item.call.clone();
            if let Some(meta) = &item.call.meta {
                if let Some(op) = &meta.operation_id {
                    md.push_str(&format!("- Operation ID: `{}`\n", op));
                }
            }
            md.push_str(&format!("- Method: `{}`\n", r.method));
            md.push_str(&format!(
                "- Timeout: {}\n",
                match r.timeout {
                    Some(t) => format!("{}ms", t),
                    None => "-".to_string(),
                }
            ));
            if r.headers.is_none() {
                md.push_str(&format!("- Headers: -\n"));
            } else {
                md.push_str(&format!(
                    "- Headers:\n{}\n",
                    match r.headers {
                        Some(headers) => {
                            headers
                                .iter()
                                .map(|h| {
                                    if h.0.to_lowercase() == "authorization" {
                                        format!("  - {}: xxxxxx", h.0)
                                    } else {
                                        format!("  - {}: {}", h.0, h.1)
                                    }
                                })
                                .collect::<Vec<String>>()
                                .join("\n")
                        }
                        None => "-".to_string(),
                    }
                ));
            }
            md.push_str(&format!(
                "- Body?: {}\n",
                match r.body {
                    Some(_) => "Yes".to_string(),
                    None => "No".to_string(),
                }
            ));

            md.push_str("\n");

            let strategy = item.strategy_mode.clone();

            match strategy {
                ScenarioItemCallStrategy::Load { duration, clients, rps } => {
                    md.push_str(&format!("**Strategy**: load for {} with {} clients @ {} RPS\n\n", 
                                            duration, clients, rps));

                    if !item.faults.is_empty() {
                        md.push_str("**Faults Applied**:\n\n");
                        match parse_duration::parse(duration.as_str()) {
                            Ok(total) => md.push_str(&faults_timeline(
                                &item.faults,
                                total,
                            )),
                            Err(_) => {}
                        }
                        md.push_str("\n");
                    } else {
                        md.push_str("**Faults Applied**:\n");
                        md.push_str("none\n");
                    };
                }
                ScenarioItemCallStrategy::Repeat { step, count, .. } => {
                    md.push_str(&format!(
                        "**Strategy**: repeat {} times with a step of {}\n\n",
                        count, step
                    ));

                    md.push_str("**Faults Applied**:\n");
                    if !item.faults.is_empty() {
                        for fault in &item.faults {
                            md.push_str(&format!(
                                "- {}\n",
                                fault_to_string(&fault)
                            ));
                        }
                        md.push_str("\n");
                    } else {
                        md.push_str("none\n");
                    }
                }
                ScenarioItemCallStrategy::Single {} => {
                    md.push_str(&format!("**Strategy**: single shot\n\n"));

                    md.push_str("**Faults Applied**:\n");
                    if !item.faults.is_empty() {
                        for fault in &item.faults {
                            md.push_str(&format!(
                                "- {}\n",
                                fault_to_string(&fault)
                            ));
                        }
                        md.push_str("\n");
                    } else {
                        md.push_str("none\n");
                    }
                }
            }

            if let Some(expect) = item.expectation.clone() {
                md.push_str("**Expectation**: ");

                let mut x = String::new();

                if let Some(r) = expect.response_time_under {
                    x.push_str(&format!("Response time Under {}ms | ", r));
                }

                if let Some(c) = expect.status {
                    x.push_str(&format!("Status Code {}", c));
                }

                md.push_str(&x);
                md.push_str("\n\n");
            }

            md.push_str("**Run Overview**:\n\n");
            md.push_str("| Num. Requests | Num. Errors | Min. Response Time | Max Response Time | Mean Latency (ms) | Expectation Failures | Total Time |\n");
            md.push_str("|-----------|---------|--------------------|-------------------|-------------------|----------------------|------------|\n");
            for run in item.run_overview.iter() {
                md.push_str(&format!(
                    "| {} | {} ({:.1}%) | {:.2} | {:.2} | {:.2} | {} | {} |\n",
                    run.requests_count,
                    run.error_count,
                    (run.error_count * 100) as f64 / run.requests_count as f64,
                    run.min_latency,
                    run.max_latency,
                    run.latency_percentiles[1].latency,
                    run.failure_count,
                    HumanTime::from(Duration::milliseconds(
                        run.total_time as i64
                    ))
                    .to_text_en(
                        Accuracy::Precise,
                        chrono_humanize::Tense::Present
                    )
                ));
            }
            md.push_str("\n");

            md.push_str("| Latency Percentile | Latency (ms) | Num. Requests (% of total) |\n");
            md.push_str("|------------|--------------|-----------|\n");
            for run in item.run_overview.iter() {
                md.push_str(&format!(
                    "| p25 | {:.2} | {} ({:.1}%) |\n",
                    run.latency_percentiles[0].latency,
                    run.latency_percentiles[0].count,
                    (run.latency_percentiles[0].count * 100) as f64
                        / run.requests_count as f64,
                ));
                md.push_str(&format!(
                    "| p50 | {:.2} | {} ({:.1}%) |\n",
                    run.latency_percentiles[1].latency,
                    run.latency_percentiles[1].count,
                    (run.latency_percentiles[1].count * 100) as f64
                        / run.requests_count as f64,
                ));
                md.push_str(&format!(
                    "| p75 | {:.2} | {} ({:.1}%) |\n",
                    run.latency_percentiles[2].latency,
                    run.latency_percentiles[2].count,
                    (run.latency_percentiles[2].count * 100) as f64
                        / run.requests_count as f64,
                ));
                md.push_str(&format!(
                    "| p95 | {:.2} | {} ({:.1}%) |\n",
                    run.latency_percentiles[3].latency,
                    run.latency_percentiles[3].count,
                    (run.latency_percentiles[3].count * 100) as f64
                        / run.requests_count as f64,
                ));
                md.push_str(&format!(
                    "| p99 | {:.2} | {} ({:.1}%) |\n",
                    run.latency_percentiles[4].latency,
                    run.latency_percentiles[4].count,
                    (run.latency_percentiles[4].count * 100) as f64
                        / run.requests_count as f64,
                ));
            }
            md.push_str("\n");

            // SLO table
            if !item.slo_impact_table.is_empty() {
                md.push_str("| SLO       | Pass? | Objective | Margin | Num. Requests Over Threshold (% of total) |\n");
                md.push_str("|-----------|-------|-----------|--------|--------------------------|\n");
                for row in &item.slo_impact_table {
                    md.push_str(&format!(
                        "| {} | {} | {} | {} | {} ({:.1}%) |\n",
                        row.title,
                        if row.pass { "✅" } else { "❌" },
                        format!(
                            "{}% < {}{}",
                            row.objective, row.threshold, row.unit
                        ),
                        row.margin_text,
                        row.calls_over_threshold,
                        row.calls_over_threshold_percent
                    ));
                }
                md.push_str("\n");
            }
        }

        md.push_str("\n---\n");
    }

    md
}

fn faults_timeline(
    faults: &Vec<FaultConfiguration>,
    total: std::time::Duration,
) -> String {
    let mut table = String::new();
    table.push_str("| Type | Timeline | Description |\n");
    table.push_str("|------|----------|-------------|\n");

    for fault in faults {
        if let Some(spec) = fault.get_period() {
            let (start_fraction, end_fraction) = spec.as_period(total);
            table.push_str(&format!(
                "| {} | {} | {} |\n",
                fault.kind(),
                timeline_line(start_fraction, end_fraction, 10),
                fault_to_string(&fault)
            ));
        } else {
            table.push_str(&format!(
                "| {} | {} | {} |\n",
                fault.kind(),
                timeline_line(0.0, 1.0, 10),
                fault_to_string(&fault)
            ));
        }
    }
    table.push_str("\n");

    table
}

fn timeline_line(
    start_fraction: f64,
    end_fraction: f64,
    width: usize,
) -> String {
    let mut timeline = String::with_capacity(width);
    let chunk = 1.0 / width as f64;
    for i in 0..width {
        let pos = i as f64 * chunk;
        if pos < start_fraction {
            timeline.push('.');
        } else if pos >= start_fraction && pos < end_fraction {
            timeline.push('x');
        } else {
            timeline.push('.');
        }
    }
    format!("0% `{}` 100%", timeline)
}

fn fault_to_string(fault: &FaultConfiguration) -> String {
    let mut s = String::new();
    match fault {
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
            ..
        } => {
            s.push_str("Latency: ");
            let mut details = Vec::new();

            details.push(scope_to_string(
                &side.clone().unwrap_or_default(),
                &Direction::from_str(
                    &direction.clone().unwrap_or("ingress".to_string()),
                )
                .unwrap(),
            ));

            details.push(format!(
                "Per Read/Write Op.: {}",
                !global.unwrap_or(true)
            ));

            if let Some(dist) = distribution {
                details.push(format!("Distribution: {}", dist));
            }
            if let Some(m) = mean {
                details.push(format!("Mean: {:.2} ms", m));
            }
            if let Some(s) = stddev {
                details.push(format!("Stddev: {:.2} ms", s));
            }
            if let Some(min) = min {
                details.push(format!("Min: {:.2} ms", min));
            }
            if let Some(max) = max {
                details.push(format!("Max: {:.2} ms", max));
            }
            if let Some(shape) = shape {
                details.push(format!("Shape: {:.2}", shape));
            }
            if let Some(scale) = scale {
                details.push(format!("Scale: {:.2}", scale));
            }

            s.push_str(&format!("{}", details.join(", ")));

            s
        }
        FaultConfiguration::PacketLoss { direction, side, .. } => {
            s.push_str("Packet Loss: ");

            s.push_str(&scope_to_string(
                &side.clone().unwrap_or_default(),
                &Direction::from_str(
                    &direction.clone().unwrap_or("ingress".to_string()),
                )
                .unwrap(),
            ));

            s
        }
        FaultConfiguration::Bandwidth {
            rate, unit, direction, side, ..
        } => {
            s.push_str("Bandwidth: ");

            s.push_str(&scope_to_string(
                &side.clone().unwrap_or_default(),
                &Direction::from_str(
                    &direction.clone().unwrap_or("ingress".to_string()),
                )
                .unwrap(),
            ));

            s.push_str(&format!("Rate: {}{}", rate, unit));

            s
        }
        FaultConfiguration::Jitter {
            amplitude: jitter_amplitude,
            frequency: jitter_frequency,
            direction,
            side,
            ..
        } => {
            s.push_str("Jitter: ");

            s.push_str(&scope_to_string(
                &side.clone().unwrap_or_default(),
                &Direction::from_str(
                    &direction.clone().unwrap_or("ingress".to_string()),
                )
                .unwrap(),
            ));

            s.push_str(&format!(
                "Amplitude: {:.2}ms, Frequence {:.2}Hz",
                jitter_amplitude, jitter_frequency
            ));

            s
        }
        FaultConfiguration::Dns { rate: dns_rate, .. } => {
            s.push_str(&format!("DNS Fault - Rate: {}%", dns_rate * 100.0));
            s
        }
        FaultConfiguration::HttpError {
            status_code,
            body: _,
            probability,
            ..
        } => {
            s.push_str(&format!(
                "HTTP Error Fault: Status: {}, Probablility: {}",
                status_code, probability
            ));
            s
        }
        FaultConfiguration::Blackhole { direction, side, .. } => {
            s.push_str("Blackhole: ");

            s.push_str(&scope_to_string(
                &side.clone().unwrap_or_default(),
                &Direction::from_str(
                    &direction.clone().unwrap_or("ingress".to_string()),
                )
                .unwrap(),
            ));

            s
        }
    }
}

fn scope_to_string(side: &StreamSide, direction: &Direction) -> String {
    let mut s = String::new();

    match side {
        StreamSide::Server => {
            match direction {
                Direction::Ingress => s.push_str(&"➡️"),
                Direction::Egress => s.push_str(&"⬅️"),
                Direction::Both => s.push_str(&"↔️"),
            };

            s.push_str(&"🖧");
        }
        StreamSide::Client => {
            s.push_str(&"🖥️");

            match direction {
                Direction::Ingress => s.push_str(&"⬅️"),
                Direction::Egress => s.push_str(&"➡️"),
                Direction::Both => s.push_str(&"↔️"),
            };
        }
    };

    s
}
