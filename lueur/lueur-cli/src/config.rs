use std::fmt;

use serde::Deserialize;
use serde::Serialize;

use crate::cli::BandwidthOptions;
use crate::cli::DnsOptions;
use crate::cli::HTTPResponseOptions;
use crate::cli::JitterOptions;
use crate::cli::LatencyOptions;
use crate::cli::PacketDuplicationOptions;
use crate::cli::PacketLossOptions;
use crate::cli::RunCommandOptions;
use crate::types::BandwidthUnit;
use crate::types::Direction;
use crate::types::LatencyDistribution;
use crate::types::StreamSide;

/// Internal Configuration for Latency Fault
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct LatencySettings {
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
    pub direction: Direction,
    pub side: StreamSide,
}

/// Internal Configuration for Bandwidth Throttling Fault
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct BandwidthSettings {
    pub direction: Direction,
    pub side: StreamSide,
    pub bandwidth_rate: usize, // in bytes per second
    pub bandwidth_unit: BandwidthUnit,
}

/// Internal Configuration for Jitter Fault
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct JitterSettings {
    pub direction: Direction,
    pub jitter_amplitude: f64, // in milliseconds
    pub jitter_frequency: f64, // in Hertz
}

/// Internal Configuration for DNS Fault
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct DnsSettings {
    pub direction: Direction,
    pub dns_rate: u8, // between 0 and 100
}

/// Internal Configuration for Packet Duplication Fault
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct PacketDuplicationSettings {
    pub direction: Direction,
    pub packet_duplication_probability: f64, // between 0.0 and 1.0
}

/// Internal Configuration for HTTP Error Fault
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct HttpResponseSettings {
    pub http_response_status_code: u16,
    pub http_response_body: Option<String>,
    pub http_response_trigger_probability: f64, // between 0.0 and 1.0
}

/// Fault Configuration Enum
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub enum FaultConfig {
    Dns(DnsSettings),
    Latency(LatencySettings),
    PacketLoss(PacketLossSettings),
    Bandwidth(BandwidthSettings),
    Jitter(JitterSettings),
    PacketDuplication(PacketDuplicationSettings),
    HttpError(HttpResponseSettings),
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
        }
    }
}

/// Proxy Configuration Struct
#[derive(Clone, Debug, Serialize, Deserialize, Default, PartialEq)]
pub struct ProxyConfig {
    pub faults: Vec<FaultConfig>,
}

impl From<&RunCommandOptions> for ProxyConfig {
    fn from(cli: &RunCommandOptions) -> Self {
        let mut faults = Vec::new();

        if cli.latency.enabled {
            faults.push(FaultConfig::Latency((&cli.latency).into()));
        }

        if cli.bandwidth.enabled {
            faults.push(FaultConfig::Bandwidth((&cli.bandwidth).into()));
        }

        if cli.dns.enabled {
            faults.push(FaultConfig::Dns((&cli.dns).into()));
        }

        if cli.jitter.enabled {
            faults.push(FaultConfig::Jitter((&cli.jitter).into()));
        }

        if cli.packet_loss.enabled {
            faults.push(FaultConfig::PacketLoss((&cli.packet_loss).into()));
        }

        if cli.packet_duplication.enabled {
            faults.push(FaultConfig::PacketDuplication(
                (&cli.packet_duplication).into(),
            ));
        }

        if cli.http_error.enabled {
            faults.push(FaultConfig::HttpError((&cli.http_error).into()));
        }

        ProxyConfig { faults }
    }
}

impl From<&LatencyOptions> for LatencySettings {
    fn from(cli: &LatencyOptions) -> Self {
        LatencySettings {
            distribution: cli.latency_distribution.clone(),
            direction: cli.latency_direction.clone(),
            global: cli.global,
            side: cli.side.clone(),
            latency_mean: cli.latency_mean,
            latency_stddev: cli.latency_stddev,
            latency_shape: cli.latency_shape,
            latency_scale: cli.latency_scale,
            latency_min: cli.latency_min,
            latency_max: cli.latency_max,
        }
    }
}

impl From<&BandwidthOptions> for BandwidthSettings {
    fn from(cli: &BandwidthOptions) -> Self {
        BandwidthSettings {
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
            direction: cli.jitter_direction.clone(),
            jitter_amplitude: cli.jitter_amplitude,
            jitter_frequency: cli.jitter_frequency,
        }
    }
}

impl From<&DnsOptions> for DnsSettings {
    fn from(cli: &DnsOptions) -> Self {
        DnsSettings { direction: Direction::Egress, dns_rate: cli.dns_rate }
    }
}

impl From<&PacketLossOptions> for PacketLossSettings {
    fn from(cli: &PacketLossOptions) -> Self {
        PacketLossSettings {
            direction: cli.packet_loss_direction.clone(),
            side: cli.side.clone(),
        }
    }
}

impl From<&PacketDuplicationOptions> for PacketDuplicationSettings {
    fn from(cli: &PacketDuplicationOptions) -> Self {
        PacketDuplicationSettings {
            direction: cli.packet_duplication_direction.clone(),
            packet_duplication_probability: cli.packet_duplication_probability,
        }
    }
}

impl From<&HTTPResponseOptions> for HttpResponseSettings {
    fn from(cli: &HTTPResponseOptions) -> Self {
        HttpResponseSettings {
            http_response_status_code: cli.http_response_status_code,
            http_response_body: cli.http_response_body.clone(),
            http_response_trigger_probability: cli
                .http_response_trigger_probability,
        }
    }
}
