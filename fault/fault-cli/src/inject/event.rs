use std::sync::Arc;

use serde::Deserialize;
use serde::Serialize;

use crate::event::FaultEvent;
use crate::event::TaskId;
use crate::event::TaskProgressEvent;
use crate::scenario::types::ItemEvent;
use crate::scenario::types::ItemMetricsFaults;
use crate::service;
use crate::types::DnsTiming;

pub async fn forward_progress_to_remote(
    api_address: String,
    shutdown_rx: kanal::AsyncReceiver<()>,
    receiver: kanal::AsyncReceiver<TaskProgressEvent>,
) {
    let addr = format!("http://{}", api_address);

    tracing::debug!("Ready to forward proxy events to remote API {}", addr);

    let id_events_map: Arc<scc::HashMap<TaskId, EventLifecycle>> =
        Arc::new(scc::HashMap::default());

    loop {
        tokio::select! {
            _ = shutdown_rx.recv() => {
                tracing::info!("Shutdown signal received. Stopping forwarding proress to remote API service.");
                break;
            },

            event = receiver.recv() => {
                match event {
                    Ok(event) => {
                        match event {
                            TaskProgressEvent::Started { id, url, .. } => {
                                let lifecycle = EventLifecycle::new(url);
                                let _ = id_events_map.insert_async(id, lifecycle).await;
                            }
                            TaskProgressEvent::WithFault { id, ts: _, fault } => {
                                id_events_map.update_async(&id, |_, v| {
                                    v.fault_declared = Some(fault.clone());
                                    v.clone()
                                }).await;
                            }
                            TaskProgressEvent::IpResolved { id, ts: _, domain, time_taken } => {
                                id_events_map.update_async(&id, |_, v| {
                                    v.dns_timing.push(DnsTiming { host: domain, duration: time_taken, resolved: true });
                                    v.clone()
                                }).await;
                            },
                            TaskProgressEvent::FaultApplied { id, ts: _, fault } => {
                                id_events_map.update_async(&id, |_, v| {
                                    v.faults.applied.push((v.url.clone(), fault.clone()));
                                    v.clone()
                                }).await;
                            },
                            TaskProgressEvent::Ttfb { id, ts } => {
                                id_events_map.update_async(&id, |_, v| {
                                    v.ttfb = ts.elapsed().as_millis_f64();
                                    v.clone()
                                }).await;
                            },
                            TaskProgressEvent::ResponseReceived { .. } => {},
                            TaskProgressEvent::Completed { id, .. } => {
                                if let Some((_, event)) = id_events_map.remove_async(&id).await {
                                    tracing::warn!("Sending results {}", id);
                                   let _ = service::forward_event(&addr, &event).await;
                                };
                            },
                            TaskProgressEvent::Error { .. } => {},
                            TaskProgressEvent::Passthrough { .. } => {},
                        }
                    }
                    Err(_) => {
                        break;
                    }
                }
            }
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct EventLifecycle {
    pub url: String,
    pub dns_timing: Vec<DnsTiming>,
    pub ttfb: f64,
    pub fault_declared: Option<FaultEvent>,
    pub faults: EventLifecycleFaults,
}

impl EventLifecycle {
    pub fn new(url: String) -> Self {
        Self {
            url: url.clone(),
            dns_timing: Vec::new(),
            ttfb: 0.0,
            fault_declared: None,
            faults: EventLifecycleFaults::new(url),
        }
    }
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct EventLifecycleFaults {
    pub url: String,
    pub applied: Vec<(String, FaultEvent)>,
}

impl EventLifecycleFaults {
    pub fn new(url: String) -> Self {
        Self { url, applied: Vec::new() }
    }
}

impl EventLifecycleFaults {
    pub fn as_metrics_faults(&self) -> ItemMetricsFaults {
        let applied = if self.applied.is_empty() {
            None
        } else {
            Some(
                self.applied
                    .iter()
                    .map(|(_url, event)| ItemEvent { event: event.clone() })
                    .collect::<Vec<ItemEvent>>(),
            )
        };

        ItemMetricsFaults { url: self.url.clone(), applied }
    }
}
