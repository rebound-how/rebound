use std::fmt;
use std::net::Ipv4Addr;
use std::time::Duration;

use anyhow::Result;
use clap::ValueEnum;
use serde::Deserialize;
use serde::Deserializer;
use serde::Serialize;
use serde::Serializer;
use serde::de::Error as DeError;

use crate::config;
use crate::config::FaultConfig;
use crate::config::FaultKind;
use crate::errors::ScenarioError;
use crate::sched;

#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
pub enum ProtocolType {
    #[default]
    None,
    Http,
    Https,
    Psql,
    Psqls,
    Tls,
}

impl ProtocolType {
    pub fn from_i32(s: &i32) -> Option<Self> {
        match s {
            0 => None,
            1 => Some(ProtocolType::Http),
            2 => Some(ProtocolType::Https),
            3 => Some(ProtocolType::Psql),
            4 => Some(ProtocolType::Psqls),
            _ => None,
        }
    }
}

#[derive(Debug, Clone)]
pub struct ProxyMap {
    pub proxy: ProxyAddrConfig,
    pub remote: RemoteAddrConfig,
    pub proto: Option<ProtocolType>,
}

impl fmt::Display for ProxyMap {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{}:{} => {}:{}",
            self.proxy.proxy_ip,
            self.proxy.proxy_port,
            self.remote.remote_host,
            self.remote.remote_port,
        )
    }
}

impl ProxyMap {
    pub fn remote_requires_tls(&self) -> bool {
        match &self.proto {
            Some(t) => match t {
                ProtocolType::Http => false,
                ProtocolType::Https => true,
                ProtocolType::Psql => false,
                ProtocolType::Psqls => true,
                ProtocolType::Tls => true,
                ProtocolType::None => false,
            },
            None => false,
        }
    }
}

#[derive(Debug, Clone)]
pub struct RemoteAddrConfig {
    pub remote_host: String,
    pub remote_port: u16,
}

/// Structure to hold the final configuration.
#[derive(Debug, Clone)]
pub struct ProxyAddrConfig {
    pub proxy_ip: Ipv4Addr,
    pub proxy_port: u16,
}

impl ProxyAddrConfig {
    pub fn proxy_address(&self) -> String {
        format!("{}:{}", self.proxy_ip, self.proxy_port)
    }
}

impl fmt::Display for ProxyAddrConfig {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "Proxy Configuration:\n\
             ---------------------\n\
             Proxy IP          : {}\n\
             Proxy Port        : {}",
            self.proxy_ip, self.proxy_port
        )
    }
}

pub struct EbpfProxyAddrConfig {
    pub ip: Ipv4Addr,
    pub port: u16,
    pub ifname: String,
}

impl EbpfProxyAddrConfig {
    pub fn proxy_address(&self) -> String {
        format!("{}:{}", self.ip, self.port)
    }
}

impl fmt::Display for EbpfProxyAddrConfig {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "Ebpf Proxy Configuration:\n\
             ---------------------\n\
             Proxy IP          : {}\n\
             Proxy Port        : {}",
            self.ip, self.port
        )
    }
}

#[derive(clap::ValueEnum, Clone, Debug, Serialize, Deserialize, PartialEq)]
pub enum LatencyDistribution {
    Uniform,
    Normal,
    Pareto,
    ParetoNormal,
}

impl Default for LatencyDistribution {
    fn default() -> Self {
        Self::Uniform // Default latency distribution
    }
}

impl LatencyDistribution {
    pub fn from_str(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "uniform" => Some(LatencyDistribution::Uniform),
            "normal" => Some(LatencyDistribution::Normal),
            "pareto" => Some(LatencyDistribution::Pareto),
            "pareto-normal" => Some(LatencyDistribution::ParetoNormal),
            _ => None,
        }
    }
}

impl fmt::Display for LatencyDistribution {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            LatencyDistribution::Uniform => write!(f, "uniform"),
            LatencyDistribution::Normal => write!(f, "normal"),
            LatencyDistribution::Pareto => write!(f, "pareto"),
            LatencyDistribution::ParetoNormal => write!(f, "pareto-normal"),
        }
    }
}

#[derive(
    clap::ValueEnum, Clone, Debug, Serialize, Deserialize, Eq, PartialEq,
)]
#[serde(rename_all = "lowercase")]
pub enum Direction {
    Ingress,
    Egress,
    #[serde(untagged)]
    Both,
}

impl Default for Direction {
    fn default() -> Self {
        Self::Ingress
    }
}

impl Direction {
    pub fn from_str(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "ingress" => Some(Direction::Ingress),
            "egress" => Some(Direction::Egress),
            "both" => Some(Direction::Both),
            _ => None,
        }
    }

    pub fn is_ingress(&self) -> bool {
        self == &Direction::Ingress || self == &Direction::Both
    }

    pub fn is_egress(&self) -> bool {
        self == &Direction::Egress || self == &Direction::Both
    }
}

impl fmt::Display for Direction {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Direction::Ingress => write!(f, "ingress"),
            Direction::Egress => write!(f, "egress"),
            Direction::Both => write!(f, "both"),
        }
    }
}

#[derive(
    clap::ValueEnum, Clone, Debug, Serialize, Deserialize, Eq, PartialEq,
)]
#[serde(rename_all = "lowercase")]
pub enum StreamSide {
    Client,
    Server,
}

impl StreamSide {
    pub fn from_str(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "client" => Some(StreamSide::Client),
            "server" => Some(StreamSide::Server),
            _ => None,
        }
    }
}

impl Default for StreamSide {
    fn default() -> Self {
        Self::Server
    }
}

impl fmt::Display for StreamSide {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            StreamSide::Client => write!(f, "client"),
            StreamSide::Server => write!(f, "server"),
        }
    }
}

#[derive(clap::ValueEnum, Clone, Debug, Serialize, Deserialize, PartialEq)]
pub enum PacketLossType {
    MultiStateMarkov,
}

impl Default for PacketLossType {
    fn default() -> Self {
        Self::MultiStateMarkov // Default packet loss type
    }
}

impl fmt::Display for PacketLossType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            PacketLossType::MultiStateMarkov => write!(f, "multistatemarkov"),
        }
    }
}

#[derive(
    Copy,
    Clone,
    PartialEq,
    Eq,
    PartialOrd,
    Ord,
    ValueEnum,
    Debug,
    Serialize,
    Deserialize,
)]
pub enum BandwidthUnit {
    Bps, // Bytes per second
    #[clap(name = "kbps")]
    KBps, // Kilobytes per second
    #[clap(name = "mbps")]
    MBps, // Megabytes per second
    #[clap(name = "gbps")]
    GBps, // Gigabytes per second
}

impl Default for BandwidthUnit {
    fn default() -> Self {
        Self::Bps // Default rate limit type
    }
}

impl fmt::Display for BandwidthUnit {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            BandwidthUnit::Bps => write!(f, "Bps"),
            BandwidthUnit::KBps => write!(f, "KBps"),
            BandwidthUnit::MBps => write!(f, "MBps"),
            BandwidthUnit::GBps => write!(f, "GBps"),
        }
    }
}

impl BandwidthUnit {
    pub fn to_bytes_per_second(self, rate: usize) -> usize {
        match self {
            BandwidthUnit::Bps => rate,
            BandwidthUnit::KBps => rate * 1_000,
            BandwidthUnit::MBps => rate * 1_000_000,
            BandwidthUnit::GBps => rate * 1_000_000_000,
        }
    }
}

/// Fault configuration for a scenario entry
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum FaultConfiguration {
    Latency {
        #[serde(skip_serializing_if = "Option::is_none")]
        distribution: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        global: Option<bool>,
        #[serde(skip_serializing_if = "Option::is_none")]
        side: Option<StreamSide>,
        #[serde(skip_serializing_if = "Option::is_none")]
        mean: Option<f64>,
        #[serde(skip_serializing_if = "Option::is_none")]
        stddev: Option<f64>,
        #[serde(skip_serializing_if = "Option::is_none")]
        min: Option<f64>,
        #[serde(skip_serializing_if = "Option::is_none")]
        max: Option<f64>,
        #[serde(skip_serializing_if = "Option::is_none")]
        shape: Option<f64>,
        #[serde(skip_serializing_if = "Option::is_none")]
        scale: Option<f64>,
        #[serde(skip_serializing_if = "Option::is_none")]
        direction: Option<String>,
        #[serde(default)]
        #[serde(deserialize_with = "derialize_period")]
        #[serde(serialize_with = "serialize_period")]
        #[serde(skip_serializing_if = "Option::is_none")]
        period: Option<FaultPeriodSpec>,
    },
    PacketLoss {
        #[serde(skip_serializing_if = "Option::is_none")]
        direction: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        side: Option<StreamSide>,
        #[serde(default)]
        #[serde(deserialize_with = "derialize_period")]
        #[serde(serialize_with = "serialize_period")]
        #[serde(skip_serializing_if = "Option::is_none")]
        period: Option<FaultPeriodSpec>,
    },
    Bandwidth {
        rate: u32,
        unit: BandwidthUnit,
        #[serde(skip_serializing_if = "Option::is_none")]
        direction: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        side: Option<StreamSide>,
        #[serde(default)]
        #[serde(deserialize_with = "derialize_period")]
        #[serde(serialize_with = "serialize_period")]
        #[serde(skip_serializing_if = "Option::is_none")]
        period: Option<FaultPeriodSpec>,
    },
    Jitter {
        amplitude: f64,
        frequency: f64,
        #[serde(skip_serializing_if = "Option::is_none")]
        direction: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        side: Option<StreamSide>,
        #[serde(default)]
        #[serde(deserialize_with = "derialize_period")]
        #[serde(serialize_with = "serialize_period")]
        #[serde(skip_serializing_if = "Option::is_none")]
        period: Option<FaultPeriodSpec>,
    },
    Dns {
        rate: f64,
        #[serde(default)]
        #[serde(deserialize_with = "derialize_period")]
        #[serde(serialize_with = "serialize_period")]
        #[serde(skip_serializing_if = "Option::is_none")]
        period: Option<FaultPeriodSpec>,
    },
    HttpError {
        status_code: u16,
        #[serde(skip_serializing_if = "Option::is_none")]
        body: Option<String>,
        probability: f64,
        #[serde(default)]
        #[serde(deserialize_with = "derialize_period")]
        #[serde(serialize_with = "serialize_period")]
        #[serde(skip_serializing_if = "Option::is_none")]
        period: Option<FaultPeriodSpec>,
    },
    Blackhole {
        #[serde(skip_serializing_if = "Option::is_none")]
        direction: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        side: Option<StreamSide>,
        #[serde(default)]
        #[serde(deserialize_with = "derialize_period")]
        #[serde(serialize_with = "serialize_period")]
        #[serde(skip_serializing_if = "Option::is_none")]
        period: Option<FaultPeriodSpec>,
    },
}

impl FaultConfiguration {
    pub fn build(&self) -> Result<FaultConfig, ScenarioError> {
        match self {
            FaultConfiguration::Bandwidth {
                rate,
                unit,
                direction,
                side,
                ..
            } => {
                let settings = config::BandwidthSettings {
                    enabled: true,
                    kind: FaultKind::Bandwidth,
                    direction: Direction::from_str(
                        &direction.clone().unwrap_or("ingress".to_string()),
                    )
                    .unwrap(),
                    side: side.clone().unwrap_or_default(),
                    bandwidth_rate: *rate as usize,
                    bandwidth_unit: *unit,
                };

                Ok(FaultConfig::Bandwidth(settings))
            }
            FaultConfiguration::Latency {
                distribution,
                global,
                side,
                mean,
                stddev,
                min,
                max,
                scale,
                shape,
                direction,
                ..
            } => {
                let settings = config::LatencySettings {
                    enabled: true,
                    kind: FaultKind::Latency,
                    distribution: LatencyDistribution::from_str(
                        &distribution.clone().unwrap_or("normal".to_string()),
                    )
                    .unwrap(),
                    global: global.unwrap_or(true),
                    side: side.clone().unwrap_or_default(),
                    latency_mean: mean.unwrap_or(100.0),
                    latency_stddev: stddev.unwrap_or(20.0),
                    latency_min: min.unwrap_or(20.0),
                    latency_max: max.unwrap_or(20.0),
                    latency_shape: shape.unwrap_or(20.0),
                    latency_scale: scale.unwrap_or(20.0),
                    direction: Direction::from_str(
                        &direction.clone().unwrap_or("ingress".to_string()),
                    )
                    .unwrap(),
                };

                Ok(FaultConfig::Latency(settings))
            }
            FaultConfiguration::PacketLoss { direction, side, .. } => {
                let settings = config::PacketLossSettings {
                    enabled: true,
                    kind: FaultKind::PacketLoss,
                    direction: Direction::from_str(
                        &direction.clone().unwrap_or("ingress".to_string()),
                    )
                    .unwrap(),
                    side: side.clone().unwrap_or_default(),
                };

                Ok(FaultConfig::PacketLoss(settings))
            }
            FaultConfiguration::Jitter {
                amplitude: jitter_amplitude,
                frequency: jitter_frequency,
                direction,
                side,
                ..
            } => {
                let settings = config::JitterSettings {
                    enabled: true,
                    kind: FaultKind::Jitter,
                    direction: Direction::from_str(
                        &direction.clone().unwrap_or("ingress".to_string()),
                    )
                    .unwrap(),
                    side: side.clone().unwrap_or_default(),
                    amplitude: *jitter_amplitude,
                    frequency: *jitter_frequency,
                };

                Ok(FaultConfig::Jitter(settings))
            }
            FaultConfiguration::Dns { rate: dns_rate, .. } => {
                let settings = config::DnsSettings {
                    enabled: true,
                    kind: FaultKind::Dns,
                    rate: *dns_rate,
                };

                Ok(FaultConfig::Dns(settings))
            }
            FaultConfiguration::HttpError {
                status_code,
                body,
                probability,
                ..
            } => {
                let settings = config::HttpResponseSettings {
                    enabled: true,
                    kind: FaultKind::HttpError,
                    http_response_status_code: *status_code,
                    http_response_body: body.clone(),
                    http_response_trigger_probability: *probability,
                };

                Ok(FaultConfig::HttpError(settings))
            }
            FaultConfiguration::Blackhole { direction, side, .. } => {
                let settings = config::BlackholeSettings {
                    enabled: true,
                    kind: FaultKind::Blackhole,
                    side: side.clone().unwrap_or_default(),
                    direction: Direction::from_str(
                        &direction.clone().unwrap_or("ingress".to_string()),
                    )
                    .unwrap(),
                };

                Ok(FaultConfig::Blackhole(settings))
            }
        }
    }

    pub fn get_period(&self) -> &Option<FaultPeriodSpec> {
        match self {
            FaultConfiguration::Latency { period, .. } => period,
            FaultConfiguration::PacketLoss { period, .. } => period,
            FaultConfiguration::Bandwidth { period, .. } => period,
            FaultConfiguration::Jitter { period, .. } => period,
            FaultConfiguration::Dns { period, .. } => period,
            FaultConfiguration::HttpError { period, .. } => period,
            FaultConfiguration::Blackhole { period, .. } => period,
        }
    }

    pub fn kind(&self) -> FaultKind {
        match self {
            FaultConfiguration::Latency { .. } => FaultKind::Latency,
            FaultConfiguration::PacketLoss { .. } => FaultKind::PacketLoss,
            FaultConfiguration::Bandwidth { .. } => FaultKind::Bandwidth,
            FaultConfiguration::Jitter { .. } => FaultKind::Jitter,
            FaultConfiguration::Dns { .. } => FaultKind::Dns,
            FaultConfiguration::HttpError { .. } => FaultKind::HttpError,
            FaultConfiguration::Blackhole { .. } => FaultKind::Blackhole,
        }
    }
}

pub struct ConnectRequest {
    pub target_host: String,
    pub target_port: u16,
}

/// A time specification: "30s" / "5m" / "120" / "50%" etc.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum TimeSpec {
    Absolute(Duration), // e.g. 30s, 120s, etc.
    Fraction(f64),      // e.g. 0.05 for 5%
}

impl Default for TimeSpec {
    fn default() -> Self {
        TimeSpec::Absolute(Duration::from_secs(0))
    }
}

impl fmt::Display for TimeSpec {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TimeSpec::Absolute(duration) => {
                write!(f, "{}s", duration.as_secs())
            }
            TimeSpec::Fraction(v) => write!(f, "{}%", (v * 100 as f64) as u64),
        }
    }
}

/// A single period: "start:...,duration:..."
#[derive(Default, Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct FaultPeriodSpec {
    pub start: TimeSpec,
    pub duration: Option<TimeSpec>,
}

impl fmt::Display for FaultPeriodSpec {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match &self.duration {
            Some(d) => write!(f, "start:{},duration:{}", self.start, d),
            None => write!(f, "start:{}%", self.start),
        }
    }
}

#[derive(Default, Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct FaultPeriod {
    pub start: Duration,
    pub duration: Option<Duration>,
}

impl TimeSpec {
    pub fn as_fraction(&self, total: Duration) -> f64 {
        if total.is_zero() {
            return 0.0;
        }

        tracing::info!("frac {:?}", self);

        match self {
            TimeSpec::Absolute(abs) => {
                let sec = abs.as_secs_f64();
                (sec / total.as_secs_f64()).clamp(0.0, 1.0)
            }
            TimeSpec::Fraction(frac) => frac.clamp(0.0, 1.0),
        }
    }
}

impl FaultPeriodSpec {
    pub fn as_period(&self, total: Duration) -> (f64, f64) {
        let start_frac = self.start.as_fraction(total);

        let dur_frac = if let Some(d) = &self.duration {
            d.as_fraction(total)
        } else {
            1.0 - start_frac
        };

        let end_frac = (start_frac + dur_frac).clamp(0.0, 1.0);
        (start_frac, end_frac)
    }

    pub fn parse(period: &str) -> Result<Option<Self>> {
        sched::parse_period(period)
    }
}

fn derialize_period<'de, D>(
    deserializer: D,
) -> Result<Option<FaultPeriodSpec>, D::Error>
where
    D: Deserializer<'de>,
{
    match Option::<String>::deserialize(deserializer) {
        Ok(period_str) => match period_str {
            Some(s) => match FaultPeriodSpec::parse(&s) {
                Ok(spec) => Ok(spec),
                Err(e) => Err(D::Error::custom(format!(
                    "invalid fault period '{}': {}",
                    s, e
                ))),
            },
            None => Ok(None),
        },
        Err(_) => Ok(None),
    }
}

pub fn serialize_period<S>(
    period: &Option<FaultPeriodSpec>,
    serializer: S,
) -> Result<S::Ok, S::Error>
where
    S: Serializer,
{
    let s: Option<String> = period.as_ref().map(|p| p.to_string());
    s.serialize(serializer)
}

pub enum OutputFormat {
    Markdown,
    Text,
    Html,
    Json,
    Yaml,
}
