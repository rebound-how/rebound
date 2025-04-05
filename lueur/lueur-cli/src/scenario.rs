use std::collections::HashMap;
use std::fmt;
use std::path::Path;
use std::pin::Pin;
use std::sync::Arc;
use std::sync::Mutex;
use std::sync::atomic::AtomicUsize;
use std::sync::atomic::Ordering;
use std::task::Context;
use std::task::Poll;
use std::time::Duration;
use std::time::Instant;

use arc_swap::ArcSwap;
use async_stream::stream;
use bytes::Bytes;
use bytes::BytesMut;
use futures::StreamExt;
use pin_project::pin_project;
use reqwest::Client;
use reqwest::RequestBuilder;
use serde::Deserialize;
use serde::Serialize;
use serde_yaml::Deserializer;
use tokio::fs::File;
use tokio::io::AsyncReadExt;
use tokio::sync::broadcast;
use tokio::sync::broadcast::Receiver;
use tokio::sync::broadcast::Sender;
use tokio::sync::broadcast::error::SendError;
use tokio::sync::watch;
use tokio_stream::Stream;
use url::Url;
use walkdir::WalkDir;

use crate::config::FaultConfig;
use crate::config::ProxyConfig;
use crate::errors::ProxyError;
use crate::errors::ScenarioError;
use crate::event::FaultEvent;
use crate::event::TaskId;
use crate::event::TaskProgressEvent;
use crate::event::TaskProgressReceiver;
use crate::fault::FaultInjector;
use crate::plugin::load_injectors;
use crate::proxy::ProxyState;
use crate::reporting::DnsTiming;
use crate::reporting::ReportItemEvent;
use crate::reporting::ReportItemExpectation;
use crate::reporting::ReportItemExpectationDecision;
use crate::reporting::ReportItemHttpExpectation;
use crate::reporting::ReportItemHttpResult;
use crate::reporting::ReportItemMetrics;
use crate::reporting::ReportItemMetricsFaults;
use crate::reporting::ReportItemProtocol;
use crate::reporting::ReportItemResult;
use crate::reporting::ReportItemTarget;
use crate::types::FaultConfiguration;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioItemExpectation {
    pub status: Option<u16>,
    pub response_time_under: Option<f64>, // ms
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioItemCall {
    pub method: String, // HTTP method (e.g., GET, POST)
    pub url: String,    // Target URL
    pub headers: Option<HashMap<String, String>>, // Optional headers
    pub body: Option<String>, // Optional request body
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioItemContext {
    pub upstreams: Vec<String>,
    pub faults: Vec<FaultConfiguration>,
    pub strategy: Option<ScenarioItemCallStrategy>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioItemCallStrategy {
    pub mode: ScenarioItemCallStrategyMode,
    pub failfast: Option<bool>,
    pub step: f64,
    pub count: usize,
    pub wait: Option<f64>,
    pub add_baseline_call: Option<bool>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ScenarioItemCallStrategyMode {
    Repeat,
}

impl Default for ScenarioItemCallStrategyMode {
    fn default() -> Self {
        Self::Repeat
    }
}

impl fmt::Display for ScenarioItemCallStrategyMode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ScenarioItemCallStrategyMode::Repeat => write!(f, "repeat"),
        }
    }
}

/// A single entry in the scenario
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioItem {
    pub call: ScenarioItemCall,
    pub context: ScenarioItemContext,
    pub expect: Option<ScenarioItemExpectation>,
}

/// The overall scenario containing multiple entries
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Scenario {
    pub title: String,
    pub description: Option<String>,
    pub scenarios: Vec<ScenarioItem>,
}

pub async fn execute_item(
    proxy_address: String,
    config_tx: watch::Sender<(ProxyConfig, Vec<Box<dyn FaultInjector>>)>,
    item: ScenarioItem,
    proxy_state: Arc<ProxyState>,
    event_manager: Arc<ScenarioEventManager>,
) -> ReportItemResult {
    let upstream_hosts = item.context.upstreams.clone();
    let upstreams: Vec<String> =
        upstream_hosts.iter().map(|h| upstream_to_addr(h).unwrap()).collect();
    proxy_state.set_upstream_hosts(upstreams).await;

    let faults = item.context.faults.clone();
    let fault_config: Vec<FaultConfig> =
        faults.iter().map(|f| f.build().unwrap()).collect();
    let new_config =
        ProxyConfig { faults: Arc::new(ArcSwap::from_pointee(fault_config)) };

    let injectors: Vec<Box<dyn FaultInjector>> = load_injectors(&new_config);

    if config_tx.send((new_config, injectors)).is_err() {
        tracing::error!("Proxy task has been shut down.");
    }

    let mut report = ReportItemResult {
        target: ReportItemTarget { address: item.call.url.clone() },
        expect: None,
        faults: item.context.faults.clone(),
        metrics: None,
        errors: Vec::new(),
        total_time: 0.0,
    };

    match execute_request(
        item.call.clone(),
        item.expect.clone(),
        proxy_address.clone(),
        event_manager,
    )
    .await
    {
        Ok(metrics) => {
            report.metrics = Some(metrics.clone());
            match item.expect.clone() {
                Some(r) => {
                    let mut met = None;

                    let mut result = ReportItemHttpResult {
                        status_code: None,
                        response_time: None,
                        decision: ReportItemExpectationDecision::Unknown,
                    };

                    match metrics.protocol {
                        Some(ReportItemProtocol::Http {
                            code,
                            body_length: _,
                        }) => {
                            met = match r.status {
                                Some(v) => {
                                    result.status_code = Some(code);
                                    Some(v == code)
                                }
                                None => met,
                            };
                        }
                        None => {}
                    };

                    if met.is_none() || met == Some(true) {
                        met = match r.response_time_under {
                            Some(v) => {
                                result.response_time = Some(metrics.total_time);
                                Some(metrics.total_time <= v)
                            }
                            None => met,
                        };
                    }

                    if met == Some(true) {
                        result.decision =
                            ReportItemExpectationDecision::Success;
                    } else {
                        result.decision =
                            ReportItemExpectationDecision::Failure;
                    }

                    report.expect = Some(ReportItemExpectation::Http {
                        wanted: ReportItemHttpExpectation {
                            status_code: r.status,
                            response_time_under: r.response_time_under,
                        },
                        got: Some(result),
                    });

                    met
                }
                None => None,
            };
        }
        Err(e) => report.errors.push(e.to_string()),
    }

    report
}

pub fn count_scenario_items(scenario: &Scenario) -> u64 {
    let mut count = 0;

    for item in scenario.scenarios.iter() {
        let strategy = item.context.strategy.clone();
        if let Some(strategy) = strategy {
            count += strategy.count;
            if strategy.add_baseline_call.is_some_and(|x| x) {
                count += 1;
            }
        } else {
            count += 1;
        }
    }

    count as u64
}

pub fn build_item_list(source: ScenarioItem) -> Vec<ScenarioItem> {
    let mut items = Vec::new();

    let strategy = source.context.strategy.clone();

    items.push(source.clone());

    if let Some(strategy) = strategy {
        if strategy.add_baseline_call.is_some_and(|x| x) {
            tracing::debug!("Add first call as a baseline without any faults");
            let mut next_item = source.clone();
            next_item.context.faults = Vec::new();
            items.insert(0, next_item);
        }

        for i in 1..strategy.count {
            let mut next_item = source.clone();
            next_item.context.faults = match strategy.mode {
                ScenarioItemCallStrategyMode::Repeat => {
                    let mut next_faults = Vec::new();

                    for fault in next_item.context.faults {
                        next_faults.push(match fault {
                            FaultConfiguration::Latency {
                                distribution,
                                global,
                                side,
                                mean,
                                stddev,
                                min,
                                max,
                                shape,
                                scale,
                                direction,
                                period,
                            } => FaultConfiguration::Latency {
                                distribution,
                                global,
                                side,
                                mean: Some(
                                    mean.unwrap() + (strategy.step * i as f64),
                                ),
                                stddev,
                                min,
                                max,
                                shape,
                                scale,
                                direction,
                                period,
                            },
                            FaultConfiguration::PacketLoss {
                                direction,
                                side,
                                period,
                            } => FaultConfiguration::PacketLoss {
                                direction,
                                side,
                                period,
                            },
                            FaultConfiguration::Bandwidth {
                                rate,
                                unit,
                                direction,
                                side,
                                period,
                            } => FaultConfiguration::Bandwidth {
                                rate,
                                unit,
                                direction,
                                side,
                                period,
                            },
                            FaultConfiguration::Jitter {
                                amplitude: jitter_amplitude,
                                frequency: jitter_frequency,
                                direction,
                                period,
                            } => FaultConfiguration::Jitter {
                                amplitude: jitter_amplitude,
                                frequency: jitter_frequency,
                                direction,
                                period,
                            },
                            FaultConfiguration::Dns {
                                period,
                                rate: dns_rate,
                            } => FaultConfiguration::Dns {
                                rate: dns_rate,
                                period,
                            },
                            FaultConfiguration::HttpError {
                                status_code,
                                body,
                                probability,
                                period,
                            } => FaultConfiguration::HttpError {
                                status_code,
                                body,
                                probability,
                                period,
                            },
                        })
                    }
                    next_faults
                }
            };
            items.push(next_item)
        }
    }

    items
}

pub async fn execute_request(
    call: ScenarioItemCall,
    _expect: Option<ScenarioItemExpectation>,
    proxy_address: String,
    event_manager: Arc<ScenarioEventManager>,
) -> Result<ReportItemMetrics, ProxyError> {
    let url = &call.url;
    let event = event_manager.new_event().await.unwrap();
    let _ = event.on_started(url.clone());

    let client = Arc::new(
        reqwest::Client::builder()
            .proxy(reqwest::Proxy::http(&proxy_address).unwrap())
            .build()
            .unwrap(),
    );

    let reqwest_request =
        build_request(&client, &call)?.build().map_err(|e| {
            ProxyError::InvalidConfiguration(format!(
                "Failed to build request: {}",
                e
            ))
        })?;

    let conn_start = Instant::now();
    let ttfb_start = Instant::now();
    let mut buffer = BytesMut::new();

    let response = client
        .execute(reqwest_request)
        .await
        .map_err(ProxyError::NetworkError)?;

    let status = response.status();
    let stream = response.bytes_stream();
    let timing_stream = TimingStream::new(stream, ttfb_start);

    futures::pin_mut!(timing_stream);
    while let Some(chunk) = timing_stream.next().await {
        match chunk {
            Ok(bytes) => {
                buffer.extend_from_slice(&bytes);
            }
            Err(e) => {
                tracing::error!("Error while receiving bytes: {}", e);
                break;
            }
        }
    }

    let conn_duration = conn_start.elapsed();

    let ttfb_time = ttfb_start.elapsed();

    let body_bytes = buffer.freeze();
    let body_length = body_bytes.len();
    let _ = match timing_stream.first_byte_time {
        Some(d) => d.duration_since(timing_stream.start),
        None => Duration::new(0, 0),
    };

    let mut metrics = ReportItemMetrics::new();
    metrics.protocol =
        Some(ReportItemProtocol::Http { code: status.as_u16(), body_length });
    metrics.ttfb = ttfb_time.as_millis_f64();
    metrics.total_time = conn_duration.as_millis_f64();

    let _ = event.on_terminated();

    Ok(metrics)
}

fn build_request(
    client: &Arc<Client>,
    call: &ScenarioItemCall,
) -> Result<RequestBuilder, ProxyError> {
    let mut req_builder = client.request(
        reqwest::Method::from_bytes(call.method.as_bytes()).map_err(|_| {
            ProxyError::InvalidConfiguration("Invalid HTTP method.".to_string())
        })?,
        &call.url,
    );

    if let Some(headers) = &call.headers {
        for (key, value) in headers.iter() {
            req_builder = req_builder.header(key, value);
        }
    }

    if let Some(body) = &call.body {
        req_builder = req_builder.body(body.clone());
    }

    Ok(req_builder)
}

pub fn load_scenarios(
    dir_path: &Path,
) -> Pin<Box<dyn Stream<Item = Result<Scenario, ScenarioError>> + Send>> {
    let dir_path = dir_path.to_owned();

    let scenario_stream = stream! {
        tracing::info!("Loading scenario files from directory {:?}", dir_path);

        let paths = match tokio::task::spawn_blocking(move || {
            WalkDir::new(&dir_path)
                .into_iter()
                .filter_map(|entry| match entry {
                    Ok(e) => {
                        let path = e.path();
                        if e.file_type().is_file()
                            && path.extension().is_some_and(|ext| {
                                ext.eq_ignore_ascii_case("yaml") || ext.eq_ignore_ascii_case("yml")
                            })
                        {
                            Some(path.to_owned())
                        } else {
                            None
                        }
                    },
                    Err(_) => {
                        None
                    }
                })
                .collect::<Vec<_>>()
        }).await {
            Ok(paths) => paths,
            Err(e) => {
                yield Err(ScenarioError::WalkDirError(e.to_string()));
                return;
            }
        };

        for path in paths {
            let path_clone = path.clone();
            tracing::info!("Loading scenarios from {:?}", path_clone);

            match File::open(&path_clone).await {
                Ok(mut file) => {
                    let mut contents = String::new();

                    match file.read_to_string(&mut contents).await {
                        Ok(_) => {
                            let scenarios_result = tokio::task::spawn_blocking(move || {
                                let mut docs = Vec::new();
                                for document in Deserializer::from_str(&contents) {
                                    let doc = Scenario::deserialize(document);
                                    docs.push(doc);
                                }
                                docs
                            }).await;

                            match scenarios_result {
                                Ok(scenarios) => {
                                    for scenario in scenarios {
                                        match scenario {
                                            Ok(s) => yield Ok(s),
                                            Err(e) => yield Err(ScenarioError::ParseError(
                                                path_clone.to_string_lossy().to_string(),
                                                e
                                            )),
                                        }
                                    }
                                },
                                Err(e) => {
                                    yield Err(ScenarioError::ReadError(
                                        path_clone.to_string_lossy().to_string(),
                                        std::io::Error::other(e.to_string()),
                                    ));
                                }
                            }
                        },
                        Err(e) => {
                            yield Err(ScenarioError::ReadError(
                                path_clone.to_string_lossy().to_string(),
                                e
                            ));
                        }
                    }
                },
                Err(e) => {
                    yield Err(ScenarioError::ReadError(
                        path_clone.to_string_lossy().to_string(),
                        e
                    ));
                }
            }
        }
    };

    Box::pin(scenario_stream)
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

pub type ScenarioEventId = usize;
pub type ScenarioEventSender = Sender<ScenarioItemEvent>;
pub type ScenarioEventReceiver = Receiver<ScenarioItemEvent>;

#[derive(Debug, Clone)]
pub enum ScenarioItemEvent {
    Started { id: ScenarioEventId, url: String },
    Terminated { id: ScenarioEventId },
}

pub struct ScenarioEventManager {
    counter: AtomicUsize,
    pub sender: ScenarioEventSender,
}

impl ScenarioEventManager {
    pub fn new(capacity: usize) -> (Arc<Self>, ScenarioEventReceiver) {
        let (sender, receiver) = broadcast::channel(capacity);
        (
            Arc::new(ScenarioEventManager {
                counter: AtomicUsize::new(1),
                sender,
            }),
            receiver,
        )
    }

    pub fn get_sender(&self) -> ScenarioEventSender {
        self.sender.clone()
    }

    pub fn next_id(&self) -> ScenarioEventId {
        self.counter.fetch_add(1, Ordering::SeqCst)
    }

    pub async fn new_event(
        &self,
    ) -> Result<ScenarioEvent, SendError<ScenarioItemEvent>> {
        let event_id = self.next_id();
        Ok(ScenarioEvent { id: event_id, sender: self.get_sender() })
    }
}

#[derive(Clone, Debug)]
pub struct ScenarioEvent {
    id: ScenarioEventId,
    sender: ScenarioEventSender,
}

impl ScenarioEvent {
    fn on_started(
        &self,
        url: String,
    ) -> Result<(), SendError<ScenarioItemEvent>> {
        let event: ScenarioItemEvent =
            ScenarioItemEvent::Started { id: self.id, url };
        let sender = self.sender.clone();
        let _ = sender.send(event);
        Ok(())
    }

    fn on_terminated(&self) -> Result<(), SendError<ScenarioItemEvent>> {
        let event: ScenarioItemEvent =
            ScenarioItemEvent::Terminated { id: self.id };
        let sender = self.sender.clone();
        let _ = sender.send(event);
        Ok(())
    }
}

#[derive(Clone, Debug)]
pub struct ScenarioItemLifecycle {
    pub url: String,
    pub dns_timing: Vec<DnsTiming>,
    pub fault_declared: Option<FaultEvent>,
    pub faults: HashMap<TaskId, ScenarioItemLifecycleFaults>,
}

impl ScenarioItemLifecycle {
    pub fn new(url: String) -> Self {
        Self {
            url,
            dns_timing: Vec::new(),
            fault_declared: None,
            faults: HashMap::new(),
        }
    }
}

#[derive(Clone, Debug)]
pub struct ScenarioItemLifecycleFaults {
    pub url: String,
    pub applied: Vec<(String, FaultEvent)>,
}

impl ScenarioItemLifecycleFaults {
    pub fn new(url: String) -> Self {
        Self { url, applied: Vec::new() }
    }
}

pub async fn handle_scenario_events(
    mut scenario_event_receiver: ScenarioEventReceiver,
    mut proxy_event_receiver: TaskProgressReceiver,
    queue: Arc<Mutex<Vec<ScenarioItemLifecycle>>>,
) {
    let mut current: Option<ScenarioItemLifecycle> = None;

    loop {
        tokio::select! {
            scenario_event = scenario_event_receiver.recv() => {
                match scenario_event {
                    Ok(event) => {
                        match event {
                            ScenarioItemEvent::Started{ id: _, url } => {
                                current = Some(ScenarioItemLifecycle::new(url))
                            },
                            ScenarioItemEvent::Terminated { id: _ } => {
                                if let Some(ref lifecycle) = current {
                                    let mut queue_lock = queue.lock().unwrap();
                                    queue_lock.push(lifecycle.clone());
                                }
                            }
                        }
                    }
                    Err(broadcast::error::RecvError::Closed) => {
                        break;
                    }
                    Err(broadcast::error::RecvError::Lagged(count)) => {
                        tracing::warn!("Missed {} scenario messages", count);
                    }
                }
            }

            proxy_event = proxy_event_receiver.recv() => {
                match proxy_event {
                    Ok(event) => {
                        match event {
                            TaskProgressEvent::Started { id: _, ts: _, url } => {
                                if let Some(ref mut item) = current { item.url = url; }
                            }
                            TaskProgressEvent::WithFault { id, ts: _, fault } => {
                                if let Some(ref mut item) = current {
                                    item.fault_declared = Some(fault.clone());

                                    let f = ScenarioItemLifecycleFaults::new(item.url.clone());
                                    item.faults.insert(id, f);
                                }
                            }
                            TaskProgressEvent::IpResolved { id: _, ts: _, domain, time_taken } => {
                                if let Some(ref mut item) = current {
                                    item.dns_timing.push(DnsTiming { host: domain, duration: time_taken, resolved: true });
                                }
                            },
                            TaskProgressEvent::FaultApplied { id, ts: _, fault } => {
                                if let Some(ref mut item) = current {
                                    if let Some(f) = item.faults.get_mut(&id) {
                                        f.applied.push((item.url.clone(), fault.clone()));
                                    }
                                }
                            },
                            TaskProgressEvent::Ttfb { .. } => {},
                            TaskProgressEvent::ResponseReceived { .. } => {},
                            TaskProgressEvent::Completed { .. } => {},
                            TaskProgressEvent::Error { .. } => {},
                            TaskProgressEvent::Passthrough { .. } => {},
                        }
                    }
                    Err(broadcast::error::RecvError::Closed) => {
                        break;
                    }
                    Err(broadcast::error::RecvError::Lagged(count)) => {
                        eprintln!("Missed {} messages", count);
                    }
                }
            }
        }
    }
}

// Define a custom stream wrapper to measure TTFB
#[pin_project]
struct TimingStream<S> {
    #[pin]
    inner: S,
    start: Instant,
    first_byte_time: Option<Instant>,
}

impl<S> TimingStream<S> {
    fn new(inner: S, start: Instant) -> Self {
        Self { inner, start, first_byte_time: None }
    }
}

impl<S> Stream for TimingStream<S>
where
    S: Stream<Item = Result<Bytes, reqwest::Error>> + Unpin,
{
    type Item = Result<Bytes, reqwest::Error>;

    fn poll_next(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<Option<Self::Item>> {
        let this = self.project();
        match this.inner.poll_next(cx) {
            Poll::Ready(Some(Ok(bytes))) => {
                if this.first_byte_time.is_none() {
                    let now = Instant::now();
                    *this.first_byte_time = Some(now);
                }
                Poll::Ready(Some(Ok(bytes)))
            }
            other => other,
        }
    }
}

impl ScenarioItemLifecycleFaults {
    pub fn to_report_metrics_faults(&self) -> ReportItemMetricsFaults {
        // Map the `applied` field
        let applied = if self.applied.is_empty() {
            None
        } else {
            Some(
                self.applied
                    .iter()
                    .map(|(_url, event)| ReportItemEvent {
                        event: event.clone(),
                    })
                    .collect::<Vec<ReportItemEvent>>(),
            )
        };

        ReportItemMetricsFaults { url: self.url.clone(), applied }
    }
}
