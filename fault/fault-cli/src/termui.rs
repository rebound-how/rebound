#![allow(clippy::format_in_format_args)]
use std::collections::HashMap;
use std::path::Path;
use std::sync::Arc;
use std::sync::Mutex;
use std::time::Duration;
use std::time::Instant;

use anyhow::Result;
use chrono::TimeDelta;
use chrono_humanize::Accuracy;
use chrono_humanize::HumanTime;
use chrono_humanize::Tense;
use colorful::Color;
use colorful::Colorful;
use indicatif::MultiProgress;
use indicatif::ProgressBar;
use indicatif::ProgressDrawTarget;
use indicatif::ProgressStyle;
#[cfg(feature = "injection")]
use inquire::Confirm;
#[cfg(feature = "injection")]
use inquire::Select;
use tokio::sync::RwLock;
use tokio::sync::broadcast;

use crate::cli::RunCommandOptions;
use crate::config::FaultKind;
use crate::event::FaultEvent;
use crate::event::TaskId;
use crate::event::TaskProgressEvent;
use crate::event::TaskProgressReceiver;
#[cfg(feature = "discovery")]
use crate::inject::Platform;
use crate::plugin::rpc::RpcPluginManager;
#[cfg(feature = "scenario")]
use crate::scenario;
#[cfg(feature = "scenario")]
use crate::scenario::event::ScenarioEventPhase;
#[cfg(feature = "scenario")]
use crate::scenario::event::ScenarioEventReceiver;
#[cfg(feature = "scenario")]
use crate::scenario::event::ScenarioItemLifecycle;
#[cfg(feature = "scenario")]
use crate::scenario::types::ItemExpectation;
#[cfg(feature = "scenario")]
use crate::scenario::types::ItemExpectationDecision;
use crate::sched::EventType;
use crate::sched::FaultPeriodEvent;
use crate::types::LatencyDistribution;
use crate::types::ProxyMap;

/// Struct to hold information about each task
struct TaskInfo {
    pb: ProgressBar,
    url: String,
    resolution_time: f64,
    started: Instant,
    ttfb: Option<Duration>,
    faults: Vec<FaultEvent>,
    status_code: Option<u16>,
    events: Vec<FaultEvent>,
}

pub fn long_operation(message: &str, size: Option<u64>) -> ProgressBar {
    if size.is_some() {
        let pb =
            ProgressBar::with_draw_target(size, ProgressDrawTarget::stdout());
        pb.enable_steady_tick(Duration::from_millis(80));
        pb.set_style(
            ProgressStyle::with_template(
                "{spinner:.green} [{elapsed_precise}] {pos}/{len} - {msg}",
            )
            .unwrap()
            .tick_strings(&["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]),
        );
        pb.set_message(message.to_string());

        pb
    } else {
        let pb =
            ProgressBar::with_draw_target(None, ProgressDrawTarget::stdout());
        pb.enable_steady_tick(Duration::from_millis(80));
        pb.set_style(
            ProgressStyle::with_template(
                "{spinner:.green} [{elapsed_precise}] {msg}",
            )
            .unwrap()
            .tick_strings(&["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]),
        );
        pb.set_message(message.to_string());

        pb
    }
}

pub async fn lean_progress(
    receiver: kanal::AsyncReceiver<TaskProgressEvent>,
    shutdown_rx: kanal::AsyncReceiver<()>,
    total_duration: Option<Duration>,
    has_scheduled_faults: bool,
) {
    let total_run = match total_duration {
        Some(d) => d.as_secs_f64(),
        None => 0.0,
    };

    let mb = MultiProgress::with_draw_target(ProgressDrawTarget::stdout());

    let base_indent = " ".repeat(5);

    let turtle_bar = mb.add(
        ProgressBar::with_draw_target(None, ProgressDrawTarget::stdout())
            .with_finish(indicatif::ProgressFinish::AndLeave),
    );
    let elapsed_bar = mb.add(
        ProgressBar::with_draw_target(None, ProgressDrawTarget::stdout())
            .with_finish(indicatif::ProgressFinish::AndLeave),
    );
    let status_bar = mb.add(
        ProgressBar::with_draw_target(None, ProgressDrawTarget::stdout())
            .with_finish(indicatif::ProgressFinish::AndLeave),
    );

    let turtle_template;
    if total_duration.is_some() {
        if has_scheduled_faults {
            turtle_template =
                format!("{}{{spinner:.green}} Progress: {{msg}}", base_indent);
            turtle_bar.enable_steady_tick(Duration::from_millis(100));
        } else {
            turtle_template = format!("{}Progress: {{msg}}", base_indent);
        }
    } else {
        turtle_template = format!("{}  {{msg}}", base_indent);
    }

    turtle_bar.set_style(
        ProgressStyle::with_template(turtle_template.as_str())
            .unwrap()
            .tick_strings(&["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]),
    );

    let turtle_start = tokio::time::Instant::now();
    let turtle_lane_width = 52;
    let step_sec = total_run / turtle_lane_width as f64;
    let step = if total_duration.is_some() {
        Duration::from_secs_f64(step_sec)
    } else {
        Duration::from_secs_f64(1.0)
    };
    let mut turtle_move_interval = tokio::time::interval(step);

    elapsed_bar.set_style(
        ProgressStyle::with_template(
            format!("{}{{msg}}", base_indent).as_str(),
        )
        .unwrap()
        .tick_strings(&["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]),
    );
    let mut elapsed_interval =
        tokio::time::interval(Duration::from_secs_f64(1.0));

    let mut chr = "".to_string();
    if total_duration.is_none() {
        chr = "".to_string();
    }
    status_bar.set_style(
        ProgressStyle::with_template(
            format!("{}{}{{spinner:.green}} {{msg}}", chr, base_indent)
                .as_str(),
        )
        .unwrap()
        .tick_strings(&["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]),
    );

    status_bar.enable_steady_tick(Duration::from_millis(100));
    status_bar.set_message(format!(
        "{}",
        "Waiting for incoming traffic...".gradient(Color::LightGreen)
    ));

    let mut started_count = 0usize;
    let mut passthrough_count = 0usize;
    let mut faults_count = 0usize;
    let mut error_count = 0usize;

    let delta = TimeDelta::new(total_run as i64, 0).unwrap();
    let display_duration = HumanTime::from(delta);
    let human_end_time =
        display_duration.to_text_en(Accuracy::Precise, Tense::Present);

    let start = Instant::now();
    let mut end: Option<Instant> = None;
    if let Some(d) = total_duration {
        end = Some(start + d);
    }

    let dimmed_dash = format!("{}", "-".dim());

    loop {
        tokio::select! {
            _ = elapsed_interval.tick() => {
                let mut line = String::new();

                let s = start.elapsed().as_secs();
                let (h, s) = (s / 3600, s % 3600);
                let (m, s) = (s / 60, s % 60);

                line.push_str(format!("Elapsed {} ", format!("{:02}:{:02}:{:02}", h, m, s).light_yellow()).as_str());

                if total_duration.is_some() {
                    if let Some(e) = end {
                        let now = Instant::now();
                        let remaining_duration = e - now;
                        let remaining_secs = remaining_duration.as_secs_f64();
                        let remaining = (remaining_secs / total_run) * 100.0;

                        line.push_str(
                            format!(" | Remaining {}", format!("{:.2}%", remaining).light_yellow()
                        ).as_str());
                    }

                    line.push_str(format!(" | Total {}", human_end_time.clone().light_yellow()).as_str());
                }

                elapsed_bar.set_message(line);
            }

            _ = turtle_move_interval.tick() => {
                let mut line = String::new();

                if total_duration.is_some() {
                    // display elapsed time so far
                    let elapsed_seconds = turtle_start.elapsed().as_secs_f64();
                    if elapsed_seconds >= total_run {
                        break
                    } else {
                        let fraction = elapsed_seconds / total_run;
                        let turtle_col = (fraction * turtle_lane_width as f64).round() as usize + 1;

                        let mut finished = true;
                        for i in 0..turtle_lane_width {
                            if i < turtle_col {
                                line.push_str(dimmed_dash.as_str());
                            } else if i == turtle_col {
                                line.push('🐢');
                            } else if i == turtle_lane_width - 1 {
                                line.push(' ');
                            } else {
                                finished = false;
                                line.push('-');
                            }
                        }

                        if finished {
                            line.push('🏆');
                        } else {
                            line.push('🏁');
                        }
                    }
                }

                if !line.is_empty() {
                    turtle_bar.set_message(line);
                }
            }
            event = receiver.recv() => {
                match event {
                    Ok(event) => {
                        match event {
                            TaskProgressEvent::FaultApplied { .. } => {
                                faults_count += 1;
                            },
                            TaskProgressEvent::Started { .. } => {
                                started_count += 1;
                            },
                            TaskProgressEvent::Passthrough { .. } => {
                                passthrough_count += 1;
                            },
                            TaskProgressEvent::Error { .. } => {
                                error_count += 1;
                            },
                            _ => {
                            }
                        }

                        let line = format!(
                            "Total Events {}, Applied Faults {}, Passthrough {}, Errors: {}",
                            format!("{}", started_count).light_cyan(),
                            format!("{}", faults_count).light_yellow(),
                            format!("{}", passthrough_count).light_blue(),
                            format!("{}", error_count).light_red()
                        );

                        status_bar.set_message(line);
                    },
                    Err(_) => {
                        break;
                    }
                }
            }

            _ = shutdown_rx.recv() => {
                tracing::info!("Shutdown signal received. Stopping progress bar.");
                break;
            },
        }
    }

    turtle_bar.finish();
    elapsed_bar.finish();

    status_bar.finish_with_message(format!(
        "{} {} completed, {} applied faults, {} passthrough, {} errors",
        format!("{}", "All done!".bold()),
        format!("{}", started_count).light_cyan(),
        format!("{}", faults_count).light_yellow(),
        format!("{}", passthrough_count).light_blue(),
        format!("{}", error_count).light_red()
    ));
}

pub async fn full_progress(
    shutdown_rx: kanal::AsyncReceiver<()>,
    mut receiver: kanal::AsyncReceiver<TaskProgressEvent>,
) {
    let multi = MultiProgress::with_draw_target(ProgressDrawTarget::stdout());

    let style = ProgressStyle::default_bar()
        .template("    {spinner:.green} {msg}")
        .unwrap()
        .tick_strings(&["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
        .progress_chars("=> ");

    let mut task_map: HashMap<TaskId, TaskInfo> = HashMap::new();

    let _ = multi.println(format!("\n    {}\n\n", "Stream:".bold()));

    let mut started_count = 0usize;
    let mut passthrough_count = 0usize;
    let mut faults_count = 0usize;
    let mut error_count = 0usize;

    let start = Instant::now();

    loop {
        tokio::select! {
            _ = shutdown_rx.recv() => {
                tracing::info!("Shutdown signal received. Stopping traffic tail.");
                break;
            },

            event = receiver.recv() => {
                match event {
                    Ok(event) => {
                        match event {
                            TaskProgressEvent::Started { id, ts, url, src_addr } => {
                                started_count += 1;

                                let pb = multi.add(ProgressBar::new_spinner());
                                pb.set_style(style.clone());
                                pb.enable_steady_tick(Duration::from_millis(80));
                                pb.tick();

                                let m = format!("{} {}", "URL:".dim(), url.clone().light_blue());

                                pb.set_message(m);

                                let task_info =
                                    TaskInfo { pb, url, resolution_time: 0.0, faults: Vec::new(), status_code: None, events: Vec::new(), started: ts, ttfb: None };
                                task_map.insert(id, task_info);
                            }
                            TaskProgressEvent::IpResolved { id, ts: _, domain: _, time_taken } => {
                                if let Some(task_info) = task_map.get_mut(&id) {
                                    task_info.resolution_time = time_taken;

                                    let u = format!("{} {}", "URL:".dim(), task_info.url.clone().light_blue());
                                    let d = format!("{} {:.3}ms", "DNS:".dim(), time_taken);

                                    task_info.pb.set_message(format!("{} | {} | ...", u, d));
                                }
                            },
                            TaskProgressEvent::WithFault { id, ts: _, fault } => {
                                if let Some(task_info) = task_map.get_mut(&id) {
                                    task_info.faults.push(fault.clone());

                                    let u = format!("{} {}", "URL:".dim(), task_info.url.clone().light_blue());
                                    let d = format!("{} {:.3}ms", "DNS:".dim(), task_info.resolution_time);
                                    let f = fault_to_string(&task_info.faults);
                                    task_info.pb.set_message(format!("{} | {} | {} | ...", u, d, f));
                                }
                            }
                            TaskProgressEvent::Ttfb { id, ts: _ } => {
                                if let Some(task_info) = task_map.get_mut(&id) {
                                    task_info.ttfb = Some(task_info.started.elapsed());
                                }
                            }
                            TaskProgressEvent::FaultApplied { id, ts: _, fault } => {
                                if let Some(task_info) = task_map.get_mut(&id) {
                                    faults_count += 1;
                                    task_info.events.push(fault.clone());
                                }
                            }
                            TaskProgressEvent::ResponseReceived { id, ts: _, status_code } => {
                                if let Some(task_info) = task_map.get_mut(&id) {
                                    let c = "Status:".dim();
                                    let m = if (200..300).contains(&status_code) {
                                        status_code.to_string().green()
                                    } else if (400..500).contains(&status_code) {
                                        status_code.to_string().yellow()
                                    } else if status_code == 0 {
                                        "-".to_string().dim()
                                    } else {
                                        status_code.to_string().red()
                                    };

                                    let s = format!("{} {}", c, m);

                                    task_info.status_code = Some(status_code);
                                    let u = format!("{} {}", "URL:".dim(), task_info.url.clone().light_blue());
                                    let d = format!("{} {:.3}ms", "DNS:".dim(), task_info.resolution_time);
                                    let f = format!("{} {}", "Faults:".dim(), fault_to_string(&task_info.faults).yellow());

                                    task_info.pb.set_message(format!("{} | {} | {} | {}", u, d, f, s));
                                }
                            }
                            TaskProgressEvent::Passthrough {id, time_taken, from_downstream_length, from_upstream_length, .. } => {
                                if let Some(task_info) = task_map.remove(&id) {
                                    passthrough_count += 1;

                                    let c = "Status:".dim();
                                    let status_code = task_info.status_code.unwrap_or(0);

                                    let m = if (200..300).contains(&status_code) {
                                        status_code.to_string().green()
                                    } else if (400..500).contains(&status_code) {
                                        status_code.to_string().yellow()
                                    } else if status_code == 0 {
                                        "-".to_string().dim()
                                    } else {
                                        status_code.to_string().red()
                                    };

                                    let s = format!("{} {}", c, m);
                                    let u = format!("{} {}", "URL:".dim(), task_info.url.light_blue());
                                    let d = format!("{} {:.3}ms", "DNS:".dim(), task_info.resolution_time);

                                    let ttfb = match task_info.ttfb {
                                        Some(d) => format!("{:.3}ms", d.as_millis_f64()),
                                        None => "-".to_string()
                                    };

                                    let h = format!(
                                        "{} {:.3}ms | {} {} | {} ⭫{}/b ⭭{}/b",
                                        "Duration:".dim(),
                                        time_taken.as_millis_f64(),
                                        "TTFB".dim(),
                                        ttfb,
                                        "Sent/Received:".dim(),
                                        from_downstream_length,
                                        from_upstream_length
                                    );

                                    task_info.pb.finish_with_message(format!(
                                        "{} | {} | {} | {} | {} |",
                                        u, d, "Passthrough".light_blue(), s, h
                                    ));
                                }
                            },
                            TaskProgressEvent::Completed {
                                id,
                                ts: _,
                                time_taken: _,
                                from_downstream_length,
                                from_upstream_length,
                            } => {
                                if let Some(task_info) = task_map.remove(&id) {
                                    let c = "Status:".dim();
                                    let status_code = task_info.status_code.unwrap_or(0);

                                    let m = if (200..300).contains(&status_code) {
                                        status_code.to_string().green()
                                    } else if (400..500).contains(&status_code) {
                                        status_code.to_string().yellow()
                                    } else if status_code == 0 {
                                        "-".to_string().dim()
                                    } else {
                                        status_code.to_string().red()
                                    };

                                    let s = format!("{} {}", c, m);
                                    let u = format!("{} {}", "URL:".dim(), task_info.url.light_blue());
                                    let d = format!("{} {:.3}ms", "DNS:".dim(), task_info.resolution_time);

                                    let mut fault_results = String::new();

                                    let mut sep = "".to_string();

                                    for fault in task_info.faults.clone() {
                                        if let FaultEvent::Latency { .. } = &fault {
                                            /*let max_events = 20;

                                            let sparkline: String = task_info.events.iter()
                                                .filter_map(|f| {
                                                    if let FaultEvent::Latency { direction, side, delay: Some(d) } = f {
                                                        Some(latency_to_sparkline_char(*d))
                                                    } else {
                                                        None
                                                    }
                                                })
                                                .rev()
                                                .take(max_events)
                                                .collect::<Vec<_>>()
                                                .iter()
                                                .rev()
                                                .map(|c| c.to_string())
                                                .collect();
                                            fault_results.push_str(&format!("{} {}{} ", format!("{} latency", side).cyan(), "".to_string(), &sparkline));
                                            */
                                            let mut latency = 0.0;
                                            if !task_info.events.is_empty() {
                                                let mut count = 0;
                                                let total: f64 = task_info.events.iter()
                                                .map(|f| {
                                                    if let FaultEvent::Latency { direction: _, side: _, delay: Some(d) } = f {
                                                        count += 1;
                                                        d.as_millis_f64()
                                                    } else {
                                                        0.0
                                                    }
                                                })
                                                .collect::<Vec<f64>>()
                                                .iter()
                                                .sum();

                                                latency = total / count as f64;
                                            }

                                            fault_results.push_str(&format!("{}{} ~{:.3}ms", sep, "Latency".yellow(), latency));
                                            sep = " - ".to_string();
                                        } else if let FaultEvent::Bandwidth { ..  } = &fault {

                                            let mut bandwidth = 0;
                                            if !task_info.events.is_empty() {
                                                let mut count = 0;
                                                let total: usize = task_info.events.iter()
                                                .map(|f| {
                                                    if let FaultEvent::Bandwidth { direction: _, side: _, bps: Some(d) } = f {
                                                        count += 1;
                                                        *d
                                                    } else {
                                                        0
                                                    }
                                                })
                                                .collect::<Vec<usize>>()
                                                .iter()
                                                .sum();

                                                bandwidth = total / count;
                                            }

                                            let formatted_rate = format!("~{}", format_bandwidth(bandwidth));
                                            fault_results.push_str(&format!("{}{} {}", sep, "Bandwidth".yellow(), &formatted_rate));
                                            sep = " - ".to_string();
                                        } else if let FaultEvent::PacketLoss { .. } = &fault {
                                            fault_results.push_str(&format!("{}{}", sep, "Packet Loss".yellow()));
                                            sep = " - ".to_string();
                                        } else if let FaultEvent::HttpResponseFault { .. } = &fault {
                                            fault_results.push_str(&format!("{}{}", sep, "Http".yellow()));
                                            sep = " - ".to_string();
                                        } else if let FaultEvent::Dns { ..  } = &fault {
                                            fault_results.push_str(&format!("{}{}", sep, "Dns".yellow()));
                                            sep = " - ".to_string();
                                        } else if let FaultEvent::Jitter { ..  } = &fault {
                                            fault_results.push_str(&format!("{}{}", sep, "Jitter".yellow()));
                                            sep = " - ".to_string();
                                        } else if let FaultEvent::Blackhole { ..  } = &fault {
                                            fault_results.push_str(&format!("{}{}", sep, "Blackhole".yellow()));
                                            sep = " - ".to_string();
                                        }

                                        fault_results.push_str("");
                                    }

                                    if fault_results.is_empty() {
                                        fault_results.push_str(&format!("{}", "No Faults Applied".to_string().light_blue()));
                                    }

                                    let ttfb = match task_info.ttfb {
                                        Some(d) => format!("{:.3}ms", d.as_millis_f64()),
                                        None => "-".to_string()
                                    };

                                    let h = format!(
                                        "{} {:.3}ms | {} {} | {} ⭫{}/b ⭭{}/b",
                                        "Duration:".dim(),
                                        task_info.started.elapsed().as_millis_f64(),
                                        "TTFB".dim(),
                                        ttfb,
                                        "Sent/Received:".dim(),
                                        from_downstream_length,
                                        from_upstream_length
                                    );

                                    task_info.pb.finish_with_message(format!(
                                        "{} | {} | {} | {} | {} |",
                                        u, d, fault_results, s, h
                                    ));
                                }
                            }
                            TaskProgressEvent::Error { id, ts: _, error } => {
                                if let Some(task_info) = task_map.remove(&id) {
                                    error_count += 1;

                                    let u = format!("{} {}", "URL:".dim(), task_info.url.light_blue());
                                    let d = format!("{} {:.2}ms", "DNS:".dim(), task_info.resolution_time);
                                    let f = fault_to_string(&task_info.faults);
                                    let e = format!("{} {}", "Failed:".red(), error);

                                    task_info
                                        .pb
                                        .finish_with_message(format!("{} | {} | {} | {} |", u, d, f, e));
                                }
                            }
                        }
                    }
                    Err(_) => {
                        break;
                    }
                }
            }
        }
    }

    let delta = TimeDelta::new(start.elapsed().as_secs() as i64, 0).unwrap();

    let pb = multi.add(
        ProgressBar::with_draw_target(None, ProgressDrawTarget::stdout())
            .with_finish(indicatif::ProgressFinish::AndLeave),
    );
    pb.set_style(ProgressStyle::with_template("{msg}").unwrap());
    pb.finish_with_message(format!(
        "\n    {} {} completed, {} applied faults, {} passthrough, {} errors - Total Time {}\n",
        format!("{}", "All done!".bold()),
        format!("{}", started_count).light_cyan(),
        format!("{}", faults_count).light_yellow(),
        format!("{}", passthrough_count).light_blue(),
        format!("{}", error_count).light_red(),
        format!("{}", HumanTime::from(delta).to_text_en(Accuracy::Rough, Tense::Present).dim())
    ));
}

fn fault_to_string(faults: &Vec<FaultEvent>) -> String {
    let mut b = Vec::new();

    for fault in faults {
        let f = match fault {
            FaultEvent::Latency { side, .. } => format!("{} latency", side),
            FaultEvent::Dns { side, .. } => format!("{} dns", side),
            FaultEvent::Bandwidth { side, .. } => format!("{} bandwidth", side),
            FaultEvent::Jitter { side, .. } => format!("{} jitter", side),
            FaultEvent::PacketLoss { side, .. } => {
                format!("{} packet loss", side)
            }
            FaultEvent::HttpResponseFault { side, .. } => {
                format!("{} http error", side)
            }
            FaultEvent::Blackhole { side, .. } => format!("{} blackhole", side),
            FaultEvent::Grpc { side, .. } => format!("{} grpc", side),
        };
        b.push(f);
    }

    b.join(", ")
}

/// Helper function to format bandwidth rate into human-readable string.
fn format_bandwidth(bps: usize) -> String {
    if bps >= 1_000_000_000 {
        format!("{:.2} GBps", bps as f64 / 1_000_000_000.0)
    } else if bps >= 1_000_000 {
        format!("{:.2} MBps", bps as f64 / 1_000_000.0)
    } else if bps >= 1_000 {
        format!("{:.2} KBps", bps as f64 / 1_000.0)
    } else {
        format!("{} Bps", bps)
    }
}

pub async fn quiet_handle_displayable_events(
    receiver: kanal::AsyncReceiver<TaskProgressEvent>,
) {
    loop {
        tokio::select! {
            event = receiver.recv() => {
                match event {
                    Ok(_) => {}
                    Err(_) => {
                        break;
                    }
                }
            }
        }
    }
}

#[allow(clippy::too_many_arguments)]
pub async fn proxy_prelude(
    proxy_address: String,
    disable_http_proxy: bool,
    proxied_protos: Vec<ProxyMap>,
    plugins: Arc<RwLock<RpcPluginManager>>,
    opts: &RunCommandOptions,
    upstreams: &[String],
    events: Vec<FaultPeriodEvent>,
    total_duration: Option<Duration>,
    tailing: bool,
) {
    let g = "fault.".gradient(Color::DarkOrange);
    let r = "Your Reliability Toolbox".gradient(Color::Purple1a);
    let a = format!("http://{}", proxy_address).cyan();
    let pp = proxied_protos
        .iter()
        .map(|p| {
            format!(
                "     - {} {} {} {}",
                format!("{}:{}", p.proxy.proxy_ip, p.proxy.proxy_port).cyan(),
                "=>".dim(),
                format!("{}:{}", p.remote.remote_host, p.remote.remote_port)
                    .cyan(),
                "[tcp: tunnel]".dim()
            )
            .to_string()
        })
        .collect::<Vec<_>>()
        .join("\n");

    let plugins_lock = plugins.read().await;
    let pl = plugins_lock
        .clone()
        .plugins
        .read()
        .await
        .iter()
        .map(|p| match p.meta.clone() {
            Some(meta) => format!(
                "     - {} {}",
                meta.name.clone().cyan(),
                format!("[{} | {}]", meta.version, p.addr).dim()
            )
            .to_string(),
            None => format!(
                "     - {} {}",
                format!("{}", p.addr.clone().cyan()),
                "[not connected]".dim()
            )
            .to_string(),
        })
        .collect::<Vec<String>>()
        .join("\n");

    let mut hosts;

    if !upstreams.is_empty() {
        hosts = upstreams.to_vec().join(", ").to_string();
        if hosts == "*" {
            hosts = "All Hosts".to_string();
        }
        hosts = format!("🎯 {}", hosts.dim());
    } else {
        hosts = format!("💡 {}", "No upstream hosts configured for the HTTP proxy. No faults will be applied.".color(Color::Orange1).dim());
    }

    let other_proxies;

    if pp.is_empty() {
        other_proxies = format!("");
    } else {
        other_proxies = format!("{}\n", pp);
    }

    if disable_http_proxy {
        println!(
            "
    Welcome to {} — {}!

    {}
{}",
            g,
            r,
            "Enabled Proxies:".bold(),
            other_proxies,
        );
    } else {
        println!(
            "
    Welcome to {} — {}!

    {}
     - {} {}
       {} {}
     - {} {}
       {} {}
{}",
            g,
            r,
            "Enabled Proxies:".bold(),
            a,
            "[HTTP: forward]".dim(),
            "Target Upstreams:".dim(),
            hosts,
            a,
            "[HTTP: tunnel]".dim(),
            "Target Upstreams:".dim(),
            hosts,
            other_proxies,
        );
    }

    if !pl.is_empty() {
        println!("{}", format!("    {}\n{}", "Plugins:".bold().white(), pl));
    } else {
        println!(
            "{}",
            format!(
                "    {}\n     {}",
                "Plugins:".bold().white(),
                "No plugins provided.".color(Color::Orange1).dim()
            )
        );
    }

    // Summary header with a bit of color
    println!("{}", "\n    Configured Faults:".bold().white());

    // HTTP Response Fault
    if opts.http_error.enabled {
        if let Some(body) = &opts.http_error.http_response_body {
            println!(
                "{}",
                format!(
                    "     - {}: {}: {}, {}: {}, {}: {}",
                    "HTTP Response".cyan(),
                    "status".dim(),
                    opts.http_error.http_response_status_code,
                    "probability".dim(),
                    opts.http_error.http_response_trigger_probability,
                    "body".dim(),
                    body
                )
            );
        } else {
            println!(
                "{}",
                format!(
                    "     - {}: {}: {}, {}: {}",
                    "HTTP Response".cyan(),
                    "status".dim(),
                    opts.http_error.http_response_status_code,
                    "probability".dim(),
                    opts.http_error.http_response_trigger_probability
                )
            );
        }
    }

    // Latency Fault
    if opts.latency.enabled {
        let mut latency_summary = format!(
            "     - {}: {}: {}, {}: {:?}, {}: {:?}, {}: {:?}",
            "Latency".cyan(),
            "per read/write".dim(),
            opts.latency.per_read_write,
            "side".dim(),
            opts.latency.side,
            "direction".dim(),
            opts.latency.latency_direction,
            "distribution".dim(),
            opts.latency.latency_distribution
        );

        // Depending on the distribution, display the relevant parameters
        match opts.latency.latency_distribution {
            LatencyDistribution::Uniform => {
                if let Some(min) = opts.latency.latency_min {
                    latency_summary.push_str(&format!(
                        ", {}: {}ms",
                        "min".dim(),
                        min
                    ));
                }
                if let Some(max) = opts.latency.latency_max {
                    latency_summary.push_str(&format!(
                        ", {}: {}ms",
                        "max".dim(),
                        max
                    ));
                }
            }
            LatencyDistribution::Normal => {
                if let Some(mean) = opts.latency.latency_mean {
                    latency_summary.push_str(&format!(
                        ", {}: {}ms",
                        "mean".dim(),
                        mean
                    ));
                }
                if let Some(stddev) = opts.latency.latency_stddev {
                    latency_summary.push_str(&format!(
                        ", {}: {}ms",
                        "stddev".dim(),
                        stddev
                    ));
                }
            }
            _ => {
                // For Pareto or ParetoNormal distributions
                if let Some(shape) = opts.latency.latency_shape {
                    latency_summary.push_str(&format!(
                        ", {}: {}",
                        "shape".dim(),
                        shape
                    ));
                }
                if let Some(scale) = opts.latency.latency_scale {
                    latency_summary.push_str(&format!(
                        ", {}: {}",
                        "scale".dim(),
                        scale
                    ));
                }
            }
        }
        println!("{}", latency_summary);
    }

    // Bandwidth Fault
    if opts.bandwidth.enabled {
        println!(
            "{}",
            format!(
                "     - {}: {}: {:?}, {}: {:?}, {}: {} {:?}",
                "Bandwidth".cyan(),
                "side".dim(),
                opts.bandwidth.side,
                "direction".dim(),
                opts.bandwidth.bandwidth_direction,
                "rate".dim(),
                opts.bandwidth.bandwidth_rate,
                opts.bandwidth.bandwidth_unit
            )
        );
    }

    // Jitter Fault
    if opts.jitter.enabled {
        println!(
            "{}",
            format!(
                "     - {}: {}: {:?}, {}: {}ms, {}: {}Hz",
                "Jitter".cyan(),
                "direction".dim(),
                opts.jitter.jitter_direction,
                "amplitude".dim(),
                opts.jitter.jitter_amplitude,
                "frequency".dim(),
                opts.jitter.jitter_frequency
            )
        );
    }

    // DNS Fault
    if opts.dns.enabled {
        println!(
            "{}",
            format!(
                "     - {}: {}: {}",
                "DNS".cyan(),
                "trigger probability".dim(),
                opts.dns.dns_rate
            )
        );
    }

    // Packet Loss Fault
    if opts.packet_loss.enabled {
        println!(
            "{}",
            format!(
                "     - {}: {}: {:?}, {}: {:?}",
                "Packet Loss".cyan(),
                "side".dim(),
                opts.packet_loss.side,
                "direction".dim(),
                opts.packet_loss.packet_loss_direction
            )
        );
    }

    // Blackhole Fault
    if opts.blackhole.enabled {
        println!(
            "{}",
            format!(
                "     - {}: {}: {:?}, {}: {:?}",
                "Blackhole".cyan(),
                "side".dim(),
                opts.blackhole.side,
                "direction".dim(),
                opts.blackhole.blackhole_direction
            )
        );
    }

    // If no fault is enabled, let the user know
    if !opts.http_error.enabled
        && !opts.latency.enabled
        && !opts.bandwidth.enabled
        && !opts.jitter.enabled
        && !opts.dns.enabled
        && !opts.packet_loss.enabled
        && !opts.blackhole.enabled
    {
        println!(
            "    {}",
            " No faults configured.".color(Color::Orange1).dim()
        );
    }

    let process_start = tokio::time::Instant::now();
    let (schedules, computed_total_duration) =
        build_fault_schedules(events, process_start, total_duration);

    if total_duration.is_some() && !schedules.is_empty() {
        let total_secs = computed_total_duration.as_secs_f64();
        println!("\n    {}", "Faults Schedule:".bold().white());
        schedule_timeline(&schedules, total_secs);
        if !tailing {
            println!("{}", "\n    Status:".bold().white());
        }
    } else if total_duration.is_some() && schedules.is_empty() {
        if !tailing {
            println!("{}", "\n    Status:".bold().white());
        }
    } else if total_duration.is_none() && !schedules.is_empty() {
        let total_secs = computed_total_duration.as_secs_f64();
        println!("\n    {}", "Faults Schedule:".bold().white());
        schedule_timeline(&schedules, total_secs);
    } else if total_duration.is_none() && schedules.is_empty() && !tailing {
        println!("{}", "\n    Status:".bold().white());
    }
}

pub fn demo_prelude(demo_address: String) {
    let g = "fault".gradient(Color::Plum4);
    println!(
        "
    Welcome to {}, this demo application is here to let you explore fault's capabilities.

    Here are a few examples:

    export HTTP_PROXY=http://localhost:3180
    export HTTPS_PROXY=http://localhost:3180

    curl -x ${{HTTP_PROXY}} http://{demo_address}/
    curl -x ${{HTTP_PROXY}} http://{demo_address}/ping
    curl -x ${{HTTP_PROXY}} http://{demo_address}/ping/myself
    curl -x ${{HTTP_PROXY}} --json '{{\"content\": \"hello\"}}' http://{demo_address}/uppercase

        ", g,
    );
}

#[derive(Debug, Clone)]
pub struct FaultInterval {
    pub start: f64,
    pub duration: f64,
}

#[derive(Debug, Clone)]
pub struct FaultSchedule {
    pub name: String,
    pub color: Color,
    pub intervals: Vec<FaultInterval>,
}

fn fault_kind_label_and_color(kind: FaultKind) -> (&'static str, Color) {
    match kind {
        FaultKind::Latency => ("Latency", Color::DeepSkyBlue1),
        FaultKind::Bandwidth => ("Bandwidth", Color::LightCoral),
        FaultKind::Dns => ("DNS", Color::Green),
        FaultKind::PacketLoss => ("PacketLoss", Color::Gold1),
        FaultKind::HttpError => ("HttpErr", Color::GreenYellow),
        FaultKind::Jitter => ("Jitter", Color::Purple1b),
        FaultKind::PacketDuplication => {
            ("PacketDuplication", Color::LightMagenta)
        }
        FaultKind::Blackhole => ("Blackhole", Color::Wheat4),
        FaultKind::Metrics => ("Metrics", Color::Pink1),
        FaultKind::Unknown => ("Unknown", Color::Grey0),
        FaultKind::Grpc => ("Grpc", Color::IndianRed1a),
    }
}

fn build_schedules(
    mut events: Vec<FaultPeriodEvent>,
    process_start: tokio::time::Instant,
    total_run: Duration,
) -> HashMap<FaultKind, Vec<FaultInterval>> {
    events.sort_by_key(|e| e.time);

    let mut intervals_map = HashMap::<FaultKind, Vec<FaultInterval>>::new();
    let mut active_starts = HashMap::<FaultKind, f64>::new();

    let run_secs = total_run.as_secs_f64();

    for evt in &events {
        let offset_secs = evt.time.duration_since(process_start).as_secs_f64();
        match evt.event_type {
            EventType::Start => {
                // Mark fault as active
                active_starts.insert(evt.fault_type, offset_secs);
            }
            EventType::Stop => {
                if let Some(start_sec) = active_starts.remove(&evt.fault_type) {
                    let dur = offset_secs - start_sec;
                    if dur > 0.0 {
                        intervals_map.entry(evt.fault_type).or_default().push(
                            FaultInterval { start: start_sec, duration: dur },
                        );
                    }
                }
            }
        }
    }

    // If the user never "stopped" a fault, but we want to
    // show it in the timeline up to run_secs
    for (&kind, &start_sec) in &active_starts {
        let dur = run_secs - start_sec;
        if dur > 0.0 {
            intervals_map
                .entry(kind)
                .or_default()
                .push(FaultInterval { start: start_sec, duration: dur });
        }
    }

    intervals_map
}

fn determine_timeline_end(
    events: &[FaultPeriodEvent],
    process_start: tokio::time::Instant,
    user_duration: Option<Duration>,
) -> Duration {
    if let Some(d) = user_duration {
        return d;
    }

    // If no user duration, we find the maximum offset among all events.
    // i.e. the last "time" from `events`.
    let mut max_offset_secs = 0.0;

    for evt in events {
        if evt.event_type == EventType::Stop {
            let offset = evt.time.duration_since(process_start).as_secs_f64();
            if offset > max_offset_secs {
                max_offset_secs = offset;
            }
        }
    }

    // Round up to the nearest second or so
    if max_offset_secs < 0.000_001 {
        // If we literally have no events, just pick 0 or 1 second
        return Duration::from_secs(0);
    }

    Duration::from_secs_f64(max_offset_secs)
}

fn build_fault_schedules(
    events: Vec<FaultPeriodEvent>,
    process_start: tokio::time::Instant,
    user_duration: Option<Duration>,
) -> (Vec<FaultSchedule>, Duration) {
    // 1) figure out how long the timeline is
    let total_run =
        determine_timeline_end(&events, process_start, user_duration);

    // 2) build intervals
    let intervals_map = build_schedules(events, process_start, total_run);

    // 3) map into a Vec<FaultSchedule>
    let mut schedules = Vec::new();
    for (kind, intervals) in intervals_map {
        let (label, color) = fault_kind_label_and_color(kind);
        schedules.push(FaultSchedule {
            name: label.to_string(),
            color,
            intervals,
        });
    }

    (schedules, total_run)
}

pub fn schedule_timeline(faults: &[FaultSchedule], total_run_seconds: f64) {
    if total_run_seconds <= 0.0 {
        return;
    }

    const INDENT: usize = 5;
    const TIMELINE_WIDTH: usize = 50 + INDENT;
    const LABEL_WIDTH: usize = 12 + INDENT;

    for fault in faults {
        let label = format!(
            "{}: ",
            format!("{:>width$}", fault.name, width = LABEL_WIDTH - 2).cyan()
        );

        let mut line = String::new();
        line.push_str(&label);

        for i in 0..TIMELINE_WIDTH {
            let fraction = i as f64 / TIMELINE_WIDTH as f64;
            let t = fraction * total_run_seconds;

            let active = fault.intervals.iter().any(|interval| {
                t >= interval.start && t < interval.start + interval.duration
            });

            if active {
                // Print a colored block for active
                let block = "█".color(fault.color);
                line.push_str(&block.to_string());
            } else {
                // '.' for inactive
                let dot = ".".dim();
                line.push_str(&dot.to_string());
            }
        }
        println!("{}", line);
    }
}

#[cfg(feature = "scenario")]
pub async fn scenario_ui(mut scenario_event_receiver: ScenarioEventReceiver) {
    let m = MultiProgress::new();
    let mut progress: Option<ProgressBar> = None;
    let mut progress_state = String::new();
    let mut scenario_title: String = "".to_string();

    loop {
        tokio::select! {
            scenario_event = scenario_event_receiver.recv() => {
                match scenario_event {
                    Ok(event) => {
                        match event {
                            ScenarioEventPhase::ItemStarted{ id: _, url, item } => {
                                let mut runs_on = "".to_string();
                                #[cfg(feature = "discovery")]
                                {
                                    if let Some(platform) = item.context.runs_on {
                                        match platform {
                                            scenario::types::ScenarioItemRunsOn::Kubernetes { ns, service, .. } => {
                                                runs_on = format!("{}", format!("[k8s: {}/{}] ", ns.yellow(), service.magenta()).dim())
                                            },
                                        }
                                    }
                                }
                                match progress {
                                    Some(ref pb) => {
                                        pb.inc(1);
                                        pb.set_message(format!(
                                            "{} {}{} {}{}",
                                            scenario_title.clone().bold(),
                                            progress_state,
                                            "▮".to_string().dim().blink(),
                                            runs_on,
                                            format!("[{} {}]", item.call.method.light_yellow(), url.blue()).bold(),
                                        ))
                                    }
                                    None => {}
                                };
                            },
                            ScenarioEventPhase::ItemTerminated { id: _, method, url, expectation } => {
                                match expectation {
                                    Some(ItemExpectation::Http { wanted: _, got }) => {
                                        match got {
                                            Some(status) => {
                                                if status.decision == ItemExpectationDecision::Failure {
                                                    progress_state = format!("{}{}", progress_state, "▮".to_string().red());
                                                } else if status.decision == ItemExpectationDecision::Success {
                                                    progress_state = format!("{}{}", progress_state, "▮".to_string().green());
                                                } else {
                                                    progress_state = format!("{}{}", progress_state, "▮".to_string().green().dim());
                                                }
                                            },
                                            None => progress_state = format!("{}{}", progress_state, "▮".to_string().green().dim())
                                        }
                                    },
                                    None => {
                                        progress_state = format!("{}{}", progress_state, "▮".to_string().green().dim())
                                    }
                                }

                                match progress {
                                    Some(ref pb) => pb.set_message(format!("{}", format!(
                                        "{} {} [{}]",
                                        scenario_title.clone(),
                                        progress_state,
                                        format!("{} {}", method.yellow(), url.light_blue())
                                    ).dim())),
                                    None => {}
                                };
                            }
                            ScenarioEventPhase::Started { id: _, scenario } => {
                                let n = scenario::count_scenario_items(&scenario);

                                let title = scenario.title;
                                scenario_title = title.clone();

                                let pb = m.add(ProgressBar::new(n));
                                pb.enable_steady_tick(Duration::from_millis(80));
                                pb.set_style(
                                    ProgressStyle::with_template(
                                        "{spinner:.green} {pos:>2}/{len:2} [{elapsed_precise:.dim}] {msg}",
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

                                progress = Some(pb);
                            }
                            ScenarioEventPhase::Terminated { id: _ } => {
                                match progress {
                                    Some(ref pb) => {pb.finish()}
                                    None => {}
                                };

                                break;
                            }
                        }
                    }
                    Err(broadcast::error::RecvError::Closed) => {
                        break;
                    }
                    Err(broadcast::error::RecvError::Lagged(count)) => {
                        tracing::warn!("Missed {} scenario messages", count);
                    }
                }
            }
        }
    }

    if let Some(pb) = progress {
        if !pb.is_finished() {
            pb.finish();
        }
    }
}
