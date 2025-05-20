use std::sync::Arc;
use std::sync::atomic::AtomicUsize;
use std::sync::atomic::Ordering;

use scc;
use tokio::sync::broadcast;
use tokio::sync::broadcast::Receiver;
use tokio::sync::broadcast::Sender;
use tokio::sync::broadcast::error::SendError;
use uuid::Uuid;

use super::types::ItemEvent;
use super::types::ItemExpectation;
use super::types::ItemMetricsFaults;
use super::types::Scenario;
use super::types::ScenarioItem;
use crate::event::FaultEvent;
use crate::event::TaskProgressEvent;
use crate::event::TaskProgressReceiver;
use crate::report::types::DnsTiming;

pub type ScenarioEventId = usize;
pub type ScenarioEventSender = Sender<ScenarioEventPhase>;
pub type ScenarioEventReceiver = Receiver<ScenarioEventPhase>;

#[derive(Debug, Clone)]
pub enum ScenarioEventPhase {
    Started {
        id: ScenarioEventId,
        scenario: Scenario,
    },
    Terminated {
        id: ScenarioEventId,
    },
    ItemStarted {
        id: ScenarioEventId,
        url: String,
        item: ScenarioItem,
    },
    ItemTerminated {
        id: ScenarioEventId,
        method: String,
        url: String,
        expectation: Option<ItemExpectation>,
    },
}

pub struct ScenarioEventManager {
    counter: AtomicUsize,
    pub sender: ScenarioEventSender,
}

#[derive(Clone, Debug)]
pub struct ScenarioEvent {
    pub id: ScenarioEventId,
    pub sender: ScenarioEventSender,
}

impl ScenarioEvent {
    pub fn on_started(
        &self,
        scenario: Scenario,
    ) -> Result<(), SendError<ScenarioEventPhase>> {
        let event = ScenarioEventPhase::Started { id: self.id, scenario };
        let sender = self.sender.clone();
        let _ = sender.send(event);
        Ok(())
    }

    pub fn on_terminated(&self) -> Result<(), SendError<ScenarioEventPhase>> {
        let event = ScenarioEventPhase::Terminated { id: self.id };
        let sender = self.sender.clone();
        let _ = sender.send(event);
        Ok(())
    }

    pub fn on_item_started(
        &self,
        url: String,
        item: ScenarioItem,
    ) -> Result<(), SendError<ScenarioEventPhase>> {
        let event = ScenarioEventPhase::ItemStarted { id: self.id, url, item };
        let sender = self.sender.clone();
        let _ = sender.send(event);
        Ok(())
    }

    pub fn on_item_terminated(
        &self,
        item: &ScenarioItem,
        expectation: Option<ItemExpectation>,
    ) -> Result<(), SendError<ScenarioEventPhase>> {
        let event = ScenarioEventPhase::ItemTerminated {
            id: self.id,
            method: item.call.method.clone(),
            url: item.call.url.clone(),
            expectation,
        };
        let sender = self.sender.clone();
        let _ = sender.send(event);
        Ok(())
    }
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

    pub fn new_subscriber(&self) -> ScenarioEventReceiver {
        self.sender.subscribe()
    }

    pub fn next_id(&self) -> ScenarioEventId {
        self.counter.fetch_add(1, Ordering::SeqCst)
    }

    pub async fn new_event(
        &self,
    ) -> Result<ScenarioEvent, SendError<ScenarioEventPhase>> {
        let event_id = self.next_id();
        Ok(ScenarioEvent { id: event_id, sender: self.get_sender() })
    }
}

#[derive(Clone, Debug)]
pub struct ScenarioItemLifecycle {
    pub url: String,
    pub dns_timing: Vec<DnsTiming>,
    pub ttfb: f64,
    pub fault_declared: Option<FaultEvent>,
    pub faults: ScenarioItemLifecycleFaults,
}

impl ScenarioItemLifecycle {
    pub fn new(url: String) -> Self {
        Self {
            url: url.clone(),
            dns_timing: Vec::new(),
            ttfb: 0.0,
            fault_declared: None,
            faults: ScenarioItemLifecycleFaults::new(url),
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

impl ScenarioItemLifecycleFaults {
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

pub async fn capture_request_events(
    shutdown_rx: kanal::AsyncReceiver<()>,
    proxy_event_receiver: TaskProgressReceiver,
    addr_id_map: Arc<scc::HashMap<String, Uuid>>,
    id_events_map: Arc<scc::HashMap<Uuid, ScenarioItemLifecycle>>,
) {
    loop {
        tokio::select! {
            _ = shutdown_rx.recv() => {
                tracing::info!("Shutdown signal received. Stopping capturing scenario events.");
                break;
            },

            proxy_event = proxy_event_receiver.recv() => {
                match proxy_event {
                    Ok(event) => {
                        match event {
                            TaskProgressEvent::Started { id, ts: _, url, src_addr } => {
                                let lifecycle = ScenarioItemLifecycle::new(url);
                                let _ = addr_id_map.insert_async(src_addr, id).await;
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
                            TaskProgressEvent::Completed { .. } => {},
                            TaskProgressEvent::Error { .. } => {},
                            TaskProgressEvent::Passthrough { .. } => {},
                        }
                    }
                    Err(e) => {
                        tracing::warn!("Error in scenario events capture {:?}", e);
                    }
                }
            }
        }
    }
}
