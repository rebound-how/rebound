use clap::Args;
use clap::Parser;
use clap::Subcommand;
use serde::Deserialize;
use serde::Serialize;

use crate::types::BandwidthUnit;
use crate::types::Direction;
use crate::types::LatencyDistribution;
use crate::types::StreamSide;

#[derive(Parser, Debug)]
#[command(
    version,
    about = "A proxy to test network resilience by injecting various faults.",
    long_about = None
)]
pub struct Cli {
    /// Path to the log file. Disabled by default
    #[arg(long)]
    pub log_file: Option<String>,

    /// Stdout logging enabled
    #[arg(long, default_value_t = false)]
    pub log_stdout: bool,

    /// Log level
    #[arg(long, default_value = "info,tower_http=debug")]
    pub log_level: Option<String>,

    /// Disable open telemetry
    #[arg(long, default_value_t = false)]
    pub with_otel: bool,

    #[command(subcommand)]
    pub command: Commands,
}

/// Common options for all Proxy aware commands
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct ProxyAwareCommandCommon {
    /// Listening address for the proxy server
    #[arg(
        help_heading = "Proxy Options",
        long = "proxy-address",
        help = "Listening address for the proxy server.",
        value_parser
    )]
    pub proxy_address: Option<String>,

    #[cfg(target_os = "linux")]
    /// Enable stealth mode (using ebpf)
    #[arg(
        help_heading = "Stealth Options",
        long = "stealth",
        default_value_t = false,
        help = "Enable stealth support (using ebpf).",
        value_parser
    )]
    pub ebpf: bool,

    #[cfg(target_os = "linux")]
    /// Enable ebpf interface
    #[arg(
        help_heading = "Stealth Options",
        long = "ebpf-interface",
        help = "Interface to bind ebpf programs to.",
        requires_if("interface", "ebpf"),
        value_parser
    )]
    pub iface: Option<String>,

    /// gRPC plugin addresses to apply (can specify multiple)
    #[arg(
        help_heading = "Remote Plugins Options",
        short,
        long = "grpc-plugin",
        help = "gRPC plugin addresses to apply (can specify multiple).",
        value_parser
    )]
    pub grpc_plugins: Vec<String>,

    /// Target hosts to match against (can be specified multiple times)
    #[arg(
        help_heading = "Upstreams Options",
        short,
        long = "upstream",
        help = "Host to proxy.",
        requires_if("host", "ebpf"),
        value_parser
    )]
    pub upstream_hosts: Vec<String>,
}

#[derive(Subcommand, Debug)]
pub enum Commands {
    /// Apply a network fault
    Run {
        #[command(flatten)]
        options: RunCommandOptions,
    },

    /// Execute a predefined scenario
    Scenario {
        #[command(subcommand)]
        scenario: ScenarioCommands,

        #[command(flatten)]
        common: ProxyAwareCommandCommon,
    },

    /// Run a simple demo server for learning purpose
    #[command(subcommand)]
    Demo(DemoCommands),
}

#[derive(Parser, Debug, Serialize, Deserialize, Clone)]
pub struct LatencyOptions {
    /// Latency fault enabled
    #[arg(
        help_heading = "Latency Options",
        action,
        name = "latency_enabled",
        long = "with-latency",
        default_value_t = false,
        help = "Enable latency network fault."
    )]
    pub enabled: bool,

    /// Global or per-operation (read/write)
    #[arg(
        help_heading = "Latency Options",
        name = "latency_global",
        action,
        long,
        default_value_t = true,
        help = "Apply a global latency rather than a per write/read operation.",
    )]
    pub global: bool,

    /// Latency side
    #[arg(
        help_heading = "Latency Options",
        name = "latency_side",
        long,
        default_value_t = StreamSide::Server,
        help = "Apply latency on the communication between client to proxy or proxy to upstream server.",
    )]
    pub side: StreamSide,

    /// Direction to apply the latency on
    #[arg(
        help_heading = "Latency Options",
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction.",
    )]
    pub latency_direction: Direction,

    /// Latency distribution to simulate
    #[arg(
        help_heading = "Latency Options",
        long,
        default_value_t = LatencyDistribution::Normal,
        value_enum,
        help = "Latency distribution to simulate (options: uniform, normal, pareto, pareto_normal)."
    )]
    pub latency_distribution: LatencyDistribution,

    /// Mean latency in milliseconds
    #[arg(
        help_heading = "Latency Options",
        long,
        default_value_t = 100.0,
        help = "Mean latency in milliseconds. Must be a positive value.",
        value_parser = validate_positive_f64
    )]
    pub latency_mean: f64,

    /// Standard deviation in milliseconds (applicable for certain
    /// distributions)
    #[arg(
        help_heading = "Latency Options",
        long,
        default_value_t = 20.0,
        help = "Standard deviation in milliseconds. Must be a non-negative value.",
        value_parser = validate_non_negative_f64
    )]
    pub latency_stddev: f64,

    /// Distribution shape
    #[arg(
        help_heading = "Latency Options",
        long,
        default_value_t = 20.0,
        help = "Distribution shape.",
        value_parser = validate_non_negative_f64
    )]
    pub latency_shape: f64,

    /// Distribution scale
    #[arg(
        help_heading = "Latency Options",
        long,
        default_value_t = 20.0,
        help = "Distribution scale.",
        value_parser = validate_non_negative_f64
    )]
    pub latency_scale: f64,

    /// Uniform distribution min
    #[arg(
        help_heading = "Latency Options",
        long,
        default_value_t = 20.0,
        help = "Distribution min.",
        value_parser = validate_non_negative_f64
    )]
    pub latency_min: f64,

    /// Uniform distribution max
    #[arg(
        help_heading = "Latency Options",
        long,
        default_value_t = 20.0,
        help = "Distribution max.",
        value_parser = validate_non_negative_f64
    )]
    pub latency_max: f64,
}

#[derive(Parser, Debug, Serialize, Deserialize, Clone)]
pub struct BandwidthOptions {
    /// Bandwidth fault enabled
    #[arg(
        help_heading = "Bandwidth Options",
        action,
        name = "bandwidth_enabled",
        long = "with-bandwidth",
        default_value_t = false,
        help = "Enable bandwidth network fault."
    )]
    pub enabled: bool,

    /// Bandwidth side
    #[arg(
        help_heading = "Bandwidth Options",
        name = "bandwidth_side",
        long,
        default_value_t = StreamSide::Server,
        help = "Apply bandwidth on the communication between client to proxy or proxy to upstream server.",
    )]
    pub side: StreamSide,

    /// Direction to apply the bandwidth limiter on
    #[arg(
        help_heading = "Bandwidth Options",
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction.",
    )]
    pub bandwidth_direction: Direction,

    /// Bandwidth rate
    #[arg(
        help_heading = "Bandwidth Options",
        long,
        default_value_t = 1000,
        help = "Bandwidth rate. Must be a positive integer.",
        value_parser = validate_positive_usize
    )]
    pub bandwidth_rate: usize,

    /// Unit for the bandwidth rate
    #[arg(
        help_heading = "Bandwidth Options",
        long,
        default_value_t = BandwidthUnit::Bps,
        value_enum,
        help = "Unit for the bandwidth rate (options: Bps, KBps, MBps, GBps)."
    )]
    pub bandwidth_unit: BandwidthUnit,
}

#[derive(Parser, Debug, Serialize, Deserialize, Clone)]
pub struct JitterOptions {
    /// Jitter fault enabled
    #[arg(
        help_heading = "Jitter Options",
        action,
        name = "jitter_enabled",
        long = "with-jitter",
        default_value_t = false,
        help = "Enable jitter network fault."
    )]
    pub enabled: bool,

    /// Direction to apply the jitter on
    #[arg(
        help_heading = "Jitter Options",
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction.",
    )]
    pub jitter_direction: Direction,

    /// Maximum jitter delay in milliseconds
    #[arg(
        help_heading = "Jitter Options",
        long,
        default_value_t = 20.0,
        help = "Maximum jitter delay in milliseconds. Must be a non-negative value.",
        value_parser = validate_non_negative_f64
    )]
    pub jitter_amplitude: f64,

    /// Frequency of jitter application in Hertz (times per second)
    #[arg(
        help_heading = "Jitter Options",
        long,
        default_value_t = 5.0,
        help = "Frequency of jitter application in Hertz (times per second). Must be a non-negative value.",
        value_parser = validate_non_negative_f64
    )]
    pub jitter_frequency: f64,
}

#[derive(Parser, Debug, Serialize, Deserialize, Clone)]
pub struct DnsOptions {
    /// Dns fault enabled
    #[arg(
        help_heading = "DNS Options",
        action,
        name = "dns_enabled",
        long = "with-dns",
        default_value_t = false,
        help = "Enable dns network fault."
    )]
    pub enabled: bool,

    /// Probability to inject the error between 0 and 100
    #[arg(
        help_heading = "DNS Options",
        long,
        default_value_t = 50,
        help = "Probability to trigger the DNS failure between 0 and 100.",
        value_parser = validate_positive_u8
    )]
    pub dns_rate: u8,
}

#[derive(Parser, Debug, Serialize, Deserialize, Clone)]
pub struct PacketLossOptions {
    /// Packet Loss fault enabled
    #[arg(
        help_heading = "Packet Loss Options",
        action,
        name = "packet_loss_enabled",
        long = "with-packet-loss",
        default_value_t = false,
        help = "Enable packet loss network fault."
    )]
    pub enabled: bool,

    /// Packet Loss side
    #[arg(
        help_heading = "Bandwidth Options",
        name = "packet_loss_side",
        long,
        default_value_t = StreamSide::Server,
        help = "Apply packet loss on the communication between client to proxy or proxy to upstream server.",
    )]
    pub side: StreamSide,

    /// Direction to apply the jitter on
    #[arg(
        help_heading = "Packet Loss Options",
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction.",
    )]
    pub packet_loss_direction: Direction,
}

#[derive(Parser, Debug, Serialize, Deserialize, Clone)]
pub struct PacketDuplicationOptions {
    /// Packet Duplication fault enabled
    #[arg(
        help_heading = "Packet Duplication Options",
        action,
        name = "packet_duplication_enabled",
        long = "with-packet-duplication",
        default_value_t = false,
        help = "Enable packet duplication network fault."
    )]
    pub enabled: bool,

    /// Direction to apply the packet duplication on
    #[arg(
        help_heading = "Packet Duplication Options",
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction."
    )]
    pub packet_duplication_direction: Direction,

    /// Probability to duplicate each packet (0.0 to 1.0)
    #[arg(
        help_heading = "Packet Duplication Options",
        long,
        default_value_t = 0.1,
        help = "Probability to duplicate each packet (0.0 to 1.0).",
        value_parser = validate_probability
    )]
    pub packet_duplication_probability: f64,
}

#[derive(Parser, Debug, Serialize, Deserialize, Clone)]
pub struct HTTPResponseOptions {
    /// HTTP Response Fault enabled
    #[arg(
        help_heading = "HTTP Response Options",
        action,
        name = "http_response_enabled",
        long = "with-http-response",
        default_value_t = false,
        help = "Enable HTTP response fault."
    )]
    pub enabled: bool,

    /// HTTP status code to return (e.g., 500, 503)
    #[arg(
        help_heading = "HTTP Response Options",
        long = "http-status",
        default_value_t = 500,
        help = "HTTP status code to return.",
        value_parser = validate_http_status
    )]
    pub http_response_status_code: u16,

    /// Optional response body to return
    #[arg(
        help_heading = "HTTP Response Options",
        long = "http-body",
        help = "Optional HTTP response body to return.",
        value_parser
    )]
    pub http_response_body: Option<String>,

    /// Probability to trigger the HTTP response fault (0.0 to 1.0)
    #[arg(
        help_heading = "HTTP Response Options",
        long,
        default_value_t = 1.0, // Default to always trigger when enabled
        help = "Probability to trigger the HTTP response fault (0.0 to 1.0).",
        value_parser = validate_probability
    )]
    pub http_response_trigger_probability: f64,
}

#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct RunCommandOptions {
    #[command(flatten)]
    pub common: ProxyAwareCommandCommon,

    // Http Error Options
    #[command(flatten)]
    pub http_error: HTTPResponseOptions,

    // Latency Options
    #[command(flatten)]
    pub latency: LatencyOptions,

    // Bandwidth Options
    #[command(flatten)]
    pub bandwidth: BandwidthOptions,

    // Jitter Options
    #[command(flatten)]
    pub jitter: JitterOptions,

    // Dns Options
    #[command(flatten)]
    pub dns: DnsOptions,

    // Packet Loss Options
    #[command(flatten)]
    pub packet_loss: PacketLossOptions,

    // Packet Duplication Options
    #[command(flatten)]
    pub packet_duplication: PacketDuplicationOptions,
}

/// Subcommands for executing scenarios
#[derive(Subcommand, Debug)]
pub enum ScenarioCommands {
    /// Execute a scenario from a file
    Run(ScenarioConfig),
}

/// Subcommands for executing a demo server
#[derive(Subcommand, Debug)]
pub enum DemoCommands {
    /// Execute a demo server for learning purpose
    Run(DemoConfig),
}

/// Configuration for executing scenarios
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct ScenarioConfig {
    /// Path to the scenario file (JSON or YAML)
    #[arg(short, long)]
    pub scenario: String,

    /// Path to the output report file (JSON)
    #[arg(
        short,
        long,
        help = "File to save the generated report. The extension determines the format: .json, .yaml, .html and .md are supported.",
        default_value = "report.json"
    )]
    pub report: String,

    /// Listening address for the proxy server
    #[arg(
        long = "proxy-address",
        help = "Listening address for the proxy server. Overrides the one defined in the scenario.",
        value_parser
    )]
    pub proxy_address: Option<String>,
}

/// Configuration for executing the demo server
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct DemoConfig {
    /// Listening address for the demo server
    #[arg(
        help = "Listening address for the proxy server. Overrides the one defined in the scenario.",
        default_value = "127.0.0.1",
        value_parser
    )]
    pub address: String,

    /// Listening port for the demo server
    #[arg(
        help = "Listening address for the proxy server. Overrides the one defined in the scenario.",
        default_value_t = 7070,
        value_parser
    )]
    pub port: u16,
}

/// Common options for all RunCommands
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct RunCommandCommon {
    /// Direction to apply the latency on
    #[arg(
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction.",
    )]
    pub direction: Direction,
}

/// CLI Configuration for Latency Fault
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct RunCommandLatency {
    #[command(flatten)]
    pub common: RunCommandCommon,

    #[command(flatten)]
    pub config: CliLatencyConfig,
}

/// CLI Configuration for Packet Loss Fault
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct RunCommandPacketLoss {
    #[command(flatten)]
    pub common: RunCommandCommon,

    #[command(flatten)]
    pub config: CliPacketLossConfig,
}

/// CLI Configuration for Bandwidth Throttling Fault
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct RunCommandBandwidth {
    #[command(flatten)]
    pub common: RunCommandCommon,

    #[command(flatten)]
    pub config: CliBandwidthConfig,
}

/// CLI Configuration for Jitter Fault
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct RunCommandJitter {
    #[command(flatten)]
    pub common: RunCommandCommon,

    #[command(flatten)]
    pub config: CliJitterConfig,
}

/// CLI DNS Fault
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct RunCommandDNS {
    #[command(flatten)]
    pub common: RunCommandCommon,

    #[command(flatten)]
    pub config: CliDNSConfig,
}

/// CLI Configuration for Latency Fault
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct CliLatencyConfig {
    /// Latency distribution to simulate
    #[arg(
        long,
        default_value_t = LatencyDistribution::Normal,
        value_enum,
        help = "Latency distribution to simulate (options: uniform, normal, pareto, pareto_normal)."
    )]
    pub distribution: LatencyDistribution,

    /// Mean latency in milliseconds
    #[arg(
        long,
        default_value_t = 100.0,
        help = "Mean latency in milliseconds. Must be a positive value.",
        value_parser = validate_positive_f64
    )]
    pub mean: f64,

    /// Standard deviation in milliseconds (applicable for certain
    /// distributions)
    #[arg(
        long,
        default_value_t = 20.0,
        help = "Standard deviation in milliseconds. Must be a non-negative value.",
        value_parser = validate_non_negative_f64
    )]
    pub stddev: f64,

    /// Distribution shape
    #[arg(
        long,
        default_value_t = 20.0,
        help = "Distribution shape.",
        value_parser = validate_non_negative_f64
    )]
    pub shape: f64,

    /// Distribution scale
    #[arg(
        long,
        default_value_t = 20.0,
        help = "Distribution scale.",
        value_parser = validate_non_negative_f64
    )]
    pub scale: f64,

    /// Uniform distribution min
    #[arg(
        long,
        default_value_t = 20.0,
        help = "Distribution min.",
        value_parser = validate_non_negative_f64
    )]
    pub min: f64,

    /// Uniform distribution max
    #[arg(
        long,
        default_value_t = 20.0,
        help = "Distribution max.",
        value_parser = validate_non_negative_f64
    )]
    pub max: f64,
}

/// CLI Configuration for Packet Loss Fault
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct CliPacketLossConfig {}

/// CLI Configuration for Bandwidth Throttling Fault
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct CliBandwidthConfig {
    /// Bandwidth rate
    #[arg(
        long,
        default_value_t = 1000,
        help = "Bandwidth rate. Must be a positive integer.",
        value_parser = validate_positive_u32
    )]
    pub rate: u32,

    /// Unit for the bandwidth rate
    #[arg(
        long,
        default_value_t = BandwidthUnit::Bps,
        value_enum,
        help = "Unit for the bandwidth rate (options: Bps, KBps, MBps, GBps)."
    )]
    pub unit: BandwidthUnit,
}

/// CLI Configuration for Jitter Fault
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct CliJitterConfig {
    /// Maximum jitter delay in milliseconds
    #[arg(
        long,
        default_value_t = 20.0,
        help = "Maximum jitter delay in milliseconds. Must be a non-negative value.",
        value_parser = validate_non_negative_f64
    )]
    pub amplitude: f64,

    /// Frequency of jitter application in Hertz (times per second)
    #[arg(
        long,
        default_value_t = 5.0,
        help = "Frequency of jitter application in Hertz (times per second). Must be a non-negative value.",
        value_parser = validate_non_negative_f64
    )]
    pub frequency: f64,
}

/// CLI Configuration for DNS
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct CliDNSConfig {
    /// Probability to inject the error between 0 and 100
    #[arg(
        long,
        default_value_t = 50,
        help = "Probability to trigger the DNS failure between 0 and 100.",
        value_parser = validate_positive_u8
    )]
    pub rate: u8,
}

/// Validator for positive f64 values
fn validate_positive_f64(val: &str) -> Result<f64, String> {
    match val.parse::<f64>() {
        Ok(v) if v > 0.0 => Ok(v),
        Ok(_) => Err(String::from("Value must be a positive number.")),
        Err(_) => Err(String::from("Invalid floating-point number.")),
    }
}

/// Validator for non-negative f64 values
fn validate_non_negative_f64(val: &str) -> Result<f64, String> {
    match val.parse::<f64>() {
        Ok(v) if v >= 0.0 => Ok(v),
        Ok(_) => Err(String::from("Value must be a non-negative number.")),
        Err(_) => Err(String::from("Invalid floating-point number.")),
    }
}

/// Validator for positive u32 values
fn validate_positive_u32(val: &str) -> Result<u32, String> {
    match val.parse::<u32>() {
        Ok(v) if v > 0 => Ok(v),
        Ok(_) => Err(String::from("Value must be a positive integer.")),
        Err(_) => Err(String::from("Invalid unsigned integer.")),
    }
}

/// Validator for positive u8 values
fn validate_positive_u8(val: &str) -> Result<u8, String> {
    match val.parse::<u8>() {
        Ok(v) if v > 0 => Ok(v),
        Ok(_) => Err(String::from("Value must be a positive integer.")),
        Err(_) => Err(String::from("Invalid unsigned integer.")),
    }
}

/// Validator for positive usize values
fn validate_positive_usize(val: &str) -> Result<usize, String> {
    match val.parse::<usize>() {
        Ok(v) if v > 0 => Ok(v),
        Ok(_) => Err(String::from("Value must be a positive integer.")),
        Err(_) => Err(String::from("Invalid unsigned integer.")),
    }
}

fn validate_probability(val: &str) -> Result<f64, String> {
    match val.parse::<f64>() {
        Ok(f) if (0.0..=1.0).contains(&f) => Ok(f),
        _ => {
            Err(String::from("Probability must be a float between 0.0 and 1.0"))
        }
    }
}

fn validate_http_status(val: &str) -> Result<u16, String> {
    match val.parse::<u16>() {
        Ok(code) if (100..=599).contains(&code) => Ok(code),
        _ => Err(String::from("HTTP status code must be between 100 and 599")),
    }
}
