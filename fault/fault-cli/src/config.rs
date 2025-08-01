use std::fmt;
use std::sync::Arc;
use std::time::Duration;

use arc_swap::ArcSwap;
use serde::Deserialize;
use serde::Serialize;

use crate::cli::BandwidthOptions;
use crate::cli::BlackholeOptions;
use crate::cli::DbOptions;
use crate::cli::DnsOptions;
use crate::cli::HTTPResponseOptions;
use crate::cli::JitterOptions;
use crate::cli::LatencyOptions;
use crate::cli::LlmOptions;
//use crate::cli::PacketDuplicationOptions;
use crate::cli::PacketLossOptions;
use crate::cli::RunCommonOptions;
use crate::fault::content::ContentInjectSettings;
use crate::fault::llm::openai::OpenAiInjector;
use crate::fault::llm::openai::OpenAiSettings;
use crate::fault::llm::openai::SlowStreamSettings;
use crate::types::BandwidthUnit;
use crate::types::DbCase;
use crate::types::Direction;
use crate::types::LatencyDistribution;
use crate::types::LlmCase;
use crate::types::ProtocolType;
use crate::types::StreamSide;

/// Internal Configuration for Latency Fault
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct LatencySettings {
    pub kind: FaultKind,
    pub enabled: bool,
    pub distribution: LatencyDistribution,
    pub direction: Direction,
    pub global: bool,
    pub side: StreamSide,
    pub latency_mean: f64,
    pub latency_stddev: f64,
    pub latency_shape: f64,
    pub latency_scale: f64,
    pub latency_min: f64,
    pub latency_max: f64,
}

/// Internal Configuration for Packet Loss Fault
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct PacketLossSettings {
    pub kind: FaultKind,
    pub enabled: bool,
    pub direction: Direction,
    pub side: StreamSide,
}

/// Internal Configuration for Bandwidth Throttling Fault
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct BandwidthSettings {
    pub kind: FaultKind,
    pub enabled: bool,
    pub direction: Direction,
    pub side: StreamSide,
    pub bandwidth_rate: usize, // in bytes per second
    pub bandwidth_unit: BandwidthUnit,
}

/// Internal Configuration for Jitter Fault
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct JitterSettings {
    pub kind: FaultKind,
    pub enabled: bool,
    pub direction: Direction,
    pub side: StreamSide,
    pub amplitude: f64, // in milliseconds
    pub frequency: f64, // in Hertz
}

/// Internal Configuration for DNS Fault
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct DnsSettings {
    pub kind: FaultKind,
    pub enabled: bool,
    pub rate: f64, // between 0 and 1.0
}

/// Internal Configuration for Packet Duplication Fault
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct PacketDuplicationSettings {
    pub kind: FaultKind,
    pub enabled: bool,
    pub direction: Direction,
    pub packet_duplication_probability: f64, // between 0.0 and 1.0
}

/// Internal Configuration for HTTP Error Fault
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct HttpResponseSettings {
    pub kind: FaultKind,
    pub enabled: bool,
    pub http_response_status_code: u16,
    pub http_response_body: Option<String>,
    pub http_response_trigger_probability: f64, // between 0.0 and 1.0
}

/// Internal Configuration for Blackhole Fault
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct BlackholeSettings {
    pub enabled: bool,
    pub side: StreamSide,
    pub direction: Direction,
    pub kind: FaultKind,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
pub struct GrpcCapabilities {
    pub forward: bool,
    pub tunnel: bool,
    pub protocols: Vec<ProtocolType>,
}

/// Internal Configuration for Grpc plugins
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct GrpcSettings {
    pub name: String,
    pub kind: FaultKind,
    pub enabled: bool,
    pub direction: Direction,
    pub side: StreamSide,
    pub capabilities: Option<GrpcCapabilities>,
}

/// Internal Configuration for Llm faults
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct LlmSettings {}

/// Fault Configuration Enum
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub enum FaultConfig {
    // network
    Dns(DnsSettings),
    Latency(LatencySettings),
    PacketLoss(PacketLossSettings),
    Bandwidth(BandwidthSettings),
    Jitter(JitterSettings),
    PacketDuplication(PacketDuplicationSettings),
    HttpError(HttpResponseSettings),
    Blackhole(BlackholeSettings),

    // llm
    SlowStream(SlowStreamSettings),
    PromptScramble(OpenAiSettings),
    InjectBias(OpenAiSettings),
    TruncateResponse(OpenAiSettings),
}

/// Implement Default manually for FaultConfig
impl Default for FaultConfig {
    fn default() -> Self {
        FaultConfig::Latency(LatencySettings::default())
    }
}

impl fmt::Display for FaultConfig {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            FaultConfig::Dns(_) => write!(f, "dns"),
            FaultConfig::Latency(_) => write!(f, "latency"),
            FaultConfig::PacketLoss(_) => write!(f, "packet-loss"),
            FaultConfig::Bandwidth(_) => write!(f, "bandwidth"),
            FaultConfig::Jitter(_) => write!(f, "jitter"),
            FaultConfig::PacketDuplication(_) => {
                write!(f, "packet-duplication")
            }
            FaultConfig::HttpError(_) => write!(f, "http-error"),
            FaultConfig::Blackhole(_) => write!(f, "blackhole"),
            FaultConfig::PromptScramble(_) => write!(f, "llm-prompt-scramble"),
            FaultConfig::InjectBias(_) => write!(f, "llm-inject-bias"),
            FaultConfig::TruncateResponse(_) => {
                write!(f, "llm-truncate-response")
            }
            FaultConfig::SlowStream(_) => write!(f, "llm-slow-stream"),
        }
    }
}

impl FaultConfig {
    pub fn kind(&self) -> FaultKind {
        match self {
            FaultConfig::Dns(_) => FaultKind::Dns,
            FaultConfig::Latency(_) => FaultKind::Latency,
            FaultConfig::PacketLoss(_) => FaultKind::PacketLoss,
            FaultConfig::Bandwidth(_) => FaultKind::Bandwidth,
            FaultConfig::Jitter(_) => FaultKind::Jitter,
            FaultConfig::PacketDuplication(_) => FaultKind::PacketDuplication,
            FaultConfig::HttpError(_) => FaultKind::HttpError,
            FaultConfig::Blackhole(_) => FaultKind::Blackhole,
            FaultConfig::PromptScramble(_) => FaultKind::PromptScramble,
            FaultConfig::InjectBias(_) => FaultKind::InjectBias,
            FaultConfig::TruncateResponse(_) => FaultKind::TruncateResponse,
            FaultConfig::SlowStream(_) => FaultKind::SlowStream,
        }
    }
}

#[derive(
    Default, Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, Hash,
)]
pub enum FaultKind {
    #[default]
    Unknown,

    // network
    Dns,
    Latency,
    PacketLoss,
    Bandwidth,
    Jitter,
    PacketDuplication,
    HttpError,
    Blackhole,
    Metrics,
    Grpc,

    // llm
    SlowStream,
    PromptScramble,
    InjectBias,
    TruncateResponse,
}

impl fmt::Display for FaultKind {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            FaultKind::Unknown => write!(f, "unknown"),
            FaultKind::Dns => write!(f, "dns"),
            FaultKind::Latency => write!(f, "latency"),
            FaultKind::PacketLoss => write!(f, "packet-loss"),
            FaultKind::Bandwidth => write!(f, "bandwidth"),
            FaultKind::Jitter => write!(f, "jitter"),
            FaultKind::PacketDuplication => write!(f, "packet-duplication"),
            FaultKind::HttpError => write!(f, "http-error"),
            FaultKind::Blackhole => write!(f, "blackhole"),
            FaultKind::Metrics => write!(f, "metrics"),
            FaultKind::Grpc => write!(f, "grpc"),
            FaultKind::PromptScramble => write!(f, "prompt-scramble"),
            FaultKind::InjectBias => write!(f, "inject-bias"),
            FaultKind::TruncateResponse => write!(f, "truncate-response"),
            FaultKind::SlowStream => write!(f, "slow-stream"),
        }
    }
}

/// Proxy Configuration Struct
#[derive(Clone, Debug, Default)]
pub struct ProxyConfig {
    pub faults: Arc<ArcSwap<Vec<FaultConfig>>>,
}

impl ProxyConfig {
    pub fn add(&self, faults: Vec<FaultConfig>) {
        let current = self.faults.load_full();
        let mut vec = (*current).clone();
        vec.extend(faults);
        self.faults.store(Arc::new(vec.to_vec()));
    }
}

impl From<RunCommonOptions> for ProxyConfig {
    fn from(cli: RunCommonOptions) -> Self {
        let mut faults = Vec::new();

        if cli.latency.enabled && cli.latency.latency_sched.is_none() {
            faults.push(FaultConfig::Latency((&cli.latency).into()));
        }

        if cli.bandwidth.enabled && cli.bandwidth.bandwidth_sched.is_none() {
            faults.push(FaultConfig::Bandwidth((&cli.bandwidth).into()));
        }

        if cli.dns.enabled && cli.dns.dns_sched.is_none() {
            faults.push(FaultConfig::Dns((&cli.dns).into()));
        }

        if cli.jitter.enabled && cli.jitter.jitter_sched.is_none() {
            faults.push(FaultConfig::Jitter((&cli.jitter).into()));
        }

        if cli.packet_loss.enabled
            && cli.packet_loss.packet_loss_sched.is_none()
        {
            faults.push(FaultConfig::PacketLoss((&cli.packet_loss).into()));
        }

        /*
        if cli.packet_duplication.enabled {
            faults.push(FaultConfig::PacketDuplication(
                (&cli.packet_duplication).into(),
            ));
        }
        */

        if cli.http_error.enabled
            && cli.http_error.http_response_sched.is_none()
        {
            faults.push(FaultConfig::HttpError((&cli.http_error).into()));
        }

        if cli.blackhole.enabled && cli.blackhole.blackhole_sched.is_none() {
            faults.push(FaultConfig::Blackhole((&cli.blackhole).into()));
        }

        ProxyConfig { faults: Arc::new(ArcSwap::from_pointee(faults)) }
    }
}

impl From<&LatencyOptions> for LatencySettings {
    fn from(cli: &LatencyOptions) -> Self {
        LatencySettings {
            enabled: cli.enabled,
            kind: FaultKind::Latency,
            distribution: cli.latency_distribution.clone(),
            direction: cli.latency_direction.clone(),
            global: !cli.per_read_write,
            side: cli.side.clone(),
            latency_mean: cli.latency_mean.unwrap_or(0.0),
            latency_stddev: cli.latency_stddev.unwrap_or(0.0),
            latency_shape: cli.latency_shape.unwrap_or(0.0),
            latency_scale: cli.latency_scale.unwrap_or(0.0),
            latency_min: cli.latency_min.unwrap_or(0.0),
            latency_max: cli.latency_max.unwrap_or(0.0),
        }
    }
}

impl From<&BandwidthOptions> for BandwidthSettings {
    fn from(cli: &BandwidthOptions) -> Self {
        BandwidthSettings {
            enabled: cli.enabled,
            kind: FaultKind::Bandwidth,
            direction: cli.bandwidth_direction.clone(),
            side: cli.side.clone(),
            bandwidth_rate: cli.bandwidth_rate,
            bandwidth_unit: cli.bandwidth_unit,
        }
    }
}

impl From<&JitterOptions> for JitterSettings {
    fn from(cli: &JitterOptions) -> Self {
        JitterSettings {
            enabled: cli.enabled,
            kind: FaultKind::Jitter,
            direction: cli.jitter_direction.clone(),
            amplitude: cli.jitter_amplitude,
            frequency: cli.jitter_frequency,
            side: cli.jitter_side.clone(),
        }
    }
}

impl From<&DnsOptions> for DnsSettings {
    fn from(cli: &DnsOptions) -> Self {
        DnsSettings {
            enabled: cli.enabled,
            kind: FaultKind::Dns,
            rate: cli.dns_rate,
        }
    }
}

impl From<&PacketLossOptions> for PacketLossSettings {
    fn from(cli: &PacketLossOptions) -> Self {
        PacketLossSettings {
            enabled: cli.enabled,
            kind: FaultKind::PacketLoss,
            direction: cli.packet_loss_direction.clone(),
            side: cli.side.clone(),
        }
    }
}

impl From<&BlackholeOptions> for BlackholeSettings {
    fn from(cli: &BlackholeOptions) -> Self {
        BlackholeSettings {
            enabled: cli.enabled,
            kind: FaultKind::Blackhole,
            direction: cli.blackhole_direction.clone(),
            side: cli.side.clone(),
        }
    }
}

/*
impl From<&PacketDuplicationOptions> for PacketDuplicationSettings {
    fn from(cli: &PacketDuplicationOptions) -> Self {
        PacketDuplicationSettings {
            direction: cli.packet_duplication_direction.clone(),
            packet_duplication_probability: cli.packet_duplication_probability,
        }
    }
}
*/
impl From<&HTTPResponseOptions> for HttpResponseSettings {
    fn from(cli: &HTTPResponseOptions) -> Self {
        HttpResponseSettings {
            enabled: cli.enabled,
            kind: FaultKind::HttpError,
            http_response_status_code: cli.http_response_status_code,
            http_response_body: cli.http_response_body.clone(),
            http_response_trigger_probability: cli
                .http_response_trigger_probability,
        }
    }
}

impl From<(LlmCase, &LlmOptions)> for FaultConfig {
    fn from((case, options): (LlmCase, &LlmOptions)) -> Self {
        match case {
            LlmCase::SlowStream => {
                FaultConfig::SlowStream(SlowStreamSettings {
                    mean_ms: options.slow_stream_mean_delay.unwrap_or(50.0),
                    stddev_ms: Some(0.0),
                    probability: options.probability,
                    kind: FaultKind::SlowStream,
                    side: StreamSide::Server,
                    direction: Direction::Egress,
                })
            }
            LlmCase::TokenDrop => FaultConfig::PacketLoss(PacketLossSettings {
                enabled: true,
                kind: FaultKind::PacketLoss,
                direction: Direction::Both,
                side: StreamSide::Server,
            }),
            LlmCase::PromptScramble => {
                let s = OpenAiSettings {
                    case: LlmCase::PromptScramble,
                    pattern: None,
                    replacement: None,
                    instruction: options.instruction.clone(),
                    probability: options.probability,
                    kind: FaultKind::PromptScramble,
                    direction: Direction::Egress,
                    side: StreamSide::Client,
                };
                FaultConfig::PromptScramble(s)
            }

            LlmCase::InjectBias => {
                let s = OpenAiSettings {
                    case: LlmCase::InjectBias,
                    pattern: options.bias_pattern.clone(),
                    replacement: options.bias_replacement.clone(),
                    instruction: None,
                    probability: options.probability,
                    kind: FaultKind::InjectBias,
                    direction: Direction::Ingress,
                    side: StreamSide::Client,
                };
                FaultConfig::InjectBias(s)
            }

            LlmCase::TruncateResponse => {
                let s = OpenAiSettings {
                    case: LlmCase::TruncateResponse,
                    pattern: options.scramble_pattern.clone(),
                    replacement: options.scramble_with.clone(),
                    instruction: None,
                    probability: options.probability,
                    kind: FaultKind::TruncateResponse,
                    direction: Direction::Ingress,
                    side: StreamSide::Client,
                };
                FaultConfig::TruncateResponse(s)
            }

            LlmCase::HttpError => {
                // your existing HTTP‐error injection
                FaultConfig::HttpError(HttpResponseSettings {
                    enabled: true,
                    kind: FaultKind::HttpError,
                    http_response_status_code: 500,
                    http_response_body: Some("SERVER ERROR".into()),
                    http_response_trigger_probability: options.probability,
                })
            }
        }
    }
}

impl From<(DbCase, &DbOptions)> for FaultConfig {
    fn from((case, options): (DbCase, &DbOptions)) -> Self {
        match case {
            DbCase::SlowQuery => {
                let mean =
                    options.latency_mean.unwrap_or(Duration::from_millis(200));
                FaultConfig::Latency(LatencySettings {
                    enabled: true,
                    kind: FaultKind::Latency,
                    distribution: LatencyDistribution::Normal,
                    direction: Direction::Both,
                    global: false,
                    side: StreamSide::Server,
                    latency_mean: mean.as_secs_f64(),
                    latency_stddev: 0.0,
                    latency_shape: 0.0,
                    latency_scale: 0.0,
                    latency_min: 0.0,
                    latency_max: 0.0,
                })
            }
            DbCase::Deadlock => FaultConfig::HttpError(HttpResponseSettings {
                enabled: true,
                kind: FaultKind::HttpError,
                http_response_status_code: options
                    .error_code
                    .as_ref()
                    .and_then(|c| c.parse().ok())
                    .unwrap_or(500),
                http_response_body: None,
                http_response_trigger_probability: options.deadlock_rate,
            }),
            _ => FaultConfig::Latency(LatencySettings::default()),
        }
    }
}
