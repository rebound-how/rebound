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
mod sched;
mod state;
mod termui;
mod types;

use std::collections::HashMap;
use std::fs::File;
use std::io::Write;
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
use cli::RunCommandOptions;
use cli::ScenarioCommands;
use colorful::Colorful;
use colorful::ExtraColorInterface;
use config::ProxyConfig;
use errors::ProxyError;
use event::TaskManager;
use fault::FaultInjector;
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
use parse_duration::parse;
use plugin::load_injectors;
use proxy::monitor_and_update_proxy_config;
#[cfg(all(
    target_os = "linux",
    any(feature = "stealth", feature = "stealth-auto-build")
))]
use proxy::protocols::ebpf::init::initialize_ebpf_proxy;
use proxy::protocols::http::init::get_http_proxy_address;
use proxy::protocols::http::init::initialize_http_proxy;
use proxy::protocols::tcp::init::initialize_tcp_proxies;
use proxy::protocols::tcp::init::parse_proxy_protocols;
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
use sched::build_schedule_events;
use sched::run_fault_schedule;
use state::initialize_proxy_state;
use termui::demo_prelude;
use termui::full_progress;
use termui::get_output_format_result;
use termui::lean_progress;
use termui::proxy_prelude;
use termui::quiet_handle_displayable_events;
use tokio::sync::broadcast;
use tokio::sync::watch;
use tokio::task;
use tokio::time::sleep;
use tokio_stream::StreamExt;
use tracing::error;

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

    let (proxy_shutdown_tx, proxy_shutdown_rx) = broadcast::channel::<()>(5);
    let (task_manager, receiver) = TaskManager::new(5000);
    let (config_tx, config_rx) = watch::channel((
        ProxyConfig::default(),
        Vec::<Box<dyn FaultInjector>>::new(),
    ));

    let _fault_schedule_handle;
    let _progress_guard;

    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]
    let mut _guard: Option<Ebpf> = None;

    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]
    let mut _ebpf_proxy_guard: task::JoinHandle<Result<(), ProxyError>>;

    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]
    let (ebpf_proxy_shutdown_tx, ebpf_proxy_shutdown_rx) =
        broadcast::channel::<()>(1);

    match &cli.command {
        Commands::Run { options } => {
            // if we are in stealth mode, we'll start the ebpf layer as well
            let stealth_mode = is_stealth(options);

            // initiliaze a default state
            // By default we mean that it doesn't know yet about the user
            // input and therefore has no faults configured
            let proxy_state =
                state::initialize_proxy_state(&options.common, stealth_mode)
                    .await?;

            // we keep an eye on changes in the fault configuration
            // so we set the proxy state accordingly
            tokio::spawn(monitor_and_update_proxy_config(
                proxy_state.clone(),
                config_rx,
            ));

            // if the user configured remote plugins, let's connect and
            // initialize them as if they were fault injectors as
            // well
            if !options.common.grpc_plugins.clone().is_empty() {
                let manager = proxy_state.rpc_manager.clone();

                // remote plugins may come and go. We adjust the proxy state
                // accordingly every 10s or so
                tokio::spawn(async move {
                    let mut interval =
                        tokio::time::interval(Duration::from_secs(10));

                    loop {
                        interval.tick().await;
                        let mut manager = manager.write().await;
                        manager.supervise_remote_plugins().await;
                    }
                });
            }

            // it's time to start our HTTP proxies
            let http_proxy_nic_config = get_http_proxy_address(&options.common);
            let _http_proxy_guard = initialize_http_proxy(
                &http_proxy_nic_config,
                proxy_state.clone(),
                proxy_shutdown_tx.subscribe(),
                task_manager.clone(),
            )
            .await;

            // we now also start any other proxy that the user has requested us
            // to setup
            let mut proxied_protos = Vec::new();
            if !options.common.proxy_protocols.is_empty() {
                proxied_protos = parse_proxy_protocols(
                    options.common.proxy_protocols.clone(),
                )
                .await?;
                let _tcp_proxy_guard = initialize_tcp_proxies(
                    proxied_protos.clone(),
                    proxy_state.clone(),
                    proxy_shutdown_tx.clone(),
                    task_manager.clone(),
                )
                .await;
            }

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
                        match ebpf::get_ebpf_proxy(
                            &http_proxy_nic_config,
                            options.stealth.ebpf_proxy_iface.clone(),
                            options.stealth.ebpf_proxy_ip.clone(),
                            options.stealth.ebpf_proxy_port,
                        ) {
                            Ok(Some(ebpf_proxy_config)) => {
                                _ebpf_proxy_guard = initialize_ebpf_proxy(
                                    &ebpf_proxy_config,
                                    proxy_state.clone(),
                                    ebpf_proxy_shutdown_rx,
                                    task_manager.clone(),
                                )
                                .await
                                .unwrap();

                                _guard = ebpf::initialize_stealth(
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

            // let's turn the cli flags into a proxy configuration we can work
            // with
            let proxy_config = options.into();

            // load the configured injectors
            let injectors: Vec<Box<dyn FaultInjector>> =
                load_injectors(&proxy_config);

            // send the whole thing so the state can record them
            if config_tx.send((proxy_config, injectors.clone())).is_err() {
                error!("Proxy configuration listener has been shut down.");
            }

            // Let's get some data ready for the UI
            let total_duration =
                options.common.duration.as_ref().map(|s| parse(s).unwrap());
            let fault_schedule =
                build_schedule_events(options, total_duration)?;

            let schedule_for_prelude = fault_schedule.clone();
            _fault_schedule_handle = tokio::spawn(run_fault_schedule(
                fault_schedule,
                proxy_state.clone(),
                injectors,
            ));

            let faults_scheduled = !schedule_for_prelude.is_empty();

            if !options.ui.no_ui {
                let hosts = proxy_state.upstream_hosts.load_full();
                let upstreams = (*hosts).clone();

                proxy_prelude(
                    http_proxy_nic_config.proxy_address(),
                    proxied_protos.clone(),
                    proxy_state.clone().rpc_manager.clone(),
                    options,
                    &upstreams,
                    schedule_for_prelude,
                    total_duration,
                    options.ui.tail,
                )
                .await;
            }

            if options.ui.no_ui {
                _progress_guard =
                    task::spawn(quiet_handle_displayable_events(receiver));
            } else if options.ui.tail {
                _progress_guard = task::spawn(full_progress(
                    proxy_shutdown_tx.subscribe(),
                    receiver,
                ));
            } else {
                _progress_guard = task::spawn(lean_progress(
                    task_manager.new_subscriber(),
                    proxy_shutdown_tx.subscribe(),
                    total_duration,
                    faults_scheduled,
                ));
            }

            // okay at this stage, we have now displayed our UI
            // and told the user they can start using the proxy

            // if the user gave us a duration, let's wait until it completes
            // otherwise, let's wait for a sigint signal
            match total_duration {
                Some(d) => {
                    tokio::select! {
                        _ = tokio::signal::ctrl_c() => {
                            tracing::info!("Shutdown signal received. Initiating shutdown.");
                        }

                        _ = sleep(d) => {
                            tracing::info!("Time's up! Shutting down now.");
                        }
                    }
                }
                None => {
                    if let Err(e) = tokio::signal::ctrl_c().await {
                        tracing::warn!(
                            "Error listening for shutdown signal: {}",
                            e
                        );
                    } else {
                        tracing::info!(
                            "Shutdown signal received. Initiating shutdown."
                        );
                    }
                }
            }
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

                let proxy_nic_config = get_http_proxy_address(common);

                let m = MultiProgress::new();

                let app_state = initialize_proxy_state(common, false).await?;

                tokio::spawn(monitor_and_update_proxy_config(
                    app_state.clone(),
                    config_rx,
                ));

                let _proxy_guard = initialize_http_proxy(
                    &proxy_nic_config,
                    app_state.clone(),
                    proxy_shutdown_rx,
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
    };

    match proxy_shutdown_tx.send(()) {
        Ok(_) => tracing::debug!("Shutdown notified."),
        Err(e) => tracing::warn!("Failed to notify shutdown {}", e),
    };

    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]
    {
        match ebpf_proxy_shutdown_tx.send(()) {
            Ok(_) => tracing::debug!("Shutdown of ebpf notified."),
            Err(e) => tracing::warn!("Failed to notify ebpf shutdown {}", e),
        };
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
