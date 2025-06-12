use std::collections::BTreeMap;

use clap::Args;
use clap::Parser;
use clap::Subcommand;
use serde::Deserialize;
use serde::Serialize;

#[cfg(feature = "agent")]
use crate::agent::clients::SupportedLLMClient;
#[cfg(feature = "agent")]
use crate::agent::insight::ReportReviewRole;
#[cfg(feature = "agent")]
use crate::agent::platform::PlatformReviewRole;
#[cfg(feature = "discovery")]
use crate::discovery::types::ResourcePlatform;
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
    #[arg(help_heading = "Logging Options", long, env = "FAULT_LOG_FILE")]
    pub log_file: Option<String>,

    /// Stdout logging enabled
    #[arg(
        help_heading = "Logging Options",
        long,
        default_value_t = false,
        env = "FAULT_WITH_STDOUT_LOGGING"
    )]
    pub log_stdout: bool,

    /// Log level
    #[arg(
        help_heading = "Logging Options",
        long,
        default_value = "info",
        env = "FAULT_LOG_LEVEL"
    )]
    pub log_level: Option<String>,

    /// Enable open telemetry
    #[arg(
        help_heading = "Observability Options",
        long,
        help = "Enable Open Telemetry tracing and metrics.",
        env = "FAULT_WITH_OTEL",
        default_value_t = false
    )]
    pub with_otel: bool,

    /// Listening address for the API service
    #[arg(
        hide = true,
        help_heading = "API Service Options",
        long = "api-address",
        help = "Address for the API service.",
        env = "FAULT_API_SERVICE_ADDRESS",
        default_value = "0.0.0.0:7900",
        value_parser
    )]
    pub api_address: Option<String>,

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
        env = "FAULT_HTTP_PROXY_ADDRESS",
        default_value = "127.0.0.1:3180",
        value_parser
    )]
    pub http_proxy_address: Option<String>,

    /// Disable HTTP proxying
    #[arg(
        help_heading = "Proxy Options",
        long = "disable-http-proxy",
        default_value_t = false,
        help = "Disable HTTP proxying.",
        env = "FAULT_DISABLE_HTTP_PROXY",
        value_parser
    )]
    pub disable_http_proxies: bool,

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
        env = "FAULT_GRPC_PLUGINS",
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
        env = "FAULT_UPSTREAMS",
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
        env = "FAULT_PROXY_DURATION",
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
        env = "FAULT_ENABLE_STEALTH",
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
        env = "FAULT_EBPF_PROCESS_NAME",
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
        help = "Directory containing the fault ebpf programs.",
        env = "FAULT_EBPF_PROGRAMS_DIR",
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
        env = "FAULT_EBPF_PROXY_IP",
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
        env = "FAULT_EBPF_PROXY_IFACE",
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
        env = "FAULT_EBPF_PROXY_PORT",
        value_parser
    )]
    pub ebpf_proxy_port: Option<u16>,
}

#[derive(Subcommand, Debug)]
pub enum Commands {
    /// Resilience Proxy
    Run {
        #[command(flatten)]
        options: Box<RunCommandOptions>,
    },

    /// Resilience Fault Injection
    #[cfg(feature = "injection")]
    Inject {
        #[command(subcommand)]
        inject: FaultInjectionCommands,
    },

    /// Resilience Automation
    #[cfg(feature = "scenario")]
    Scenario {
        #[command(subcommand)]
        scenario: ScenarioCommands,

        #[command(flatten)]
        common: ProxyAwareCommandCommon,
    },

    /// Resilience Agentic Buddy
    #[cfg(feature = "agent")]
    Agent {
        #[command(subcommand)]
        agent: AgentCommands,

        #[command(flatten)]
        common: AgentCommandCommon,
    },

    /// Run a simple demo server for learning purpose
    #[cfg(feature = "demo")]
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
        env = "FAULT_WITH_LATENCY"
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
        env = "FAULT_LATENCY_PER_READ_WRITE"
    )]
    pub per_read_write: bool,

    /// Latency side
    #[arg(
        help_heading = "Latency Options",
        name = "latency-side",
        long,
        default_value_t = StreamSide::Server,
        help = "Apply latency on the communication between client to proxy or proxy to upstream server.",
        env = "FAULT_LATENCY_SIDE",
    )]
    pub side: StreamSide,

    /// Direction to apply the latency on
    #[arg(
        help_heading = "Latency Options",
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction.",
        env = "FAULT_LATENCY_DIRECTION",
    )]
    pub latency_direction: Direction,

    /// Latency distribution to simulate
    #[arg(
        help_heading = "Latency Options",
        long,
        default_value_t = LatencyDistribution::Normal,
        value_enum,
        help = "Latency distribution to simulate (options: uniform, normal, pareto, pareto_normal).",
        env = "FAULT_LATENCY_DISTRIBUTION",
    )]
    pub latency_distribution: LatencyDistribution,

    /// Mean latency in milliseconds
    #[arg(
        help_heading = "Latency Options",
        long,
        help = "Mean latency in milliseconds. Must be a positive value.",
        value_parser = validate_positive_f64,
        env = "FAULT_LATENCY_MEAN",
    )]
    pub latency_mean: Option<f64>,

    /// Standard deviation in milliseconds (applicable for certain
    /// distributions)
    #[arg(
        help_heading = "Latency Options",
        long,
        help = "Standard deviation in milliseconds. Must be a non-negative value.",
        value_parser = validate_non_negative_f64,
        env = "FAULT_LATENCY_STANDARD_DEVIATION",
    )]
    pub latency_stddev: Option<f64>,

    /// Distribution shape
    #[arg(
        help_heading = "Latency Options",
        long,
        help = "Distribution shape.",
        value_parser = validate_non_negative_f64,
        env = "FAULT_LATENCY_SHAPE",
    )]
    pub latency_shape: Option<f64>,

    /// Distribution scale
    #[arg(
        help_heading = "Latency Options",
        long,
        help = "Distribution scale.",
        value_parser = validate_non_negative_f64,
        env = "FAULT_LATENCY_SCALE",
    )]
    pub latency_scale: Option<f64>,

    /// Uniform distribution min
    #[arg(
        help_heading = "Latency Options",
        long,
        help = "Distribution min.",
        value_parser = validate_non_negative_f64,
        env = "FAULT_LATENCY_MIN",
    )]
    pub latency_min: Option<f64>,

    /// Uniform distribution max
    #[arg(
        help_heading = "Latency Options",
        long,
        help = "Distribution max.",
        value_parser = validate_non_negative_f64,
        env = "FAULT_LATENCY_MAX",
    )]
    pub latency_max: Option<f64>,

    /// Latency period
    #[arg(
        help_heading = "Latency Options",
        long,
        help = "Latency schedule",
        env = "FAULT_LATENCY_SCHED"
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
        env = "FAULT_WITH_BANDWIDTH"
    )]
    pub enabled: bool,

    /// Bandwidth side
    #[arg(
        help_heading = "Bandwidth Options",
        name = "bandwidth-side",
        long,
        default_value_t = StreamSide::Server,
        help = "Apply bandwidth on the communication between client to proxy or proxy to upstream server.",
        env = "FAULT_BANDWIDTH_SIDE",
    )]
    pub side: StreamSide,

    /// Direction to apply the bandwidth limiter on
    #[arg(
        help_heading = "Bandwidth Options",
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction.",
        env = "FAULT_BANDWIDTH_DIRECTION",
    )]
    pub bandwidth_direction: Direction,

    /// Bandwidth rate
    #[arg(
        help_heading = "Bandwidth Options",
        long,
        default_value_t = 1000,
        help = "Bandwidth rate. Must be a positive integer.",
        value_parser = validate_positive_usize,
        env = "FAULT_BANDWIDTH_RATE",
    )]
    pub bandwidth_rate: usize,

    /// Unit for the bandwidth rate
    #[arg(
        help_heading = "Bandwidth Options",
        long,
        default_value_t = BandwidthUnit::Bps,
        value_enum,
        help = "Unit for the bandwidth rate (options: Bps, KBps, MBps, GBps).",
        env = "FAULT_BANDWIDTH_UNIT",
    )]
    pub bandwidth_unit: BandwidthUnit,

    /// Bandwidth period
    #[arg(
        help_heading = "Bandwidth Options",
        long,
        help = "Bandwidth schedule",
        env = "FAULT_BANDWIDTH_SCHED"
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
        env = "FAULT_WITH_JITTER"
    )]
    pub enabled: bool,

    /// Direction to apply the jitter on
    #[arg(
        help_heading = "Jitter Options",
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction.",
        env = "FAULT_JITTER_DIRECTION",
    )]
    pub jitter_direction: Direction,

    /// Side to apply the jitter on
    #[arg(
        help_heading = "Jitter Options",
        long,
        default_value_t = StreamSide::Server,
        value_enum,
        help = "Fault's side.",
        env = "FAULT_JITTER_SIDE",
    )]
    pub jitter_side: StreamSide,

    /// Maximum jitter delay in milliseconds
    #[arg(
        help_heading = "Jitter Options",
        long,
        default_value_t = 20.0,
        help = "Maximum jitter delay in milliseconds. Must be a non-negative value.",
        value_parser = validate_non_negative_f64,
        env = "FAULT_JITTER_AMPLITUDE",
    )]
    pub jitter_amplitude: f64,

    /// Frequency of jitter application in Hertz (times per second)
    #[arg(
        help_heading = "Jitter Options",
        long,
        default_value_t = 5.0,
        help = "Frequency of jitter application in Hertz (times per second). Must be a non-negative value.",
        value_parser = validate_non_negative_f64,
        env = "FAULT_JITTER_FREQ",
    )]
    pub jitter_frequency: f64,

    /// Jitter period
    #[arg(
        help_heading = "Jitter Options",
        long,
        help = "Jitter schedule",
        env = "FAULT_JITTER_SCHED"
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
        env = "FAULT_WITH_DNS"
    )]
    pub enabled: bool,

    /// Probability to inject the error between 0 and 100
    #[arg(
        help_heading = "DNS Options",
        long,
        default_value_t = 0.5,
        help = "Probability to trigger the DNS failure between 0.0 and 1.0.",
        value_parser = validate_probability,
        env = "FAULT_DNS_PROBABILITY",
    )]
    pub dns_rate: f64,

    /// Dns period
    #[arg(
        help_heading = "DNS Options",
        long,
        help = "Dns schedule",
        env = "FAULT_DNS_SCHED"
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
        env = "FAULT_WITH_PACKET_LOSS"
    )]
    pub enabled: bool,

    /// Packet Loss side
    #[arg(
        help_heading = "Packet Loss Options",
        name = "packet-loss-side",
        long,
        default_value_t = StreamSide::Server,
        help = "Apply packet loss on the communication between client to proxy or proxy to upstream server.",
        env = "FAULT_PACKET_LOSS_SIDE",
    )]
    pub side: StreamSide,

    /// Direction to apply the packet loss on
    #[arg(
        help_heading = "Packet Loss Options",
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction.",
        env = "FAULT_PACKET_LOSS_DIRECTION",
    )]
    pub packet_loss_direction: Direction,

    /// Packet Loss period
    #[arg(
        help_heading = "Packet Loss Options",
        long,
        help = "Packet Loss schedule",
        env = "FAULT_PACKET_LOSS_SCHED"
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
        env = "FAULT_WITH_BLACKHOLE"
    )]
    pub enabled: bool,

    /// Blackhole side
    #[arg(
        help_heading = "Blackhole Options",
        name = "blackhole-side",
        long,
        default_value_t = StreamSide::Server,
        help = "Apply blackhole on the communication between client to proxy or proxy to upstream server.",
        env = "FAULT_BLACKHOLE_SIDE",
    )]
    pub side: StreamSide,

    /// Direction to apply the blackhole on
    #[arg(
        help_heading = "Blackhole Options",
        long,
        default_value_t = Direction::Ingress,
        value_enum,
        help = "Fault's direction.",
        env = "FAULT_BLACKHOLE_DIRECTION",
    )]
    pub blackhole_direction: Direction,

    /// Blackhole period
    #[arg(
        help_heading = "Blackhole Options",
        long,
        help = "Blackhole schedule",
        env = "FAULT_BLACKHOLE_SCHED"
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
        env = "FAULT_WITH_HTTP_FAULT"
    )]
    pub enabled: bool,

    /// HTTP status code to return (e.g., 500, 503)
    #[arg(
        help_heading = "HTTP Response Options",
        long = "http-response-status",
        default_value_t = 500,
        help = "HTTP status code to return.",
        value_parser = validate_http_status,
        env = "FAULT_HTTP_FAULT_STATUS",
    )]
    pub http_response_status_code: u16,

    /// Optional response body to return
    #[arg(
        help_heading = "HTTP Response Options",
        long = "http-response-body",
        help = "Optional HTTP response body to return.",
        value_parser,
        env = "FAULT_HTTP_FAULT_BODY"
    )]
    pub http_response_body: Option<String>,

    /// Probability to trigger the HTTP response fault (0.0 to 1.0)
    #[arg(
        help_heading = "HTTP Response Options",
        long,
        default_value_t = 1.0, // Default to always trigger when enabled
        help = "Probability to trigger the HTTP response fault (0.0 to 1.0).",
        value_parser = validate_probability,
        env = "FAULT_HTTP_FAULT_PROBABILITY",
    )]
    pub http_response_trigger_probability: f64,

    /// HTTP Response period
    #[arg(
        help_heading = "HTTP Response Options",
        long,
        help = "HTTP Response schedule",
        env = "FAULT_HTTP_FAULT_SCHED"
    )]
    pub http_response_sched: Option<String>,
}

#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct ProxyUICommon {
    /// Disable proxi terminal UI
    #[arg(long, default_value_t = false, env = "FAULT_PROXY_NO_UI")]
    pub no_ui: bool,

    /// Enable tailing of incoming requests
    #[arg(long, default_value_t = false, env = "FAULT_PROXY_TAILING")]
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
#[cfg(feature = "scenario")]
#[derive(Subcommand, Debug)]
pub enum ScenarioCommands {
    /// Execute a scenario from a file
    Run(ScenarioRunConfig),

    /// Generate a new scenario from an OpenAPIv3 specification
    #[cfg(feature = "openapi")]
    Generate(ScenarioGenerateConfig),
}

/// Subcommands for the agent
#[cfg(feature = "agent")]
#[derive(Subcommand, Debug)]
pub enum AgentCommands {
    /// Explore and suggests changes of source code to help reliability
    CodeReview(AgentReviewConfig),

    /// Analyze and offer advices of your scenario report
    ScenarioReview(AgentAdviceConfig),

    /// Analyze and offer advices of your platform report
    PlatformReview {
        #[command(subcommand)]
        platform: AgentPlatformCommands,
    },
}

/// Subcommands for executing a demo server
#[cfg(feature = "demo")]
#[derive(Subcommand, Debug)]
pub enum DemoCommands {
    /// Execute a demo server for learning purpose
    Run(DemoConfig),
}

/// Configuration for executing scenarios
#[cfg(feature = "scenario")]
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct ScenarioRunConfig {
    /// Path to the scenario file (YAML)
    #[arg(
        short,
        long,
        help = "Path to a scenario file",
        env = "FAULT_SCENARIO_PATH"
    )]
    pub scenario: String,

    /// Path to the output report file
    #[arg(
        short,
        long,
        help = "File to save the generated report.",
        default_value = "report.md",
        env = "FAULT_SCENARIO_REPORT_PATH"
    )]
    pub report: String,

    /// Path to the output results file (JSON)
    #[arg(
        long,
        help = "File to save the generated results.",
        default_value = "results.json",
        env = "FAULT_SCENARIO_RESULTS_PATH"
    )]
    pub result: String,
}

/// Configuration for generating scenarios
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct ScenarioGenerateConfig {
    /// Directory or file where to save the scenarios
    #[arg(
        long,
        help = "Directory or file where to save the scenarios",
        env = "FAULT_SCENARIO_PATH"
    )]
    pub scenario: String,

    /// Path to a OpenAPI v3 specification file
    #[arg(
        long,
        help = "Path to a OpenAPI v3 specification file",
        env = "FAULT_SCENARIO_OPENAPI_V3_SPEC_FILE"
    )]
    pub spec_file: Option<String>,

    /// URL to a OpenAPI v3 specification resource
    #[arg(
        long,
        help = "URL to a OpenAPI v3 specification resource",
        env = "FAULT_SCENARIO_OPENAPI_V3_SPEC_URL"
    )]
    pub spec_url: Option<String>,
}

/// Common options for all agent commands
#[cfg(feature = "agent")]
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct AgentCommandCommon {
    /// LLM client to use
    #[arg(
        long,
        help_heading = "Agent Options",
        help = "LLM client to use.",
        env = "FAULT_AGENT_CLIENT",
        default_value_t = SupportedLLMClient::OpenAI,
        value_enum,
    )]
    pub llm_client: SupportedLLMClient,

    /// Prompt reasoning model
    #[arg(
        long,
        help_heading = "Agent Options",
        help = "LLM prompt reasoning model, used by the advise command.",
        env = "FAULT_AGENT_PROMPT_REASONING_MODEL",
        default_value = "o4-mini"
    )]
    pub llm_prompt_reasoning_model: String,

    /// Prompt chat model
    #[arg(
        long,
        help_heading = "Agent Options",
        help = "LLM prompt chat model, used by the review command.",
        env = "FAULT_AGENT_PROMPT_CHAT_MODEL",
        default_value = "gpt-4.1-mini"
    )]
    pub llm_prompt_chat_model: String,

    /// Embed model
    #[arg(
        long,
        help_heading = "Agent Options",
        help = "LLM embed model.",
        env = "FAULT_AGENT_EMBED_MODEL",
        default_value = "text-embedding-3-small"
    )]
    pub llm_embed_model: String,
}

/// Configuration for reviewing source code
#[cfg(feature = "agent")]
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct AgentReviewConfig {
    /// Path where to save the generated reviews report
    #[arg(
        long = "report",
        help = "Path where to save the generated reviews report",
        default_value = "code-review-report.md",
        env = "FAULT_AGENT_CODE_REVIEW_REPORT_FILE"
    )]
    pub report: String,

    /// Path to the scenario results file (JSON)
    #[arg(
        long,
        help = "Path to the generated json results file",
        default_value = "results.json",
        env = "FAULT_SCENARIO_RESULTS_PATH"
    )]
    pub results: String,

    /// Source index path
    #[arg(
        long,
        help = "Path to the index cache",
        default_value = "/tmp/index.db",
        env = "FAULT_AGENT_CODE_REVIEW_SOURCE_INDEX_PATH"
    )]
    pub index: String,

    /// Project source code repository directory
    #[arg(
        long = "source-dir",
        help = "Path to the repository source code directory",
        env = "FAULT_AGENT_CODE_REVIEW_SOURCE_DIR"
    )]
    pub repo: String,

    /// Source language
    #[arg(
        long = "source-lang",
        help = "Target language to index: python, rust, go, java, ...",
        env = "FAULT_AGENT_CODE_REVIEW_SOURCE_LANGUAGE"
    )]
    pub lang: String,

    /// Scenario review report
    #[arg(
        long = "scenario-review-report",
        help = "Path to the output of the scenario-review command",
        default_value = "scenario-analysis-report.md",
        env = "FAULT_AGENT_SCENARIO_REVIEW_REPORT_FILE"
    )]
    pub advices: Option<String>,
}

/// Configuration for suggesting advices on scenario reports
#[cfg(feature = "agent")]
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct AgentAdviceConfig {
    /// Path to the scenario results file (JSON)
    #[arg(
        long,
        help = "Path to the generated json results file",
        default_value = "results.json",
        env = "FAULT_SCENARIO_RESULTS_PATH"
    )]
    pub results: String,

    /// Role to influence the advice
    #[arg(
        long,
        default_value_t = ReportReviewRole::Developer,
        value_enum,
        help = "Role to influence the advice",
        env = "FAULT_AGENT_ADVICE_ROLE"
    )]
    pub role: ReportReviewRole,

    /// Path where to save the generated advice report.
    #[arg(
        long,
        help = "Path where to save the generated advice report.",
        default_value = "scenario-analysis-report.md",
        env = "FAULT_AGENT_SCENARIO_REVIEW_REPORT_FILE"
    )]
    pub report: String,
}

/// Subcommands for the fault command
#[cfg(feature = "agent")]
#[derive(Subcommand, Debug)]
pub enum AgentPlatformCommands {
    Gcp(GcpPlatformAdviceConfig),
    Kubernetes(KubernetesPlatformAdviceConfig),
}

/// Configuration for suggesting advices on your platform resources
#[cfg(feature = "agent")]
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct KubernetesPlatformAdviceConfig {
    /// Namespace
    #[arg(
        long,
        help = "Namespace.",
        env = "FAULT_AGENT_PLATFORM_ADVICE_K8S_NS",
        default_value = "default"
    )]
    pub ns: String,

    /// Path where to save the generated reviews report
    #[arg(
        long = "report",
        help = "Path where to save the generated reviews report",
        default_value = "platform-review-report.md",
        env = "FAULT_AGENT_PLATFORM_ADVICE_REPORT_FILE"
    )]
    pub report: String,

    /// Role to influence the advice
    #[arg(
        long,
        default_value_t = PlatformReviewRole::Developer,
        value_enum,
        help = "Role to influence the advice",
        env = "FAULT_AGENT_PLATFORM_ADVICE_ROLE"
    )]
    pub role: PlatformReviewRole,
}

/// Configuration for suggesting advices on your platform resources
#[cfg(feature = "agent")]
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct GcpPlatformAdviceConfig {
    /// Project
    #[arg(
        long,
        help = "Project.",
        env = "FAULT_AGENT_PLATFORM_ADVICE_GCP_PROJECT"
    )]
    pub project: String,

    /// Region
    #[arg(
        short,
        long,
        help = "Region.",
        env = "FAULT_AGENT_PLATFORM_ADVICE_GCP_REGION"
    )]
    pub region: String,

    /// Path where to save the generated reviews report
    #[arg(
        long = "report",
        help = "Path where to save the generated reviews report",
        default_value = "platform-review-report.md",
        env = "FAULT_AGENT_PLATFORM_ADVICE_REPORT_FILE"
    )]
    pub report: String,

    /// Role to influence the advice
    #[arg(
        long,
        default_value_t = PlatformReviewRole::Developer,
        value_enum,
        help = "Role to influence the advice",
        env = "FAULT_AGENT_PLATFORM_ADVICE_ROLE"
    )]
    pub role: PlatformReviewRole,
}

#[cfg(feature = "injection")]
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct FaultInjectionCommandOptions {
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

    // Packet Loss Options
    #[command(flatten)]
    pub packet_loss: PacketLossOptions,

    // Blackhole Options
    #[command(flatten)]
    pub blackhole: BlackholeOptions,
}

/// Subcommands for the fault command
#[cfg(feature = "injection")]
#[derive(Subcommand, Debug)]
pub enum FaultInjectionCommands {
    Gcp(FaultInjectionGcpConfig),
    Kubernetes(FaultInjectionKubernetesConfig),
}

#[cfg(feature = "injection")]
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct FaultInjectionGcpConfig {
    /// Project
    #[arg(long, help = "Project.", env = "FAULT_INJECTION_GCP_PROJECT")]
    pub project: String,

    /// Region
    #[arg(short, long, help = "Region.", env = "FAULT_INJECTION_GCP_REGION")]
    pub region: String,

    /// Service name
    #[arg(
        short,
        long,
        help = "Service name.",
        env = "FAULT_INJECTION_GCP_SERVICE"
    )]
    pub service: Option<String>,

    /// Traffic percentage
    #[arg(
        short,
        long,
        help = "Traffic percentage sent to the proxy.",
        env = "FAULT_INJECTION_GCP_TRAFFIC_PERCENT",
        default_value_t = 100
    )]
    pub percent: u32,

    /// Container image performing the fault
    #[arg(
        short,
        long,
        help = "Container image performing the fault.",
        env = "FAULT_INJECTION_GCP_IMAGE"
    )]
    pub image: String,

    /// How long to run the injection for
    #[arg(
        long,
        help = "How long to run the injection for.",
        env = "FAULT_INJECTION_GCP_DURATION",
        value_parser
    )]
    pub duration: Option<String>,

    #[command(flatten)]
    pub options: Box<FaultInjectionCommandOptions>,
}

#[cfg(feature = "injection")]
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct FaultInjectionKubernetesConfig {
    /// Namespace
    #[arg(
        long,
        help = "Namespace.",
        env = "FAULT_INJECTION_K8S_NS",
        default_value = "default"
    )]
    pub ns: String,

    /// Service to inject fault into
    #[arg(
        short,
        long,
        help = "Service to inject fault into.",
        env = "FAULT_INJECTION_K8S_SERVICE"
    )]
    pub service: Option<String>,

    /// Container image performing the fault
    #[arg(
        short,
        long,
        help = "Container image performing the fault.",
        env = "FAULT_INJECTION_K8S_IMAGE",
        default_value = "ghcr.io/rebound-how/fault:latest"
    )]
    pub image: String,

    /// How long to run the injection for
    #[arg(
        long,
        help = "How long to run the injection for.",
        env = "FAULT_INJECTION_K8S_DURATION",
        value_parser
    )]
    pub duration: Option<String>,

    #[command(flatten)]
    pub options: Box<FaultInjectionCommandOptions>,
}

/// Configuration for executing the demo server
#[cfg(feature = "demo")]
#[derive(Args, Clone, Debug, Serialize, Deserialize)]
pub struct DemoConfig {
    /// Listening address for the demo server
    #[arg(
        help = "Listening address for the proxy server. Overrides the one defined in the scenario.",
        default_value = "127.0.0.1",
        value_parser,
        env = "FAULT_DEMO_ADDR"
    )]
    pub address: String,

    /// Listening port for the demo server
    #[arg(
        help = "Listening address for the proxy server. Overrides the one defined in the scenario.",
        default_value_t = 7070,
        value_parser,
        env = "FAULT_DEMO_PORT"
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

#[cfg(feature = "injection")]
impl FaultInjectionCommandOptions {
    pub fn to_environment_variables(&self) -> BTreeMap<String, String> {
        let mut map = BTreeMap::<String, String>::default();

        if self.bandwidth.enabled {
            map.insert("FAULT_WITH_BANDWIDTH".to_string(), "true".to_string());
            map.insert(
                "FAULT_BANDWIDTH_SIDE".to_string(),
                self.bandwidth.side.to_string(),
            );
            map.insert(
                "FAULT_BANDWIDTH_DIRECTION".to_string(),
                self.bandwidth.bandwidth_direction.to_string(),
            );
            map.insert(
                "FAULT_BANDWIDTH_RATE".to_string(),
                self.bandwidth.bandwidth_rate.to_string(),
            );
            map.insert(
                "FAULT_BANDWIDTH_UNIT".to_string(),
                self.bandwidth.bandwidth_unit.to_string(),
            );

            match &self.bandwidth.bandwidth_sched {
                Some(sched) => map.insert(
                    "FAULT_BANDWIDTH_SCHED".to_string(),
                    sched.to_string(),
                ),
                None => None,
            };
        }

        if self.jitter.enabled {
            map.insert("FAULT_WITH_JITTER".to_string(), "true".to_string());
            map.insert(
                "FAULT_JITTER_SIDE".to_string(),
                self.jitter.jitter_side.to_string(),
            );
            map.insert(
                "FAULT_JITTER_DIRECTION".to_string(),
                self.jitter.jitter_direction.to_string(),
            );
            map.insert(
                "FAULT_JITTER_AMPLITUDE".to_string(),
                self.jitter.jitter_amplitude.to_string(),
            );
            map.insert(
                "FAULT_JITTER_FREQ".to_string(),
                self.jitter.jitter_frequency.to_string(),
            );

            match &self.jitter.jitter_sched {
                Some(sched) => map.insert(
                    "FAULT_JITTER_SCHED".to_string(),
                    sched.to_string(),
                ),
                None => None,
            };
        }

        if self.packet_loss.enabled {
            map.insert(
                "FAULT_WITH_PACKET_LOSS".to_string(),
                "true".to_string(),
            );
            map.insert(
                "FAULT_PACKET_LOSS_SIDE".to_string(),
                self.packet_loss.side.to_string(),
            );
            map.insert(
                "FAULT_PACKET_LOSS_DIRECTION".to_string(),
                self.packet_loss.packet_loss_direction.to_string(),
            );

            match &self.packet_loss.packet_loss_sched {
                Some(sched) => map.insert(
                    "FAULT_PACKET_LOSS_SCHED".to_string(),
                    sched.to_string(),
                ),
                None => None,
            };
        }

        if self.blackhole.enabled {
            map.insert("FAULT_WITH_BLACKHOLE".to_string(), "true".to_string());
            map.insert(
                "FAULT_BLACKHOLE_SIDE".to_string(),
                self.blackhole.side.to_string(),
            );
            map.insert(
                "FAULT_BLACKHOLE_DIRECTION".to_string(),
                self.blackhole.blackhole_direction.to_string(),
            );

            match &self.blackhole.blackhole_sched {
                Some(sched) => map.insert(
                    "FAULT_BLACKHOLE_SCHED".to_string(),
                    sched.to_string(),
                ),
                None => None,
            };
        }

        if self.http_error.enabled {
            map.insert("FAULT_WITH_HTTP_FAULT".to_string(), "true".to_string());

            map.insert(
                "FAULT_HTTP_FAULT_PROBABILITY".to_string(),
                self.http_error.http_response_trigger_probability.to_string(),
            );

            map.insert(
                "FAULT_HTTP_FAULT_STATUS".to_string(),
                self.http_error.http_response_status_code.to_string(),
            );

            if let Some(body) = &self.http_error.http_response_body {
                map.insert("FAULT_HTTP_FAULT_BODY".to_string(), body.clone());
            }

            match &self.http_error.http_response_sched {
                Some(sched) => map.insert(
                    "FAULT_HTTP_FAULT_SCHED".to_string(),
                    sched.to_string(),
                ),
                None => None,
            };
        }

        if self.latency.enabled {
            map.insert("FAULT_WITH_LATENCY".to_string(), "true".to_string());
            map.insert(
                "FAULT_LATENCY_SIDE".to_string(),
                self.latency.side.to_string(),
            );
            map.insert(
                "FAULT_LATENCY_DIRECTION".to_string(),
                self.latency.latency_direction.to_string(),
            );

            map.insert(
                "FAULT_LATENCY_DISTRIBUTION".to_string(),
                self.latency.latency_distribution.to_string(),
            );

            if let Some(v) = self.latency.latency_mean {
                map.insert("FAULT_LATENCY_MEAN".to_string(), v.to_string());
            }

            if let Some(v) = self.latency.latency_stddev {
                map.insert(
                    "FAULT_LATENCY_STANDARD_DEVIATION".to_string(),
                    v.to_string(),
                );
            }

            if let Some(v) = self.latency.latency_shape {
                map.insert("FAULT_LATENCY_SHAPE".to_string(), v.to_string());
            }

            if let Some(v) = self.latency.latency_scale {
                map.insert("FAULT_LATENCY_SCALE".to_string(), v.to_string());
            }

            if let Some(v) = self.latency.latency_min {
                map.insert("FAULT_LATENCY_MIN".to_string(), v.to_string());
            }

            if let Some(v) = self.latency.latency_max {
                map.insert("FAULT_LATENCY_MAX".to_string(), v.to_string());
            }

            if self.latency.per_read_write {
                map.insert(
                    "FAULT_LATENCY_PER_READ_WRITE".to_string(),
                    "true".to_string(),
                );
            }

            match &self.latency.latency_sched {
                Some(sched) => map.insert(
                    "FAULT_LATENCY_SCHED".to_string(),
                    sched.to_string(),
                ),
                None => None,
            };
        }

        map
    }
}
