// used by duration to access as_millis_f64() which is available in edition2024
#![feature(duration_millis_float)]
// necessary to use is_global on IPv4 addr
// https://github.com/rust-lang/rust/issues/27709
#![feature(ip)]

#[cfg(feature = "agent")]
mod agent;
mod cli;
mod config;
mod demo;
#[cfg(feature = "discovery")]
mod discovery;
#[cfg(all(
    target_os = "linux",
    any(feature = "stealth", feature = "stealth-auto-build")
))]
mod ebpf;
mod errors;
mod event;
mod fault;
#[cfg(feature = "discovery")]
mod inject;
mod logging;
mod plugin;
mod proxy;
mod report;
mod resolver;
mod scenario;
mod sched;
mod state;
mod termui;
mod types;

use std::collections::BTreeMap;
use std::fs::File;
use std::io::BufReader;
use std::path::Path;
use std::str::FromStr;
use std::sync::Arc;
use std::time::Duration;
use std::time::Instant;

#[cfg(feature = "agent")]
use agent::insight::ReviewEventPhase;
#[cfg(feature = "agent")]
use agent::suggestion::CodeReviewEventPhase;
use anyhow::Result;
use anyhow::anyhow;
#[cfg(all(
    target_os = "linux",
    any(feature = "stealth", feature = "stealth-auto-build")
))]
use aya::Ebpf;
use chrono::Utc;
use clap::Parser;
use cli::Cli;
use cli::Commands;
use cli::DemoCommands;
use cli::RunCommandOptions;
use cli::ScenarioCommands;
use colorful::Color;
use colorful::Colorful;
use config::ProxyConfig;
use event::TaskManager;
use fault::FaultInjector;
#[cfg(feature = "discovery")]
use inject::k8s::Platform;
use inquire::Confirm;
use inquire::Select;
use kanal::AsyncReceiver;
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
use scenario::event::ScenarioEventManager;
use scenario::event::ScenarioItemLifecycle;
use scenario::event::capture_request_events;
use scenario::executor::execute_item;
#[cfg(feature = "discovery")]
use scenario::types::ScenarioItemRunsOn;
#[cfg(feature = "openapi")]
use scenario::generator::openapi;
use scenario::types::ScenarioResult;
use scenario::types::ScenariosResults;
use sched::build_schedule_events;
use sched::run_fault_schedule;
use scopeguard::guard;
use serde_json::from_reader;
#[cfg(all(target_family = "unix", feature = "agent"))]
use swiftide::integrations::treesitter::SupportedLanguages;
use termui::demo_prelude;
use termui::full_progress;
use termui::lean_progress;
use termui::long_operation;
use termui::proxy_prelude;
use termui::quiet_handle_displayable_events;
use tokio::sync::Notify;
use tokio::sync::watch;
use tokio::task;
use tokio::time::sleep;
use tokio_rustls::rustls;
use tokio_stream::StreamExt;
use tracing::error;
use uuid::Uuid;

#[tokio::main]
async fn main() -> Result<()> {
    let _ = rustls::crypto::ring::default_provider().install_default();

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

    let (proxy_shutdown_tx, proxy_shutdown_rx) = kanal::bounded_async(5);
    let task_manager = TaskManager::new();
    let (config_tx, config_rx) = watch::channel((
        ProxyConfig::default(),
        Vec::<Box<dyn FaultInjector>>::new(),
    ));

    let _fault_schedule_handle;
    let _progress_guard;
    let _scenario_event_capture_guard;

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
        kanal::bounded_async(1);

    let _http_proxy_guard;

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

            let http_proxy_nic_config = get_http_proxy_address(&options.common);

            // it's time to start our HTTP proxies
            if options.common.disable_http_proxies == false {
                _http_proxy_guard = initialize_http_proxy(
                    &http_proxy_nic_config,
                    proxy_state.clone(),
                    proxy_shutdown_rx.clone(),
                    task_manager.clone(),
                )
                .await;
            }

            // we now also start any other proxy that the user has requested us
            // to setup
            let mut proxied_protos = Vec::new();
            if !options.common.proxy_map.is_empty() {
                proxied_protos =
                    parse_proxy_protocols(options.common.proxy_map.clone())
                        .await?;
                let _tcp_proxy_guard = initialize_tcp_proxies(
                    proxied_protos.clone(),
                    proxy_state.clone(),
                    proxy_shutdown_rx.clone(),
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
                                    ebpf_proxy_shutdown_rx.clone(),
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
                    options.common.disable_http_proxies,
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
                _progress_guard = task::spawn(quiet_handle_displayable_events(
                    task_manager.new_subscriber(),
                ));
            } else if options.ui.tail {
                _progress_guard = task::spawn(full_progress(
                    proxy_shutdown_rx.clone(),
                    task_manager.new_subscriber(),
                ));
            } else {
                _progress_guard = task::spawn(lean_progress(
                    task_manager.new_subscriber(),
                    proxy_shutdown_rx.clone(),
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
        Commands::Scenario { scenario, .. } => match scenario {
            ScenarioCommands::Run(config) => {
                _scenario_event_capture_guard = run_scenario_command(
                    proxy_shutdown_rx,
                    task_manager.clone(),
                    config.scenario.clone(),
                    config.report.clone(),
                    config.result.clone(),
                )
                .await?;
            }
            #[cfg(feature = "openapi")]
            ScenarioCommands::Generate(config) => {
                if let Some(spec_file) = &config.spec_file {
                    match openapi::build_from_file(spec_file, None) {
                        Ok(scenarios) => {
                            let split_files = false;
                            let count = openapi::save(
                                &scenarios,
                                &config.scenario,
                                split_files,
                            )?;
                            println!(
                                "Generated {} reliability scenarios across {} endpoints!",
                                format!("{}", scenarios.len())
                                    .color(Color::Turquoise2),
                                format!("{}", count).color(Color::IndianRed1b)
                            );
                        }
                        Err(e) => {
                            tracing::error!("Failed to generate scenario {}", e)
                        }
                    }
                } else if let Some(spec_url) = &config.spec_url {
                    match openapi::build_from_url(spec_url, None).await {
                        Ok(scenarios) => {
                            let mut split_files = false;
                            if Path::new(&config.scenario).is_dir() {
                                split_files = true;
                            }
                            let count = openapi::save(
                                &scenarios,
                                &config.scenario,
                                split_files,
                            )?;
                            println!(
                                "Generated {} reliability scenarios across {} endpoints!",
                                format!("{}", scenarios.len())
                                    .color(Color::Turquoise2),
                                format!("{}", count).color(Color::IndianRed1b)
                            );
                        }
                        Err(e) => {
                            tracing::error!("Failed to generate scenario {}", e)
                        }
                    }
                }
            }
        },
        #[cfg(feature = "agent")]
        Commands::Agent { agent, common } => match agent {
            cli::AgentCommands::CodeReview(cfg) => {
                let file = File::open(&cfg.results)?;
                let reader = BufReader::new(file);
                let final_results: ScenariosResults = from_reader(reader)?;
                let final_report = report::builder::to_report(&final_results);
                let metas = agent::meta::get_metas(&final_report);

                let report_path = cfg.report.clone();
                let repo = cfg.repo.clone();
                let lang = cfg.lang.clone();
                let index = cfg.index.clone();
                let advices = cfg.advices.clone();
                let llm_client = common.llm_client.clone();
                let llm_prompt_model =
                    common.llm_prompt_reasoning_model.clone();
                let llm_prompt_reasoning_model =
                    common.llm_prompt_reasoning_model.clone();
                let llm_embed_model = common.llm_embed_model.clone();

                let (sender, receiver) = kanal::unbounded_async();

                let pb = long_operation(
                    "Reviewing! This could take a while...",
                    None,
                );

                let _event_handle: task::JoinHandle<Result<()>> =
                    tokio::spawn(async move {
                        let mut stream: kanal::ReceiveStream<
                            '_,
                            agent::suggestion::CodeReviewEvent,
                        > = receiver.stream();
                        let pb = pb.clone();
                        while let Some(event) = stream.next().await {
                            pb.inc(1);
                            if event.phase == CodeReviewEventPhase::Completed {
                                pb.finish_and_clear();

                                event.save_analysis(&report_path)?;

                                break;
                            }
                            pb.set_message(format!(
                                "{}...",
                                event.phase.long_form().bold()
                            ));
                        }

                        Ok(())
                    });

                let handle: task::JoinHandle<Result<()>> =
                    tokio::spawn(async move {
                        agent::source::index(
                            &repo,
                            &lang,
                            &metas,
                            &index,
                            llm_client,
                            &llm_prompt_model,
                            &llm_embed_model,
                        )
                        .await?;

                        agent::suggestion::review_source(
                            &metas,
                            &lang,
                            &repo,
                            advices,
                            llm_client,
                            &llm_prompt_model,
                            &llm_prompt_reasoning_model,
                            &llm_embed_model,
                            sender,
                        )
                        .await?;

                        Ok(())
                    });

                handle.await??;
            }
            cli::AgentCommands::ScenarioReview(cfg) => {
                let file = File::open(&cfg.results)?;
                let reader = BufReader::new(file);
                let final_results: ScenariosResults = from_reader(reader)?;
                let final_report = report::builder::to_report(&final_results);

                let role = cfg.role.clone();
                let llm_client = common.llm_client.clone();
                let llm_prompt_model =
                    common.llm_prompt_reasoning_model.clone();
                let llm_embed_model = common.llm_embed_model.clone();

                let (sender, receiver) = kanal::bounded_async(7);

                let handle: task::JoinHandle<
                    Result<agent::insight::ReportReviews>,
                > = tokio::spawn(async move {
                    Ok(agent::insight::analyze(
                        &final_report,
                        &role,
                        sender,
                        llm_client,
                        &llm_prompt_model,
                        &llm_embed_model,
                    )
                    .await?)
                });

                let pb = long_operation(
                    "Analyzing! This could take a while...",
                    Some(7),
                );

                tokio::spawn(async move {
                    let mut stream = receiver.stream();
                    let pb = pb.clone();
                    while let Some(event) = stream.next().await {
                        pb.inc(1);
                        if event.phase == ReviewEventPhase::Completed {
                            pb.finish_and_clear();
                            break;
                        }
                        pb.set_message(format!(
                            "{}...",
                            event.phase.long_form().bold()
                        ));
                    }
                });

                let report = handle.await??;
                report.save(&cfg.report)?;
            }
        },
        Commands::Inject { inject } => match inject {
            cli::FaultInjectionCommands::Kubernetes(cfg) => {

                let fault_settings = cfg.options.to_environment_variables();
                let plt = &mut inject::k8s::KubernetesPlatform::new(
                    &cfg.ns,
                    fault_settings,
                )
                .await?;

                run_fault_injector_roundtrip(
                    plt,
                    cfg.service.clone()
                ).await?;
            }
        },
    };

    match proxy_shutdown_tx.send(()).await {
        Ok(_) => tracing::debug!("Shutdown notified."),
        Err(e) => tracing::warn!("Failed to notify shutdown {}", e),
    };

    #[cfg(all(
        target_os = "linux",
        any(feature = "stealth", feature = "stealth-auto-build")
    ))]
    {
        match ebpf_proxy_shutdown_tx.send(()).await {
            Ok(_) => tracing::debug!("Shutdown of ebpf notified."),
            Err(e) => tracing::warn!("Failed to notify ebpf shutdown {}", e),
        };
    }

    drop(task_manager);

    shutdown_tracer(tracer_provider, meter_provider);

    Ok(())
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

#[cfg(feature = "discovery")]
pub async fn run_fault_injector_roundtrip<P: Platform>(
    plt: &mut P,
    service: Option<String>,
) -> Result<()> {
    let svcs = plt.discover().await?;
    let names: Vec<_> = svcs.iter().map(|s| s.name.clone()).collect();
    let sel = match service {
        Some(s) => s,
        None => Select::new("Service:", names).prompt()?,
    };
    let svc = match svcs.into_iter().find(|s| s.name == sel) {
        Some(m) => m,
        None => {
            return Err(anyhow!(format!("service {} could not be found", sel)));
        }
    };

    let handle = plt.inject(&svc).await?;
    println!("    Injected into service {} 🚀. You can now explore how your system reacts to its new conditions.", svc.name);

    let _ = Confirm::new("    Press 'y' to finish and rollback").prompt();

    plt.rollback(&svc, handle).await?;
    println!("   Rolled back 🛑");

    Ok(())
}

#[derive(Debug, Clone)]
pub enum FaultInjectionScenarioEvent {
    New {
        fault_settings: BTreeMap<String, String>
    },
    Done {}
}

#[cfg(feature = "discovery")]
pub async fn runs_item_on_platform(
    platform: ScenarioItemRunsOn,
    fault_settings: BTreeMap<String, String>, 
    ready_on: Arc<Notify>,
    wait_on: Arc<Notify>,
    rolledback_on: Arc<Notify>,
) -> Result<()> {
    match platform {
        ScenarioItemRunsOn::Kubernetes { ns, service } => {
            runs_item_on_kubernetes(ns, service, fault_settings, ready_on, wait_on, rolledback_on).await
        }
    }
}


#[cfg(feature = "discovery")]
pub async fn runs_item_on_kubernetes(
    ns: String,
    service: String,
    fault_settings: BTreeMap<String, String>,
    ready_on: Arc<Notify>,
    wait_on: Arc<Notify>,
    rolledback_on: Arc<Notify>,
) -> Result<()> {
    let plt = &mut inject::k8s::KubernetesPlatform::new(
        &ns,
        fault_settings,
    )
    .await?;

    let svcs = plt.discover().await?;
    let svc = match svcs.into_iter().find(|s| s.name == service) {
        Some(m) => m,
        None => {
            return Err(anyhow!(format!("service {} could not be found", service)));
        }
    };

    let handle = plt.inject(&svc).await?;
    plt.wait_ready(&svc).await?;

    ready_on.notify_one();

    tracing::debug!("waiting to complete");
    wait_on.notified().await;
    tracing::debug!("completed, rollback now");

    plt.rollback(&svc, handle).await?;

    plt.wait_cleanup(&svc).await?;

    rolledback_on.notify_one();

    Ok(())
}


async fn run_scenario_command(
    proxy_shutdown_rx: kanal::AsyncReceiver<()>,
    task_manager: Arc<TaskManager>,
    scenario: String,
    report: String,
    result: String
) -> Result<task::JoinHandle<()>> {
    let start_instant = Instant::now();
    let start = Utc::now();

    let addr_id_map: Arc<scc::HashMap<String, Uuid>> =
        Arc::new(scc::HashMap::default());
    let id_events_map: Arc<scc::HashMap<Uuid, ScenarioItemLifecycle>> =
        Arc::new(scc::HashMap::default());

    let scenario_event_capture_guard= tokio::spawn(capture_request_events(
        proxy_shutdown_rx,
        task_manager.new_subscriber(),
        addr_id_map.clone(),
        id_events_map.clone(),
    ));

    println!(
        "\n{}\n",
        "================ Running Scenarios ================".dim()
    );

    let mut scenarios = scenario::load_scenarios(Path::new(&scenario));

    let mut results = Vec::new();

    while let Some(candidate) = scenarios.next().await {
        match candidate {
            Ok(scenario) => {
                let (event_manager, scenario_event_receiver) =
                    ScenarioEventManager::new(500);

                tokio::spawn(termui::scenario_ui(scenario_event_receiver));

                let event = Arc::new(event_manager.new_event().await.unwrap());
                let _ = event.on_started(scenario.clone());

                let mut item_results = Vec::new();

                let cloned_scenario = scenario.clone();

                for mut i in scenario.items.into_iter() {
                    let wait_on: Arc<Notify> = Arc::new(Notify::new());
                    let mut rolledback_on = None;
                    let mut original_faults = None;

                    #[cfg(feature = "discovery")]
                    {
                        if let Some(ref platform) = i.context.runs_on {
                            let ready_on: Arc<Notify> = Arc::new(Notify::new());
                            let rb_on = Arc::new(Notify::new());

                            original_faults = Some(i.context.faults.clone());
                            let fault_settings = i.context.faults_to_environment_variables();
                            i.context.faults.clear();

                            tokio::spawn(runs_item_on_platform(
                                platform.clone(), fault_settings, ready_on.clone(), wait_on.clone(), rb_on.clone()));
                            
                            rolledback_on = Some(rb_on);
                            ready_on.notified().await;
                        }
                    }

                    let result = execute_item(
                        i.clone(),
                        event.clone(),
                        scenario.config.clone(),
                        addr_id_map.clone(),
                        id_events_map.clone(),
                        task_manager.clone(),
                    )
                    .await?;
                    item_results.push(result);

                    #[cfg(feature = "discovery")]
                    {
                        tracing::debug!("notify completion");
                        wait_on.notify_one();

                        // restore the faults for next round
                        if let Some(faults) = original_faults {
                            i.context.faults.extend(faults);
                        }

                        if let Some(rb_on) = rolledback_on {
                            tracing::debug!("waiting for rollback");
                            rb_on.notified().await;
                            tracing::debug!("done rollback");
                        }
                    }
                }

                results.push(ScenarioResult {
                    scenario: cloned_scenario,
                    results: item_results,
                });

                let _ = event.on_terminated();
            }
            Err(e) => error!("Failed to load scenario: {:?}", e),
        }
    }

    let final_results = ScenariosResults { start, end: Utc::now(), results };

    let final_report = report::builder::to_report(&final_results);

    println!("\n");
    println!(
        "{}\n",
        "===================== Summary =====================".dim()
    );

    println!(
        "Tests run: {}, Tests failed: {}",
        final_report
            .scenario_summaries
            .iter()
            .map(|s| s.item_count)
            .sum::<usize>()
            .to_string()
            .cyan(),
        final_report
            .scenario_summaries
            .iter()
            .map(|s| s
                .item_summaries
                .iter()
                .map(|i| i.failure_count)
                .sum::<usize>())
            .sum::<usize>()
            .to_string()
            .light_red(),
    );
    println!("Total time: {:.1}s", start_instant.elapsed().as_secs_f64());
    println!("");

    final_results.save(&result)?;
    final_report.save(&report)?;

    Ok(scenario_event_capture_guard)
}
