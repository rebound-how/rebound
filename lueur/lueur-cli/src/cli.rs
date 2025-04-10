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
    #[arg(help_heading = "Logging Options", long, env = "LUEUR_LOG_FILE")]
    pub log_file: Option<String>,

    /// Stdout logging enabled
    #[arg(
        help_heading = "Logging Options",
        long,
        default_value_t = false,
        env = "LUEUR_WITH_STDOUT_LOGGING"
    )]
    pub log_stdout: bool,

    /// Log level
    #[arg(
        help_heading = "Logging Options",
        long,
        default_value = "info",
        env = "LUEUR_LOG_LEVEL"
    )]
    pub log_level: Option<String>,

    /// Enable open telemetry
    #[arg(
        help_heading = "Observability Options",
        long,
        help = "Enable Open Telemetry tracing and metrics.",
        env = "LUEUR_WITH_OTEL",
        default_value_t = false
    )]
    pub with_otel: bool,

    #[command(subcommand)]
    pub command: Commands,
}

/// Common options for all Proxy aware commands
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct ProxyAwareCommandCommon {
    /// Listening address for the HTTP proxy server
    #[arg(
        help_heading = "Proxy Options",
        long = "proxy-address",
        help = "Listening address for the proxy server.",
        env = "LUEUR_HTTP_PROXY_ADDRESS",
        default_value = "127.0.0.1:3180",
        value_parser
    )]
    pub http_proxy_address: Option<String>,

    /// Mapping to proxy over TCP
    #[arg(
        help_heading = "Proxy Options",
        long = "proxy",
        help = "Start a dedicated proxy for the given mapping.",
        value_parser
    )]
    pub proxy_map: Vec<String>,

    /// gRPC plugin addresses to apply (can specify multiple)
    #[arg(
        help_heading = "Remote Plugins Options",
        short,
        long = "grpc-plugin",
        help = "gRPC plugin addresses to apply (can specify multiple).",
        env = "LUEUR_GRPC_PLUGINS",
        value_delimiter = ',',
        value_parser
    )]
    pub grpc_plugins: Vec<String>,

    /// Target hosts to match against (can be specified multiple times)
    #[arg(
        help_heading = "Upstreams Options",
        short,
        long = "upstream",
        help = "Host to proxy.",
        env = "LUEUR_UPSTREAMS",
        value_delimiter = ',',
        value_parser
    )]
    pub upstream_hosts: Vec<String>,

    /// How long to run the proxy for
    /// If omitted, fraction-based times in DSL (like "5%") are disallowed.
    #[arg(
        help_heading = "Lifecycle Option",
        long,
        help = "How long to run the proxy for.",
        env = "LUEUR_PROXY_DURATIOn",
        value_parser
    )]
    pub duration: Option<String>,
}

#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct StealthCommandCommon {
    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]
    /// Enable stealth mode (using ebpf)
    #[arg(
        help_heading = "Stealth Options",
        long = "stealth",
        default_value_t = false,
        help = "Enable stealth support (using ebpf).",
        env = "LUEUR_ENABLE_STEALTH",
        value_parser
    )]
    pub ebpf: bool,

    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]

    /// Ebpf allowed process by names
    #[arg(
        help_heading = "Stealth Options",
        long = "capture-process",
        help = "Process name to intercept traffic using ebpf.",
        env = "LUEUR_EBPF_PROCESS_NAME",
        value_parser
    )]
    pub ebpf_process_name: Option<String>,

    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]
    /// eBPF programs directory
    #[arg(
        help_heading = "Stealth Options",
        long = "ebpf-programs-dir",
        help = "Directory containing the lueur ebpf programs.",
        env = "LUEUR_EBPF_PROGRAMS_DIR",
        default_value = "~/.local/bin",
        value_parser
    )]
    pub ebpf_programs_dir: Option<String>,

    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]
    /// eBPF proxy port, leave empty for a random port
    #[arg(
        help_heading = "Stealth Options",
        long = "ebpf-proxy-ip",
        help = "IP of the eBPF proxy, if not provided use the same IP as the proxy or the first non-loopback available.",
        env = "LUEUR_EBPF_PROXY_IP",
        value_parser
    )]
    pub ebpf_proxy_ip: Option<String>,

    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]
    /// eBPF proxy port, leave empty for a random port
    #[arg(
        help_heading = "Stealth Options",
        long = "ebpf-proxy-iface",
        help = "Interface to bind the EBPF programs to, if not provided find the first non-loopback available.",
        env = "LUEUR_EBPF_PROXY_IFACE",
        value_parser
    )]
    pub ebpf_proxy_iface: Option<String>,

    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]
    /// eBPF proxy port, leave empty for a random port
    #[arg(
        help_heading = "Stealth Options",
        long = "ebpf-proxy-port",
        help = "Port of the eBPF proxy, if not provided a random port will be used.",
        env = "LUEUR_EBPF_PROXY_PORT",
        value_parser
    )]
    pub ebpf_proxy_port: Option<u16>,
}

#[derive(Subcommand, Debug)]
pub enum Commands {
    /// Run the lueur proxy and apply network faults to traffic
    Run {
        #[command(flatten)]
        options: Box<RunCommandOptions>,
    },

    /// Execute a scenario
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
        help = "Enable latency network fault.",
        env = "LUEUR_WITH_LATENCY"
    )]
    pub enabled: bool,

    /// Global or per-operation (read/write)
    #[arg(
        help_heading = "Latency Options",
        name = "latency-per-read-write",
        action,
        long,
        default_value_t = false,
        help = "Apply a global latency rather than a per write/read operation.",
        env = "LUEUR_LATENCY_PER_READ_WRITE"
    )]
    pub per_read_write: bool,

    /// Latency side
    #[arg(
        help_heading = "Latency Options",
        name = "latency-side",
        long,
        default_value_t = StreamSide::Server,
        help = "Apply latency on the communication between client to proxy or proxy to upstream server.",
        env = "LUEUR_LATENCY_SIDE",
    )]
    pub side: StreamSide,

    /// Direction to apply the latency on
    #[arg(
        help_heading = "Latency Options",
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction.",
        env = "LUEUR_LATENCY_DIRECTION",
    )]
    pub latency_direction: Direction,

    /// Latency distribution to simulate
    #[arg(
        help_heading = "Latency Options",
        long,
        default_value_t = LatencyDistribution::Normal,
        value_enum,
        help = "Latency distribution to simulate (options: uniform, normal, pareto, pareto_normal).",
        env = "LUEUR_LATENCY_DISTRIBUTION",
    )]
    pub latency_distribution: LatencyDistribution,

    /// Mean latency in milliseconds
    #[arg(
        help_heading = "Latency Options",
        long,
        help = "Mean latency in milliseconds. Must be a positive value.",
        value_parser = validate_positive_f64,
        env = "LUEUR_LATENCY_MEAN",
    )]
    pub latency_mean: Option<f64>,

    /// Standard deviation in milliseconds (applicable for certain
    /// distributions)
    #[arg(
        help_heading = "Latency Options",
        long,
        help = "Standard deviation in milliseconds. Must be a non-negative value.",
        value_parser = validate_non_negative_f64,
        env = "LUEUR_LATENCY_STANDARD_DEVIATION",
    )]
    pub latency_stddev: Option<f64>,

    /// Distribution shape
    #[arg(
        help_heading = "Latency Options",
        long,
        help = "Distribution shape.",
        value_parser = validate_non_negative_f64,
        env = "LUEUR_LATENCY_SHAPE",
    )]
    pub latency_shape: Option<f64>,

    /// Distribution scale
    #[arg(
        help_heading = "Latency Options",
        long,
        help = "Distribution scale.",
        value_parser = validate_non_negative_f64,
        env = "LUEUR_LATENCY_SCALE",
    )]
    pub latency_scale: Option<f64>,

    /// Uniform distribution min
    #[arg(
        help_heading = "Latency Options",
        long,
        help = "Distribution min.",
        value_parser = validate_non_negative_f64,
        env = "LUEUR_LATENCY_MIN",
    )]
    pub latency_min: Option<f64>,

    /// Uniform distribution max
    #[arg(
        help_heading = "Latency Options",
        long,
        help = "Distribution max.",
        value_parser = validate_non_negative_f64,
        env = "LUEUR_LATENCY_MAX",
    )]
    pub latency_max: Option<f64>,

    /// Latency period
    #[arg(
        help_heading = "Latency Options",
        long,
        help = "Latency schedule",
        env = "LUEUR_LATENCY_SCHED"
    )]
    pub latency_sched: Option<String>,
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
        help = "Enable bandwidth network fault.",
        env = "LUEUR_WITH_BANDWIDTH"
    )]
    pub enabled: bool,

    /// Bandwidth side
    #[arg(
        help_heading = "Bandwidth Options",
        name = "bandwidth-side",
        long,
        default_value_t = StreamSide::Server,
        help = "Apply bandwidth on the communication between client to proxy or proxy to upstream server.",
        env = "LUEUR_BANDWIDTH_SIDE",
    )]
    pub side: StreamSide,

    /// Direction to apply the bandwidth limiter on
    #[arg(
        help_heading = "Bandwidth Options",
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction.",
        env = "LUEUR_BANDWIDTH_DIRECTION",
    )]
    pub bandwidth_direction: Direction,

    /// Bandwidth rate
    #[arg(
        help_heading = "Bandwidth Options",
        long,
        default_value_t = 1000,
        help = "Bandwidth rate. Must be a positive integer.",
        value_parser = validate_positive_usize,
        env = "LUEUR_BANDWIDTH_RATE",
    )]
    pub bandwidth_rate: usize,

    /// Unit for the bandwidth rate
    #[arg(
        help_heading = "Bandwidth Options",
        long,
        default_value_t = BandwidthUnit::Bps,
        value_enum,
        help = "Unit for the bandwidth rate (options: Bps, KBps, MBps, GBps).",
        env = "LUEUR_BANDWIDTH_UNIT",
    )]
    pub bandwidth_unit: BandwidthUnit,

    /// Bandwidth period
    #[arg(
        help_heading = "Bandwidth Options",
        long,
        help = "Bandwidth schedule",
        env = "LUEUR_BANDWIDTH_SCHED"
    )]
    pub bandwidth_sched: Option<String>,
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
        help = "Enable jitter network fault.",
        env = "LUEUR_WITH_JITTER"
    )]
    pub enabled: bool,

    /// Direction to apply the jitter on
    #[arg(
        help_heading = "Jitter Options",
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction.",
        env = "LUEUR_JITTER_DIRECTION",
    )]
    pub jitter_direction: Direction,

    /// Maximum jitter delay in milliseconds
    #[arg(
        help_heading = "Jitter Options",
        long,
        default_value_t = 20.0,
        help = "Maximum jitter delay in milliseconds. Must be a non-negative value.",
        value_parser = validate_non_negative_f64,
        env = "LUEUR_JITTER_AMPLITUDE",
    )]
    pub jitter_amplitude: f64,

    /// Frequency of jitter application in Hertz (times per second)
    #[arg(
        help_heading = "Jitter Options",
        long,
        default_value_t = 5.0,
        help = "Frequency of jitter application in Hertz (times per second). Must be a non-negative value.",
        value_parser = validate_non_negative_f64,
        env = "LUEUR_JITTER_FREQ",
    )]
    pub jitter_frequency: f64,

    /// Jitter period
    #[arg(
        help_heading = "Jitter Options",
        long,
        help = "Jitter schedule",
        env = "LUEUR_JITTER_SCHED"
    )]
    pub jitter_sched: Option<String>,
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
        help = "Enable dns network fault.",
        env = "LUEUR_WITH_DNS"
    )]
    pub enabled: bool,

    /// Probability to inject the error between 0 and 100
    #[arg(
        help_heading = "DNS Options",
        long,
        default_value_t = 0.5,
        help = "Probability to trigger the DNS failure between 0.0 and 1.0.",
        value_parser = validate_probability,
        env = "LUEUR_DNS_PROBABILITY",
    )]
    pub dns_rate: f64,

    /// Dns period
    #[arg(
        help_heading = "Dns Options",
        long,
        help = "Dns schedule",
        env = "LUEUR_DNS_SCHED"
    )]
    pub dns_sched: Option<String>,
}

#[derive(Parser, Debug, Serialize, Deserialize, Clone)]
pub struct PacketLossOptions {
    /// Packet Loss fault enabled
    #[arg(
        help_heading = "Packet Loss Options",
        action,
        name = "packet-loss-enabled",
        long = "with-packet-loss",
        default_value_t = false,
        help = "Enable packet loss network fault.",
        env = "LUEUR_WITH_PACKET_LOSS"
    )]
    pub enabled: bool,

    /// Packet Loss side
    #[arg(
        help_heading = "Packet Loss Options",
        name = "packet-loss-side",
        long,
        default_value_t = StreamSide::Server,
        help = "Apply packet loss on the communication between client to proxy or proxy to upstream server.",
        env = "LUEUR_PACKET_LOSS_SIDE",
    )]
    pub side: StreamSide,

    /// Direction to apply the packet loss on
    #[arg(
        help_heading = "Packet Loss Options",
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction.",
        env = "LUEUR_PACKET_LOSS_DIRECTION",
    )]
    pub packet_loss_direction: Direction,

    /// Packet Loss period
    #[arg(
        help_heading = "Packet Loss Options",
        long,
        help = "Packet Loss schedule",
        env = "LUEUR_PACKET_LOSS_SCHED"
    )]
    pub packet_loss_sched: Option<String>,
}

#[derive(Parser, Debug, Serialize, Deserialize, Clone)]
pub struct BlackholeOptions {
    /// Blackhole fault enabled
    #[arg(
        help_heading = "Blackhole Options",
        action,
        name = "blackhole-enabled",
        long = "with-blackhole",
        default_value_t = false,
        help = "Enable blackhole network fault.",
        env = "LUEUR_WITH_BLACKHOLE"
    )]
    pub enabled: bool,

    /// Blackhole side
    #[arg(
        help_heading = "Blackhole Options",
        name = "blackhole-side",
        long,
        default_value_t = StreamSide::Server,
        help = "Apply blackhole on the communication between client to proxy or proxy to upstream server.",
        env = "LUEUR_BLACKHOLE_SIDE",
    )]
    pub side: StreamSide,

    /// Direction to apply the blackhole on
    #[arg(
        help_heading = "Blackhole Options",
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction.",
        env = "LUEUR_BLACKHOLE_DIRECTION",
    )]
    pub blackhole_direction: Direction,

    /// Blackhole period
    #[arg(
        help_heading = "Blackhole Options",
        long,
        help = "Blackhole schedule",
        env = "LUEUR_BLACKHOLE_SCHED"
    )]
    pub blackhole_sched: Option<String>,
}

/*
#[derive(Parser, Debug, Serialize, Deserialize, Clone)]
pub struct PacketDuplicationOptions {
    /// Packet Duplication fault enabled
    #[arg(
        help_heading = "Packet Duplication Options",
        action,
        name = "packet-duplication-enabled",
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
*/
#[derive(Parser, Debug, Serialize, Deserialize, Clone)]
pub struct HTTPResponseOptions {
    /// HTTP Response Fault enabled
    #[arg(
        help_heading = "HTTP Response Options",
        action,
        name = "http_response_enabled",
        long = "with-http-response",
        default_value_t = false,
        help = "Enable HTTP response fault.",
        env = "LUEUR_WITH_HTTP_FAULT"
    )]
    pub enabled: bool,

    /// HTTP status code to return (e.g., 500, 503)
    #[arg(
        help_heading = "HTTP Response Options",
        long = "http-response-status",
        default_value_t = 500,
        help = "HTTP status code to return.",
        value_parser = validate_http_status,
        env = "LUEUR_HTTP_FAULT_STATUS",
    )]
    pub http_response_status_code: u16,

    /// Optional response body to return
    #[arg(
        help_heading = "HTTP Response Options",
        long = "http-response-body",
        help = "Optional HTTP response body to return.",
        value_parser,
        env = "LUEUR_HTTP_FAULT_BODY"
    )]
    pub http_response_body: Option<String>,

    /// Probability to trigger the HTTP response fault (0.0 to 1.0)
    #[arg(
        help_heading = "HTTP Response Options",
        long,
        default_value_t = 1.0, // Default to always trigger when enabled
        help = "Probability to trigger the HTTP response fault (0.0 to 1.0).",
        value_parser = validate_probability,
        env = "LUEUR_HTTP_FAULT_PROBABILITY",
    )]
    pub http_response_trigger_probability: f64,

    /// HTTP Response period
    #[arg(
        help_heading = "HTTP Response Options",
        long,
        help = "HTTP Response schedule",
        env = "LUEUR_HTTP_FAULT_SCHED"
    )]
    pub http_response_sched: Option<String>,
}

#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct ProxyUICommon {
    /// Disable proxi terminal UI
    #[arg(long, default_value_t = false, env = "LUEUR_PROXY_NO_UI")]
    pub no_ui: bool,

    /// Enable tailing of incoming requests
    #[arg(long, default_value_t = false, env = "LUEUR_PROXY_TAILING")]
    pub tail: bool,
}

#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct RunCommandOptions {
    #[command(flatten)]
    pub ui: ProxyUICommon,

    #[command(flatten)]
    pub common: ProxyAwareCommandCommon,

    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]
    #[command(flatten)]
    pub stealth: StealthCommandCommon,

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

    // Blackhole Options
    #[command(flatten)]
    pub blackhole: BlackholeOptions,
    /*
    // Packet Duplication Options
    #[command(flatten)]
    pub packet_duplication: PacketDuplicationOptions,
     */
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
    /// Path to the scenario file (YAML)
    #[arg(
        short,
        long,
        help = "Path to a scenario file",
        env = "LUEUR_SCENARIO_PATH"
    )]
    pub scenario: String,

    /// Path to the output report file
    #[arg(
        short,
        long,
        help = "File to save the generated report. The extension determines the format: .json, .yaml, .html and .md are supported.",
        default_value = "report.json",
        env = "LUEUR_SCENARIO_REPORT_PATH"
    )]
    pub report: String,

    /// Path to the output results file (JSON)
    #[arg(
        long,
        help = "File to save the generated results.",
        default_value = "results.json",
        env = "LUEUR_SCENARIO_RESULTS_PATH"
    )]
    pub result: String,
}

/// Configuration for executing the demo server
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct DemoConfig {
    /// Listening address for the demo server
    #[arg(
        help = "Listening address for the proxy server. Overrides the one defined in the scenario.",
        default_value = "127.0.0.1",
        value_parser,
        env = "LUEUR_DEMO_ADDR"
    )]
    pub address: String,

    /// Listening port for the demo server
    #[arg(
        help = "Listening address for the proxy server. Overrides the one defined in the scenario.",
        default_value_t = 7070,
        value_parser,
        env = "LUEUR_DEMO_PORT"
    )]
    pub port: u16,
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
