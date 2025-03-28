use std::sync::Arc;
use std::time::Duration;

use anyhow::Result;
use anyhow::anyhow;
use parse_duration::parse;
use tokio::sync::watch;
use tokio::time::Instant;
use tokio::time::sleep_until;

use crate::AppState;
use crate::cli::RunCommandOptions;
use crate::config::FaultConfig;
use crate::config::FaultKind;
use crate::config::ProxyConfig;
use crate::errors::SchedulingError;
use crate::event::FaultEvent;
use crate::proxy::ProxyState;
use crate::types::FaultPeriod;
use crate::types::FaultPeriodSpec;
use crate::types::TimeSpec; // from the 'parse_duration' crate

fn fraction_to_duration(frac: f64, total: Duration) -> Duration {
    let secs = total.as_secs_f64() * frac;
    Duration::from_secs_f64(secs)
}

fn parse_time_spec(s: &str) -> Result<TimeSpec, SchedulingError> {
    let s = s.trim();
    if s.ends_with('%') {
        // e.g. "5%"
        let pct_str = &s[..s.len() - 1]; // remove '%'
        let fraction = pct_str
            .parse::<f64>()
            .map_err(|_| SchedulingError::InvalidFraction(s.to_string()))?
            / 100.0;
        Ok(TimeSpec::Fraction(fraction))
    } else {
        // Try parse as e.g. "30s" or "5m" or "45"
        // parse returns an error if it can't parse,
        // so we fallback to a plain integer check.
        match parse(s) {
            Ok(d) => Ok(TimeSpec::Absolute(d)),
            Err(_) => {
                // Maybe it's a bare integer => seconds
                if let Ok(secs) = s.parse::<u64>() {
                    Ok(TimeSpec::Absolute(Duration::from_secs(secs)))
                } else {
                    Err(SchedulingError::FailedParsing(s.to_string()))
                }
            }
        }
    }
}

/// Parse a DSL string with multiple periods separated by `;`,
/// each with "start:..., duration:..." pairs separated by `,`.
fn parse_periods(s: &str) -> Result<Vec<FaultPeriodSpec>, SchedulingError> {
    let mut specs = Vec::new();

    for part in s.split(';') {
        let part = part.trim();
        if part.is_empty() {
            continue;
        }
        let mut start_spec: Option<TimeSpec> = None;
        let mut duration_spec: Option<TimeSpec> = None;

        for kv in part.split(',') {
            let kv = kv.trim();
            if kv.is_empty() {
                continue;
            }
            // e.g. "start:5%" or "duration:25%"
            let mut iter = kv.splitn(2, ':');
            let key = iter.next().unwrap();
            let val = iter.next().unwrap_or("").trim();

            match key {
                "start" => {
                    start_spec = Some(parse_time_spec(val)?);
                }
                "duration" => {
                    duration_spec = Some(parse_time_spec(val)?);
                }
                k => {
                    return Err(SchedulingError::UnknownKey(k.to_string()));
                }
            }
        }

        // If no "start" was given, default to 0
        let start = start_spec
            .unwrap_or_else(|| TimeSpec::Absolute(Duration::from_secs(0)));
        specs.push(FaultPeriodSpec { start, duration: duration_spec });
    }

    Ok(specs)
}

/// Convert the parse result (FaultPeriodSpec) into final (FaultPeriod).
/// If we see a `Fraction` but `total_run_time` is None, we fail.
fn resolve_periods(
    specs: &[FaultPeriodSpec],
    total_run_time: Option<Duration>,
) -> Result<Vec<FaultPeriod>, SchedulingError> {
    let mut output = Vec::new();

    for s in specs {
        let start = match &s.start {
            TimeSpec::Absolute(d) => *d,
            TimeSpec::Fraction(f) => {
                if let Some(total) = total_run_time {
                    fraction_to_duration(*f, total)
                } else {
                    return Err(SchedulingError::MissingDuration(format!(
                        "{}%",
                        f * 100.0
                    )));
                }
            }
        };

        let duration_opt = match &s.duration {
            Some(TimeSpec::Absolute(d)) => Some(*d),
            Some(TimeSpec::Fraction(f)) => {
                if let Some(total) = total_run_time {
                    Some(fraction_to_duration(*f, total))
                } else {
                    return Err(SchedulingError::MissingDuration(format!(
                        "{}%",
                        f * 100.0
                    )));
                }
            }
            None => None,
        };

        output.push(FaultPeriod { start, duration: duration_opt });
    }

    Ok(output)
}

fn build_events_for_fault(
    fault_type: FaultKind,
    fault_config: FaultConfig,
    periods: &[FaultPeriod],
    base_instant: Instant,
) -> Vec<FaultPeriodEvent> {
    let mut events = Vec::new();

    for p in periods {
        let start_time = base_instant + p.start;
        events.push(FaultPeriodEvent {
            time: start_time,
            fault_type: fault_type.clone(),
            fault_config: fault_config.clone(),
            event_type: EventType::Start,
        });

        if let Some(d) = p.duration {
            events.push(FaultPeriodEvent {
                time: start_time + d,
                fault_type: fault_type.clone(),
                fault_config: fault_config.clone(),
                event_type: EventType::Stop,
            });
        }
    }

    events
}

pub async fn run_fault_schedule(
    mut events: Vec<FaultPeriodEvent>,
    state: Arc<ProxyState>,
) {
    tracing::debug!("Fault events: {}", events.len());

    events.sort_by_key(|e| e.time);

    for event in events {
        let now = Instant::now();
        if event.time > now {
            sleep_until(event.time).await;
        }

        match event.event_type {
            EventType::Start => {
                state.enable_fault(event.fault_type, event.fault_config).await;
            }
            EventType::Stop => {
                state.disable_fault(event.fault_type, event.fault_config).await;
            }
        }
    }
}

/// Whether we are starting or stopping that fault
#[derive(Debug, Clone, PartialEq)]
pub enum EventType {
    Start,
    Stop,
}

#[derive(Debug, Clone)]
pub struct FaultPeriodEvent {
    pub time: Instant,
    pub fault_type: FaultKind,
    pub fault_config: FaultConfig,
    pub event_type: EventType,
}

pub fn build_schedule_events(
    cli: &RunCommandOptions,
    total_duration: Option<Duration>,
) -> Result<Vec<FaultPeriodEvent>> {
    let mut events: Vec<FaultPeriodEvent> = Vec::<FaultPeriodEvent>::new();

    let start = Instant::now();

    if cli.bandwidth.enabled {
        let period = match &cli.bandwidth.bandwidth_sched {
            Some(p) => p,
            None => match total_duration {
                Some(_) => "duration:100%",
                None => "",
            },
        };

        if !period.is_empty() {
            let specs = parse_periods(&period)?;
            let periods = resolve_periods(&specs, total_duration)?;
            let fault_config = FaultConfig::Bandwidth((&cli.bandwidth).into());
            let fault_events = build_events_for_fault(
                FaultKind::Bandwidth,
                fault_config,
                &periods,
                start,
            );

            events.extend(fault_events);
        }
    }

    if cli.latency.enabled {
        let period = match &cli.latency.latency_sched {
            Some(p) => p,
            None => match total_duration {
                Some(_) => "duration:100%",
                None => "",
            },
        };

        if !period.is_empty() {
            let specs = parse_periods(&period)?;
            let periods = resolve_periods(&specs, total_duration)?;
            let fault_config = FaultConfig::Latency((&cli.latency).into());
            let fault_events = build_events_for_fault(
                FaultKind::Latency,
                fault_config,
                &periods,
                start,
            );

            events.extend(fault_events);
        }
    }

    if cli.dns.enabled {
        let period = match &cli.dns.dns_sched {
            Some(p) => p,
            None => match total_duration {
                Some(_) => "duration:100%",
                None => "",
            },
        };

        if !period.is_empty() {
            let specs = parse_periods(&period)?;
            let periods = resolve_periods(&specs, total_duration)?;
            let fault_config = FaultConfig::Dns((&cli.dns).into());
            let fault_events = build_events_for_fault(
                FaultKind::Dns,
                fault_config,
                &periods,
                start,
            );

            events.extend(fault_events);
        }
    }

    if cli.packet_loss.enabled {
        let period = match &cli.packet_loss.packet_loss_sched {
            Some(p) => p,
            None => match total_duration {
                Some(_) => "duration:100%",
                None => "",
            },
        };

        if !period.is_empty() {
            let specs = parse_periods(&period)?;
            let periods = resolve_periods(&specs, total_duration)?;
            let fault_config =
                FaultConfig::PacketLoss((&cli.packet_loss).into());
            let fault_events = build_events_for_fault(
                FaultKind::PacketLoss,
                fault_config,
                &periods,
                start,
            );

            events.extend(fault_events);
        }
    }

    if cli.jitter.enabled {
        let period = match &cli.jitter.jitter_sched {
            Some(p) => p,
            None => match total_duration {
                Some(_) => "duration:100%",
                None => "",
            },
        };

        if !period.is_empty() {
            let specs = parse_periods(&period)?;
            let periods = resolve_periods(&specs, total_duration)?;
            let fault_config = FaultConfig::Jitter((&cli.jitter).into());
            let fault_events = build_events_for_fault(
                FaultKind::Jitter,
                fault_config,
                &periods,
                start,
            );

            events.extend(fault_events);
        }
    }

    if cli.http_error.enabled {
        let period = match &cli.http_error.http_response_sched {
            Some(p) => p,
            None => match total_duration {
                Some(_) => "duration:100%",
                None => "",
            },
        };

        if !period.is_empty() {
            let specs = parse_periods(&period)?;
            let periods = resolve_periods(&specs, total_duration)?;
            let fault_config = FaultConfig::HttpError((&cli.http_error).into());
            let fault_events = build_events_for_fault(
                FaultKind::HttpError,
                fault_config,
                &periods,
                start,
            );

            events.extend(fault_events);
        }
    }

    if cli.blackhole.enabled {
        let period = match &cli.blackhole.blackhole_sched {
            Some(p) => p,
            None => match total_duration {
                Some(_) => "duration:100%",
                None => "",
            },
        };

        if !period.is_empty() {
            let specs = parse_periods(&period)?;
            let periods = resolve_periods(&specs, total_duration)?;
            let fault_config = FaultConfig::Blackhole((&cli.blackhole).into());
            let fault_events = build_events_for_fault(
                FaultKind::Blackhole,
                fault_config,
                &periods,
                start,
            );

            events.extend(fault_events);
        }
    }

    Ok(events)
}
