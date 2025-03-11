use std::collections::HashMap;
use std::time::Duration;
use std::time::Instant;

use colorful::Color;
use colorful::Colorful;
use colorful::ExtraColorInterface;
use colorful::core::color_string::CString;
use indicatif::MultiProgress;
use indicatif::ProgressBar;
use indicatif::ProgressStyle;
use tokio::sync::broadcast;
use tokio::sync::broadcast::Receiver;

use crate::event::FaultEvent;
use crate::event::TaskId;
use crate::event::TaskProgressEvent;
use crate::types::Direction;

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

/// Handles displayable events and updates the progress bars accordingly
pub async fn handle_displayable_events(
    mut receiver: Receiver<TaskProgressEvent>,
) {
    let multi = MultiProgress::new();

    let style = ProgressStyle::default_bar()
        .template("{spinner:.green} {msg}")
        .unwrap()
        .tick_strings(&["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]) // Cus
        .progress_chars("=> ");

    let mut task_map: HashMap<TaskId, TaskInfo> = HashMap::new();

    loop {
        tokio::select! {
            event = receiver.recv() => {
                match event {
                    Ok(event) => {
                        match event {
                            TaskProgressEvent::Started { id, ts, url } => {
                                let pb = multi.add(ProgressBar::new_spinner());
                                pb.set_style(style.clone());
                                pb.enable_steady_tick(Duration::from_millis(80));

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

                                    tracing::debug!("With fault {}", f);
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
                                    task_info.events.push(fault.clone());
                                    let mut fault_results = String::new();

                                    for fault in task_info.faults.clone() {
                                        if let FaultEvent::Latency { direction, side, delay: _ } = &fault {
                                            let max_events = 20;

                                            let sparkline: String = task_info.events.iter()
                                                .filter_map(|f| {
                                                    if let FaultEvent::Latency { direction: _, side: _, delay: Some(d) } = f {
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
                                            fault_results.push_str(&format!("{} {}{: <28}", format!("{} latency", side).yellow(), direction_character(direction.clone()), &sparkline));
                                        } else if let FaultEvent::Bandwidth { direction, side, bps: _ } = &fault {

                                            let count = task_info.events.len();
                                            let mut bandwidth = 0;
                                            if count > 0 {
                                                let total: usize = task_info.events.iter()
                                                .map(|f| {
                                                    if let FaultEvent::Bandwidth { direction: _, side: _, bps: Some(d) } = f {
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

                                            let formatted_rate = format!("{}{}", direction_character(direction.clone()), format_bandwidth(bandwidth));
                                            fault_results.push_str(&format!(" {} {}", format!("{} bandwidth", side).yellow(), &formatted_rate));
                                        } else if let FaultEvent::PacketLoss {state, direction: _, side} = &fault {
                                            let formatted_rate = "".to_string();
                                            fault_results.push_str(&format!(" {} {}", format!("{} packet loss ({})", side, state).yellow(), &formatted_rate));
                                        }

                                        fault_results.push_str("");
                                    }
                                    tracing::debug!("{}", fault_results);
                                    let u = format!("{} {}", "URL:".dim(), task_info.url.clone().light_blue());
                                    let d = format!("{} {:.3}ms", "DNS:".dim(), task_info.resolution_time);
                                    task_info.pb.set_message(format!("{} | {} | {} | ...", u, d, fault_results));
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

                                    for fault in task_info.faults.clone() {
                                        if let FaultEvent::Latency { direction, side, delay: _ } = &fault {
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
                                            fault_results.push_str(&format!("{} {}{} ", format!("{} latency", side).yellow(), "".to_string(), &sparkline));
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

                                            fault_results.push_str(&format!("{} {:.3}ms", format!("{} {} latency", side, direction).yellow(), latency));
                                        } else if let FaultEvent::Bandwidth { direction: _, side, bps: _ } = &fault {

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

                                            let formatted_rate = format!("{}{}", "", format_bandwidth(bandwidth));
                                            fault_results.push_str(&format!(" {} {}", format!("{} bandwidth", side).yellow(), &formatted_rate));
                                        } else if let FaultEvent::PacketLoss {state, direction: _, side} = &fault {
                                            let formatted_rate = "".to_string();
                                            fault_results.push_str(&format!(" {} {}", format!("{} packet loss ({})", side, state).yellow(), &formatted_rate));
                                        }

                                        fault_results.push_str("");
                                    }

                                    let ttfb = match task_info.ttfb {
                                        Some(d) => format!("{:.3}", d.as_millis_f64()),
                                        None => "-".to_string()
                                    };

                                    let h = format!(
                                        "{} {:.3}ms | {} {}ms | {} ⭫{}/b ⭭{}/b",
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
                    Err(broadcast::error::RecvError::Closed) => {
                        break;
                    }
                    Err(broadcast::error::RecvError::Lagged(count)) => {
                        tracing::debug!("Missed {} events that couldn't be part of the output", count);
                    }
                }
            }
        }
    }

    // Clear the MultiProgress once all tasks are done
    multi.clear().unwrap();
}

fn fault_to_string(faults: &Vec<FaultEvent>) -> String {
    let mut b = Vec::new();

    for fault in faults {
        let f = match fault {
            FaultEvent::Latency { direction: _, side, delay: _ } => {
                format!("{} latency", side)
            }
            FaultEvent::Dns { direction: _, side, triggered: _ } => {
                format!("{} dns", side)
            }
            FaultEvent::Bandwidth { direction: _, side, bps: _ } => {
                format!("{} bandwidth", side)
            }
            FaultEvent::Jitter {
                direction: _,
                side,
                amplitude: _,
                frequency: _,
            } => {
                format!("{} jitter", side)
            }
            FaultEvent::PacketLoss { state: _, direction: _, side } => {
                format!("{} packet loss", side)
            }
            FaultEvent::HttpResponseFault {
                direction: _,
                side,
                status_code: _,
                response_body: _,
            } => format!("{} http error", side),
        };
        b.push(f);
    }

    b.join(", ")
}

/// Maps a latency duration to a colored Unicode character for the sparkline.
/// The mapping is based on latency thresholds in milliseconds.
fn latency_to_sparkline_char(latency: Duration) -> CString {
    let millis = latency.as_secs_f64() * 1000.0;

    if millis < 50.0 {
        '▁'.to_string().green()
    } else if millis < 100.0 {
        '▂'.to_string().green()
    } else if millis < 200.0 {
        '▃'.to_string().yellow()
    } else if millis < 400.0 {
        '▄'.to_string().yellow()
    } else if millis < 800.0 {
        '▅'.to_string().red()
    } else {
        '▆'.to_string().red()
    }
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

fn direction_character(direction: Direction) -> String {
    match direction {
        Direction::Ingress => "⭭".to_string(),
        Direction::Egress => "⭫".to_string(),
        Direction::Both => "⭭⭫".to_string(),
    }
}


pub async fn quiet_handle_displayable_events(
    mut receiver: Receiver<TaskProgressEvent>,
) {
    loop {
        tokio::select! {
            event = receiver.recv() => {
                match event {
                    Ok(_) => {}
                    Err(broadcast::error::RecvError::Closed) => {
                        break;
                    }
                    Err(broadcast::error::RecvError::Lagged(count)) => {
                    }
                }
            }
        }
    }
}
