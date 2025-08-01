use std::sync::Arc;
use std::time::Duration;

use anyhow::Result;
use parse_duration::parse;
use tokio::time::Instant;
use tokio::time::sleep_until;

use crate::cli::RunCommonOptions;
use crate::config::FaultConfig;
use crate::config::FaultKind;
use crate::errors::SchedulingError;
use crate::fault::FaultInjector;
use crate::plugin::load_injector;
use crate::proxy::ProxyState;
use crate::types::FaultConfiguration;
use crate::types::FaultPeriod;
use crate::types::FaultPeriodSpec;
use crate::types::TimeSpec; // from the 'parse_duration' crate

fn fraction_to_duration(frac: f64, total: Duration) -> Duration {
    let secs = total.as_secs_f64() * frac;
    Duration::from_secs_f64(secs)
}

fn parse_time_spec(s: &str) -> Result<TimeSpec, SchedulingError> {
    let s = s.trim();
    if let Some(pct_str) = s.strip_suffix('%') {
        // e.g. "5%"
        // remove '%'
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

pub fn parse_period(period: &str) -> Result<Option<FaultPeriodSpec>> {
    match parse_periods(period) {
        Ok(periods) => {
            if periods.is_empty() {
                Ok(None)
            } else {
                Ok(Some(periods[0].clone()))
            }
        }
        Err(_) => Ok(None),
    }
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
            fault_type,
            fault_config: fault_config.clone(),
            event_type: EventType::Start,
        });

        if let Some(d) = p.duration {
            events.push(FaultPeriodEvent {
                time: start_time + d,
                fault_type,
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
    injectors: Vec<Box<dyn FaultInjector>>,
) {
    events.sort_by_key(|e| e.time);

    for event in events {
        let mut injectors = injectors.clone();

        let now = Instant::now();
        if event.time > now {
            sleep_until(event.time).await;
        }

        let fault_config = event.fault_config;
        let fault_type = fault_config.kind();

        match event.event_type {
            EventType::Start => {
                if let Some(existing_injector) =
                    injectors.iter_mut().find(|f| f.kind() == fault_type)
                {
                    existing_injector.enable();
                } else {
                    let mut injector = load_injector(&fault_config);
                    injector.enable();
                    injectors.push(injector);
                }
            }
            EventType::Stop => {
                if let Some(existing_injector) =
                    injectors.iter_mut().find(|f| f.kind() == fault_type)
                {
                    existing_injector.disable();
                }
            }
        }

        state.set_injectors(injectors).await;
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
    cli: &RunCommonOptions,
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
            let specs = parse_periods(period)?;
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
            let specs = parse_periods(period)?;
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
            let specs = parse_periods(period)?;
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
            let specs = parse_periods(period)?;
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
            let specs = parse_periods(period)?;
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
            let specs = parse_periods(period)?;
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
            let specs = parse_periods(period)?;
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

pub fn build_schedule_events_from_scenario_item(
    faults: &Vec<FaultConfiguration>,
    starting_point: Instant,
    total_duration: Duration,
) -> Vec<FaultPeriodEvent> {
    let mut events: Vec<FaultPeriodEvent> = Vec::<FaultPeriodEvent>::new();

    let total_run = Some(total_duration);

    for f in faults {
        let p = f.get_period();

        let mut periods = Vec::new();

        if let Some(period) = p {
            // these expect() shouldn't happen because at this point, we have
            // already parsed the period spec
            periods.extend(
                resolve_periods(&[period.clone()], total_run)
                    .expect("failed to resolve period"),
            );
        } else {
            periods.push(FaultPeriod {
                start: Duration::from_millis(0),
                duration: None,
            });
        }

        let fault_config = f.build().expect("invalid fault config");
        let fault_events = build_events_for_fault(
            fault_config.kind(),
            fault_config,
            periods.as_ref(),
            starting_point,
        );

        events.extend(fault_events);
    }

    events
}
