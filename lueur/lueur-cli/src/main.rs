// used by duration to access as_millis_f64() which is available in edition2024
#![feature(duration_millis_float)]

// necessary to use is_global on IPv4 addr
// https://github.com/rust-lang/rust/issues/27709
#![feature(ip)]

mod cli;
mod config;
mod demo;
#[cfg(all(
    target_os = "linux",
    any(feature = "stealth", feature = "stealth-auto-build")
))]
mod ebpf;
mod errors;
mod event;
mod fault;
mod logging;
mod plugin;
mod proxy;
mod reporting;
mod resolver;
mod scenario;
mod termui;
mod types;

use std::collections::HashMap;
use std::fs::File;
use std::io::Write;
use std::net::IpAddr;
use std::net::SocketAddr;
use std::path::Path;
use std::sync::Arc;
use std::sync::Mutex;
use std::time::Duration;
use std::time::Instant;

use anyhow::Result;
#[cfg(all(
    target_os = "linux",
    any(feature = "stealth", feature = "stealth-auto-build")
))]
use aya::Ebpf;
use clap::Parser;
use cli::Cli;
use cli::Commands;
use cli::DemoCommands;
use cli::ProxyAwareCommandCommon;
use cli::RunCommandOptions;
use cli::ScenarioCommands;
use colorful::Color;
use colorful::Colorful;
use colorful::ExtraColorInterface;
use config::ProxyConfig;
use errors::ProxyError;
use event::TaskManager;
use indicatif::MultiProgress;
use indicatif::ProgressBar;
use indicatif::ProgressStyle;
use logging::init_meter_provider;
use logging::init_subscriber;
use logging::init_tracer_provider;
use logging::setup_logging;
use logging::shutdown_tracer;
use opentelemetry_sdk::metrics::SdkMeterProvider;
use opentelemetry_sdk::trace::SdkTracerProvider;
use proxy::ProxyState;
#[cfg(all(
    target_os = "linux",
    any(feature = "stealth", feature = "stealth-auto-build")
))]
use proxy::run_ebpf_proxy;
use proxy::run_proxy;
use reporting::OutputFormat;
use reporting::Report;
use reporting::ReportItem;
use reporting::ReportItemExpectation;
use reporting::ReportItemExpectationDecision;
use reporting::ReportItemMetrics;
use reporting::ReportItemMetricsFaults;
use reporting::build_report_output;
use reporting::pretty_report;
use scenario::ScenarioEventManager;
use scenario::ScenarioItemLifecycle;
use scenario::ScenarioItemLifecycleFaults;
use scenario::build_item_list;
use scenario::count_scenario_items;
use scenario::execute_item;
use scenario::handle_scenario_events;
use scenario::load_scenarios;
use termui::handle_displayable_events;
use termui::quiet_handle_displayable_events;
use tokio::sync::broadcast;
use tokio::sync::watch;
use tokio::task;
use tokio_stream::StreamExt;
use tracing::error;
use types::LatencyDistribution;
use types::ProxyAddrConfig;
use types::EbpfProxyAddrConfig;
use url::Url;

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    let (_file_guard, _stdout_guard, log_layers) =
        setup_logging(cli.log_file, cli.log_stdout, cli.log_level).unwrap();

    let mut meter_provider: Option<SdkMeterProvider> = None;
    let mut tracer_provider: Option<SdkTracerProvider> = None;

    if cli.with_otel {
        meter_provider = Some(init_meter_provider());
        tracer_provider = Some(init_tracer_provider());
    }

    let _ = init_subscriber(log_layers, &tracer_provider, &meter_provider);

    let (proxy_shutdown_tx, proxy_shutdown_rx) = broadcast::channel::<()>(1);
    let (task_manager, receiver) = TaskManager::new(1000);
    let (config_tx, config_rx) = watch::channel(ProxyConfig::default());

    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]
    let mut _guard: Option<Ebpf> = None;

    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]
    let mut _ebpf_proxy_guard: task::JoinHandle<
        std::result::Result<(), ProxyError>,
    >;

    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]
    let (ebpf_proxy_shutdown_tx, ebpf_proxy_shutdown_rx) =
        broadcast::channel::<()>(1);

    match &cli.command {
        Commands::Run { options } => {
            let _progress_guard;

            if options.no_ui {
                _progress_guard =
                    task::spawn(quiet_handle_displayable_events(receiver));
            } else {
                _progress_guard =
                    task::spawn(handle_displayable_events(receiver));
            }

            let proxy_nic_config = get_proxy_address(&options.common);

            let stealth_mode = is_stealth(&options);

            let app_state = initialize_application_state(&options.common, stealth_mode).await;

            let _proxy_guard = initialize_proxy(
                &proxy_nic_config,
                app_state.clone(),
                proxy_shutdown_rx,
                config_rx.clone(),
                task_manager.clone(),
            )
            .await;

            #[cfg(all(
                target_os = "linux",
                any(feature = "stealth", feature = "stealth-auto-build")
            ))]
            {
                if stealth_mode {
                    if options.stealth.ebpf_process_name.is_none() {
                        tracing::error!(
                            "In stealth mode, you must pass a process name"
                        );
                    } else {
                        match ebpf::get_ebpf_proxy(&proxy_nic_config, options.stealth.ebpf_proxy_iface.clone(), options.stealth.ebpf_proxy_ip.clone(), options.stealth.ebpf_proxy_port) {
                            Ok(Some(ebpf_proxy_config)) => {
                                _ebpf_proxy_guard = initialize_ebpf_proxy(
                                    &ebpf_proxy_config,
                                    app_state.clone(),
                                    ebpf_proxy_shutdown_rx,
                                    config_rx.clone(),
                                    task_manager.clone(),
                                )
                                .await
                                .unwrap();
        
                                _guard = ebpf::initialize_stealth(
                                    &options.common,
                                    &options.stealth,
                                    &ebpf_proxy_config,
                                );
                            }
                            Ok(None) => {
                                tracing::warn!(
                                    "Failed to configure the eBPF proxy. Disabling stealth mode"
                                );
                            }
                            Err(_) => {
                                tracing::warn!(
                                    "Failed to configure the eBPF proxy. Disabling stealth mode"
                                );
                            }
                        };
                    }
                }
            }

            let cmd_config: ProxyConfig = options.into();

            if config_tx.send(cmd_config).is_err() {
                error!("Proxy configuration listener has been shut down.");
            }

            let hosts = app_state.proxy_state.upstream_hosts.read().await;
            let upstreams = (*hosts).clone();

            if !options.no_ui {
                proxy_prelude(
                    proxy_nic_config.proxy_address(),
                    &options,
                    &upstreams,
                );
            }

            tokio::signal::ctrl_c()
                .await
                .map_err(|e| {
                    ProxyError::Internal(format!(
                        "Failed to listen for shutdown signal: {}",
                        e
                    ))
                })
                .unwrap();

            tracing::info!("Shutdown signal received. Initiating shutdown.");
        }
        Commands::Demo(demo_cmd) => match demo_cmd {
            DemoCommands::Run(demo_config) => {
                demo_prelude(format!(
                    "{}:{}",
                    demo_config.address, demo_config.port
                ));

                let _ = demo::run((*demo_config).clone()).await;
            }
        },
        Commands::Scenario { scenario, common } => match scenario {
            ScenarioCommands::Run(config) => {
                let start = Instant::now();

                let proxy_nic_config = get_proxy_address(common);

                let m = MultiProgress::new();

                let app_state = initialize_application_state(&common, false).await;

                let _proxy_guard = initialize_proxy(
                    &proxy_nic_config,
                    app_state.clone(),
                    proxy_shutdown_rx,
                    config_rx,
                    task_manager.clone(),
                )
                .await;

                let mut scenarios = load_scenarios(Path::new(&config.scenario));

                println!(
                    "\n{}\n",
                    "================ Running Scenarios ================".dim()
                );

                let queue =
                    Arc::new(Mutex::new(Vec::<ScenarioItemLifecycle>::new()));

                let (event_manager, scenario_event_receiver) =
                    ScenarioEventManager::new(500);

                let _scenario_event_progress_guard =
                    tokio::spawn(handle_scenario_events(
                        scenario_event_receiver,
                        receiver,
                        queue.clone(),
                    ));

                let mut results = Vec::new();

                while let Some(candidate) = scenarios.next().await {
                    match candidate {
                        Ok(scenario) => {
                            let mut progress_state = String::new();

                            let title = scenario.clone().title;

                            let n = count_scenario_items(&scenario); //scenario.scenarios.len() as u64;

                            let pb = m.add(ProgressBar::new(n));
                            pb.enable_steady_tick(Duration::from_millis(80));
                            pb.set_style(
                                ProgressStyle::with_template(
                                    "{spinner:.green} {pos:>2}/{len:2} {msg}",
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

                            let key = title.clone();
                            let msg = format!("{} ", key.clone());

                            for item in scenario.scenarios.into_iter() {
                                let items = build_item_list(item);

                                for i in items {
                                    let report = execute_item(
                                        proxy_nic_config.proxy_address(),
                                        config_tx.clone(),
                                        i,
                                        app_state.clone(),
                                        event_manager.clone(),
                                    )
                                    .await;

                                    let mut events = queue.lock().unwrap();
                                    let event = events.pop();

                                    let metrics = match event {
                                        Some(e) => {
                                            match report.metrics.clone() {
                                                Some(m) => {
                                                    Some(ReportItemMetrics {
                                                        dns: e.dns_timing,
                                                        protocol: m.protocol,
                                                        ttfb: m.ttfb,
                                                        total_time: m
                                                            .total_time,
                                                        faults: map_faults(
                                                            &e.faults,
                                                        ),
                                                    })
                                                }
                                                None => None,
                                            }
                                        }
                                        None => None,
                                    };

                                    match &report.expect {
                                        Some(expect) => {
                                            match expect {
                                                ReportItemExpectation::Http { wanted: _, got } => {
                                                    match got {
                                                        Some(status) => {
                                                            if status.decision == ReportItemExpectationDecision::Failure {
                                                                progress_state = format!("{}{}", progress_state, "▮".to_string().red());
                                                            } else if status.decision == ReportItemExpectationDecision::Success {
                                                                progress_state = format!("{}{}", progress_state, "▮".to_string().green());
                                                            } else {
                                                                progress_state = format!("{}{}", progress_state, "▮".to_string().grey0());
                                                            }
                                                        },
                                                        None => progress_state = format!("{}{}", progress_state, "▮".to_string().grey0())
                                                    }
                                                }
                                            }
                                        }
                                        None => progress_state = format!("{} {}", progress_state, "▮".to_string().grey0())
                                    }

                                    results.push(ReportItem::new(
                                        title.clone(),
                                        metrics,
                                        report,
                                    ));

                                    pb.inc(1);
                                    pb.set_message(format!(
                                        "{} {}",
                                        msg.clone(),
                                        progress_state
                                    ));
                                }
                            }

                            pb.finish();
                        }
                        Err(e) => error!("Failed to load scenario: {:?}", e),
                    }
                }

                let final_report =
                    Report { plugins: Vec::new(), items: results };

                final_report.save(&config.result).unwrap();

                let report_output = build_report_output(&final_report).unwrap();

                println!("\n");
                println!(
                    "{}\n",
                    "===================== Summary =====================".dim()
                );

                println!(
                    "Tests run: {}, Tests failed: {}",
                    report_output.summary.total_tests.to_string().cyan(),
                    report_output.summary.total_failures.to_string().red()
                );
                println!("Total time: {:.1}s", start.elapsed().as_secs_f64());

                match get_output_format_result(config.report.as_str()) {
                    Ok(fmt) => match pretty_report(&report_output, &fmt) {
                        Ok(computed_report) => {
                            let path = &config.report;
                            let mut file = File::create(path).unwrap();
                            let _ = write!(file, "{}", computed_report);
                            println!(
                                "\nReport saved as {}",
                                config.report.clone().yellow()
                            );
                        }
                        Err(e) => {
                            tracing::error!("Failed to generated report: {}", e)
                        }
                    },
                    Err(_) => tracing::error!("Unsupported report format"),
                }
            }
        },
    }

    match proxy_shutdown_tx.send(()) {
        Ok(_) => tracing::debug!("Shutdown notified."),
        Err(e) => tracing::warn!("Failed to notify shutdown {}", e),
    }

    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]
    {
        match ebpf_proxy_shutdown_tx.send(()) {
            Ok(_) => tracing::debug!("Shutdown of ebpf notified."),
            Err(e) => tracing::warn!("Failed to notify ebpf shutdown {}", e),
        }
    }

    drop(task_manager);

    shutdown_tracer(tracer_provider, meter_provider);

    Ok(())
}

fn map_faults(
    original_faults: &HashMap<usize, ScenarioItemLifecycleFaults>,
) -> Vec<ReportItemMetricsFaults> {
    original_faults
        .iter()
        .map(|(_key, value)| value.to_report_metrics_faults())
        .collect()
}

#[derive(Debug, Clone)]
struct AppState {
    pub proxy_state: Arc<ProxyState>,
}

#[cfg(all(target_os = "linux", feature = "stealth"))]
fn is_stealth(cli: &RunCommandOptions) -> bool {
    cli.stealth.ebpf
}

#[cfg(all(not(target_os = "linux"), feature = "stealth"))]
fn is_stealth(cli: &RunCommandOptions) -> bool {
    false
}

#[cfg(all(target_os = "linux", not(feature = "stealth")))]
fn is_stealth(cli: &RunCommandOptions) -> bool {
    false
}

#[cfg(not(target_os = "linux"))]
fn is_stealth(cli: &RunCommandOptions) -> bool {
    false
}

async fn initialize_application_state(
    cli: &ProxyAwareCommandCommon, is_stealth: bool
) -> AppState {
    // Initialize shared state with empty configuration
    let state = Arc::new(ProxyState::new(is_stealth));

    //let rpc_plugin = load_remote_plugins(cli.grpc_plugins.clone()).await;
    //state.update_plugins(vec![rpc_plugin]).await;

    let upstream_hosts = cli.upstream_hosts.clone();
    let upstreams: Vec<String> =
        upstream_hosts.iter().map(|h| upstream_to_addr(h).unwrap()).collect();

    state.update_upstream_hosts(upstreams).await;

    AppState { proxy_state: state }
}

async fn initialize_proxy(
    proxy_nic_config: &ProxyAddrConfig,
    state: AppState,
    shutdown_rx: broadcast::Receiver<()>,
    config_rx: watch::Receiver<ProxyConfig>,
    task_manager: Arc<TaskManager>,
) -> Result<task::JoinHandle<std::result::Result<(), ProxyError>>> {
    let proxy_address = proxy_nic_config.proxy_address();

    // Create a oneshot channel for readiness signaling
    let (readiness_tx, readiness_rx) = oneshot::channel::<()>();

    let handle = tokio::spawn(run_proxy(
        proxy_address.clone(),
        state.proxy_state,
        shutdown_rx,
        readiness_tx,
        config_rx,
        task_manager,
    ));

    // Wait for the proxy to signal readiness
    let _ = readiness_rx.await.map_err(|e| {
        ProxyError::Internal(format!(
            "Failed to receive readiness signal: {}",
            e
        ))
    });

    tracing::info!("Proxy server is listening on {}", proxy_address);

    Ok(handle)
}

#[cfg(all(
    target_os = "linux",
    any(feature = "stealth", feature = "stealth-auto-build")
))]
async fn initialize_ebpf_proxy(
    ebpf_proxy_config: &EbpfProxyAddrConfig,
    state: AppState,
    shutdown_rx: broadcast::Receiver<()>,
    config_rx: watch::Receiver<ProxyConfig>,
    task_manager: Arc<TaskManager>,
) -> Result<task::JoinHandle<std::result::Result<(), ProxyError>>> {
    let proxy_address = ebpf_proxy_config.proxy_address();

    // Create a oneshot channel for readiness signaling
    let (readiness_tx, readiness_rx) = oneshot::channel::<()>();

    let handle = tokio::spawn(run_ebpf_proxy(
        proxy_address.clone(),
        state.proxy_state,
        shutdown_rx,
        readiness_tx,
        config_rx,
        task_manager,
    ));

    // Wait for the proxy to signal readiness
    let _ = readiness_rx.await.map_err(|e| {
        ProxyError::Internal(format!(
            "Failed to receive readiness signal: {}",
            e
        ))
    });

    tracing::info!("eBPF Proxy server is listening on {}", proxy_address);

    Ok(handle)
}

fn upstream_to_addr(
    host: &String,
) -> Result<String, Box<dyn std::error::Error>> {
    let url_str = if host.contains("://") {
        host.to_string()
    } else {
        format!("scheme://{}", host)
    };

    let url = Url::parse(&url_str)?;

    let host = url.host_str().ok_or("Missing host")?.to_string();

    let port = url.port_or_known_default().unwrap();

    Ok(format!("{}:{}", host, port))
}

fn proxy_prelude(
    proxy_address: String,
    opts: &RunCommandOptions,
    upstreams: &Vec<String>,
) {
    let g = "lueur".gradient(Color::LightYellow3);
    let r = "Your Resiliency Exploration Tool".gradient(Color::Purple3);
    let a = format!("http://{}", proxy_address).cyan();
    println!(
        "
    Welcome to {} — {}!

    To get started, route your HTTP/HTTPS requests through:
    {}

    As you send requests, lueur will simulate network conditions
    so you can see how your application copes.

    Ready when you are — go ahead and make some requests!
        ",
        g, r, a
    );

    // Summary header with a bit of color
    println!("{}", "\n    Configured faults:".bold().white());

    // HTTP Response Fault
    if opts.http_error.enabled {
        if let Some(body) = &opts.http_error.http_response_body {
            println!(
                "{}",
                format!(
                    "     - {}: {}: {}, {}: {}, {}: {}",
                    "HTTP Response".light_blue(),
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
                    "HTTP Response".light_blue(),
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
            "Latency".light_blue(),
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
                "Bandwidth".light_blue(),
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
                "Jitter".light_blue(),
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
                "DNS".light_blue(),
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
                "Packet Loss".light_blue(),
                "side".dim(),
                opts.packet_loss.side,
                "direction".dim(),
                opts.packet_loss.packet_loss_direction
            )
        );
    }

    let mut noop = false;

    // If no fault is enabled, let the user know
    if !opts.http_error.enabled
        && !opts.latency.enabled
        && !opts.bandwidth.enabled
        && !opts.jitter.enabled
        && !opts.dns.enabled
        && !opts.packet_loss.enabled
    {
        println!("    {}", " No faults configured.".dim().hsl(0.39, 1.0, 0.50));
        noop = true;
    }

    println!("{}", "\n    Hosts Covered By The Faults:".bold().white());
    if !upstreams.is_empty() {
        for host in upstreams {
            println!("     - {}", host.clone().cyan());
        }
        println!("\n");
    } else {
        println!(
            "    {}",
            " No upstream hosts configured.".dim().hsl(0.39, 1.0, 0.50)
        );
        noop = true;
    }

    if noop {
        println!(
            "\n    {}{}\n",
            "\n    💡 The proxy is not configured to impact any traffic.\n    You may want to try setting some parameters. For instance:\n",
            "\n    lueur run --with-latency --latency-mean 300 --upstream http://localhost:7070"
        )
    }
}

fn demo_prelude(demo_address: String) {
    let g = "lueur".gradient(Color::Plum4);
    println!(
        "
    Welcome to {}, this demo application is here to let you explore lueur's capabilities.

    Here are a few examples:

    export HTTP_PROXY=http://localhost:8080
    export HTTPS_PROXY=http://localhost:8080

    curl -x ${{HTTP_PROXY}} http://{demo_address}/
    curl -x ${{HTTP_PROXY}} http://{demo_address}/ping
    curl -x ${{HTTP_PROXY}} http://{demo_address}/ping/myself
    curl -x ${{HTTP_PROXY}} --json '{{\"content\": \"hello\"}}' http://{demo_address}/uppercase

        ", g,
    );
}

fn get_output_format_result(file_path: &str) -> Result<OutputFormat, String> {
    Path::new(file_path)
        .extension()
        .and_then(|ext| ext.to_str())
        .ok_or_else(|| "File extension is missing or invalid.".to_string())
        .and_then(|ext_str| match ext_str.to_lowercase().as_str() {
            "md" | "markdown" => Ok(OutputFormat::Markdown),
            "txt" => Ok(OutputFormat::Text),
            "html" | "htm" => Ok(OutputFormat::Html),
            "json" => Ok(OutputFormat::Json),
            "yaml" | "yml" => Ok(OutputFormat::Yaml),
            other => Err(format!("Unrecognized file extension: '{}'", other)),
        })
}

fn get_proxy_address(common: &ProxyAwareCommandCommon) -> ProxyAddrConfig {
    let proxy_address = common.proxy_address.clone();

    let addr = proxy_address.unwrap_or("127.0.0.1:8080".to_string());
    let socket_addr: SocketAddr = addr
        .parse()
        .map_err(|e| format!("Invalid proxy address '{}': {}", addr, e))
        .unwrap();
    let sock_proxy_ip = socket_addr.ip();
    let proxy_port = socket_addr.port();

    let proxy_ip = match sock_proxy_ip {
        IpAddr::V4(ipv4) => ipv4,
        IpAddr::V6(_ipv6) => {
            panic!("IPV6 addresses are not supported for proxy");
        }
    };

    ProxyAddrConfig { proxy_ip, proxy_port }
}
