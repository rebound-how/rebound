use std::error::Error;
use std::sync::Arc;
use std::time::Duration;
use std::time::Instant;

use serde::Deserialize;
use serde::Serialize;
use serde::de::Deserializer;
use serde::de::{self};
use serde::ser::Serializer;
use tokio::sync::broadcast::error::SendError;
use uuid::Uuid;

use crate::types::Direction;
use crate::types::LlmCase;
use crate::types::StreamSide;

#[derive(Debug, Clone)]
pub enum TaskProgressEvent {
    Started {
        id: TaskId,
        ts: Instant,
        url: String,
        src_addr: String,
    },
    WithFault {
        id: TaskId,
        ts: Instant,
        fault: FaultEvent,
    },
    IpResolved {
        id: TaskId,
        ts: Instant,
        domain: String,
        time_taken: f64,
    },
    FaultApplied {
        id: TaskId,
        ts: Instant,
        fault: FaultEvent,
    },
    Ttfb {
        id: TaskId,
        ts: Instant,
    },
    ResponseReceived {
        id: TaskId,
        ts: Instant,
        status_code: u16,
    },
    Completed {
        id: TaskId,
        ts: Instant,
        time_taken: Duration,
        from_downstream_length: u64,
        from_upstream_length: u64,
    },
    Error {
        id: TaskId,
        ts: Instant,
        error: String,
    },
    Passthrough {
        id: TaskId,
        ts: Instant,
        time_taken: Duration,
        from_downstream_length: u64,
        from_upstream_length: u64,
    },
}

pub type TaskId = Uuid;
pub type TaskProgressSender = kanal::AsyncSender<TaskProgressEvent>;
pub type TaskProgressReceiver = kanal::AsyncReceiver<TaskProgressEvent>;

pub trait ProxyTaskEvent: Send + Sync + std::fmt::Debug {
    fn on_started(
        &self,
        url: String,
        src_addr: String,
    ) -> Result<(), SendError<TaskProgressEvent>>;

    fn with_fault(
        &self,
        fault: FaultEvent,
    ) -> Result<(), SendError<TaskProgressEvent>>;

    fn on_resolved(
        &self,
        domain: String,
        time_taken: f64,
    ) -> Result<(), SendError<TaskProgressEvent>>;

    fn on_completed(
        &self,
        time_taken: Duration,
        from_downstream_length: u64,
        from_upstream_length: u64,
    ) -> Result<(), SendError<TaskProgressEvent>>;

    fn on_first_byte(&self) -> Result<(), SendError<TaskProgressEvent>>;

    fn on_applied(
        &self,
        fault: FaultEvent,
    ) -> Result<(), SendError<TaskProgressEvent>>;

    fn on_response(
        &self,
        status_code: u16,
    ) -> Result<(), SendError<TaskProgressEvent>>;

    fn on_error(
        &self,
        error: Box<dyn Error>,
    ) -> Result<(), SendError<TaskProgressEvent>>;

    fn clone_me(&self) -> Box<dyn ProxyTaskEvent>;

    fn get_id(&self) -> TaskId;
}

impl Clone for Box<dyn ProxyTaskEvent> {
    fn clone(&self) -> Box<dyn ProxyTaskEvent> {
        self.clone_me()
    }
}

#[derive(Clone, Debug)]
pub struct FaultTaskEvent {
    id: TaskId,
    sender: TaskProgressSender,
}

impl ProxyTaskEvent for FaultTaskEvent {
    fn on_started(
        &self,
        url: String,
        src_addr: String,
    ) -> Result<(), SendError<TaskProgressEvent>> {
        let event: TaskProgressEvent = TaskProgressEvent::Started {
            id: self.id,
            ts: Instant::now(),
            url,
            src_addr,
        };
        let sender = self.sender.clone();
        let _ = sender.as_sync().send(event);
        Ok(())
    }

    fn with_fault(
        &self,
        fault: FaultEvent,
    ) -> Result<(), SendError<TaskProgressEvent>> {
        let event: TaskProgressEvent = TaskProgressEvent::WithFault {
            id: self.id,
            ts: Instant::now(),
            fault,
        };
        let sender = self.sender.clone();
        let _ = sender.as_sync().send(event);
        Ok(())
    }

    fn on_resolved(
        &self,
        domain: String,
        time_taken: f64,
    ) -> Result<(), SendError<TaskProgressEvent>> {
        let event: TaskProgressEvent = TaskProgressEvent::IpResolved {
            id: self.id,
            ts: Instant::now(),
            domain,
            time_taken,
        };
        let sender = self.sender.clone();
        let _ = sender.as_sync().send(event);
        Ok(())
    }

    fn on_completed(
        &self,
        time_taken: Duration,
        from_downstream_length: u64,
        from_upstream_length: u64,
    ) -> Result<(), SendError<TaskProgressEvent>> {
        let event: TaskProgressEvent = TaskProgressEvent::Completed {
            id: self.id,
            ts: Instant::now(),
            time_taken,
            from_downstream_length,
            from_upstream_length,
        };
        let sender = self.sender.clone();
        let _ = sender.as_sync().send(event);
        Ok(())
    }

    fn on_first_byte(&self) -> Result<(), SendError<TaskProgressEvent>> {
        let event: TaskProgressEvent =
            TaskProgressEvent::Ttfb { id: self.id, ts: Instant::now() };
        let sender = self.sender.clone();
        let _ = sender.as_sync().send(event);
        Ok(())
    }

    fn on_applied(
        &self,
        fault: FaultEvent,
    ) -> Result<(), SendError<TaskProgressEvent>> {
        let event: TaskProgressEvent = TaskProgressEvent::FaultApplied {
            id: self.id,
            ts: Instant::now(),
            fault,
        };
        let sender = self.sender.clone();
        let _ = sender.as_sync().send(event);
        Ok(())
    }

    fn on_response(
        &self,
        status_code: u16,
    ) -> Result<(), SendError<TaskProgressEvent>> {
        let event: TaskProgressEvent = TaskProgressEvent::ResponseReceived {
            id: self.id,
            ts: Instant::now(),
            status_code,
        };
        let sender = self.sender.clone();
        let _ = sender.as_sync().send(event);
        Ok(())
    }

    fn clone_me(&self) -> Box<dyn ProxyTaskEvent> {
        Box::new(self.clone())
    }

    fn on_error(
        &self,
        error: Box<dyn Error>,
    ) -> Result<(), SendError<TaskProgressEvent>> {
        let event: TaskProgressEvent = TaskProgressEvent::Error {
            id: self.id,
            ts: Instant::now(),
            error: error.to_string(),
        };
        let sender = self.sender.clone();
        let _ = sender.as_sync().send(event);
        Ok(())
    }

    fn get_id(&self) -> TaskId {
        self.id
    }
}

#[derive(Clone, Debug)]
pub struct PassthroughTaskEvent {
    id: TaskId,
    sender: TaskProgressSender,
}

impl ProxyTaskEvent for PassthroughTaskEvent {
    fn on_started(
        &self,
        url: String,
        src_addr: String,
    ) -> Result<(), SendError<TaskProgressEvent>> {
        let event: TaskProgressEvent = TaskProgressEvent::Started {
            id: self.id,
            ts: Instant::now(),
            url,
            src_addr,
        };
        let sender = self.sender.clone();
        let _ = sender.as_sync().send(event);
        Ok(())
    }

    fn with_fault(
        &self,
        _fault: FaultEvent,
    ) -> Result<(), SendError<TaskProgressEvent>> {
        Ok(())
    }

    fn on_resolved(
        &self,
        _domain: String,
        _time_taken: f64,
    ) -> Result<(), SendError<TaskProgressEvent>> {
        Ok(())
    }

    fn on_completed(
        &self,
        time_taken: Duration,
        from_downstream_length: u64,
        from_upstream_length: u64,
    ) -> Result<(), SendError<TaskProgressEvent>> {
        let event: TaskProgressEvent = TaskProgressEvent::Passthrough {
            id: self.id,
            ts: Instant::now(),
            time_taken,
            from_downstream_length,
            from_upstream_length,
        };
        let sender = self.sender.clone();
        let _ = sender.as_sync().send(event);
        Ok(())
    }

    fn on_first_byte(&self) -> Result<(), SendError<TaskProgressEvent>> {
        Ok(())
    }

    fn on_applied(
        &self,
        _fault: FaultEvent,
    ) -> Result<(), SendError<TaskProgressEvent>> {
        Ok(())
    }

    fn on_response(
        &self,
        _status_code: u16,
    ) -> Result<(), SendError<TaskProgressEvent>> {
        Ok(())
    }

    fn clone_me(&self) -> Box<dyn ProxyTaskEvent> {
        Box::new(self.clone())
    }

    fn on_error(
        &self,
        error: Box<dyn Error>,
    ) -> Result<(), SendError<TaskProgressEvent>> {
        tracing::error!("Tracing error in bypass mode: {}", error);
        Ok(())
    }

    fn get_id(&self) -> TaskId {
        self.id
    }
}

#[derive(Debug)]
pub struct TaskManager {
    pub sender: TaskProgressSender,
    pub receiver: TaskProgressReceiver,
}

impl TaskManager {
    pub fn new() -> Arc<Self> {
        let (sender, receiver) = kanal::unbounded_async();
        Arc::new(TaskManager { sender, receiver: receiver.clone() })
    }

    pub fn get_sender(&self) -> TaskProgressSender {
        self.sender.clone()
    }

    pub fn new_subscriber(&self) -> TaskProgressReceiver {
        self.receiver.clone()
    }

    pub fn next_id(&self) -> TaskId {
        Uuid::new_v4()
    }

    pub async fn new_fault_event(
        &self,
        _url: String,
    ) -> Result<Box<dyn ProxyTaskEvent>, SendError<TaskProgressEvent>> {
        let event_id = self.next_id();
        Ok(Box::new(FaultTaskEvent { id: event_id, sender: self.get_sender() }))
    }

    pub async fn new_passthrough_event(
        &self,
        _url: String,
    ) -> Result<Box<dyn ProxyTaskEvent>, SendError<TaskProgressEvent>> {
        let event_id = self.next_id();
        Ok(Box::new(PassthroughTaskEvent {
            id: event_id,
            sender: self.get_sender(),
        }))
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum FaultEvent {
    Latency {
        direction: Direction,
        side: StreamSide,

        #[serde(
            serialize_with = "serialize_duration_as_millis_f64",
            deserialize_with = "deserialize_duration_from_millis_f64"
        )]
        delay: Option<Duration>,
    },
    Dns {
        direction: Direction,
        side: StreamSide,
        triggered: Option<bool>,
    },
    Bandwidth {
        direction: Direction,
        side: StreamSide,
        bps: Option<usize>,
    },
    Jitter {
        direction: Direction,
        side: StreamSide,
        #[serde(serialize_with = "serialize_duration_as_millis_f64")]
        amplitude: Option<Duration>,
        frequency: Option<f64>,
    },
    PacketLoss {
        state: String,
        direction: Direction,
        side: StreamSide,
    },
    HttpResponseFault {
        direction: Direction,
        side: StreamSide,
        status_code: u16,
        response_body: Option<String>,
    },
    Blackhole {
        side: StreamSide,
        direction: Direction,
    },
    Grpc {
        side: StreamSide,
        direction: Direction,
    },
    Llm {
        direction: Direction,
        side: StreamSide,
        case: LlmCase,
    },
}

impl FaultEvent {
    pub fn event_type(&self) -> String {
        match self {
            FaultEvent::Latency { .. } => "latency".to_string(),
            FaultEvent::Dns { .. } => "dns".to_string(),
            FaultEvent::Bandwidth { .. } => "bandwidth".to_string(),
            FaultEvent::Jitter { .. } => "jitter".to_string(),
            FaultEvent::PacketLoss { .. } => "packetloss".to_string(),
            FaultEvent::HttpResponseFault { .. } => "httperror".to_string(),
            FaultEvent::Blackhole { .. } => "blackhole".to_string(),
            FaultEvent::Grpc { .. } => "grpc".to_string(),
            FaultEvent::Llm { .. } => "llm".to_string(),
        }
    }
}

/// Helper function to serialize `Duration` as `f64` milliseconds using
/// `as_millis_f64()`.
fn serialize_duration_as_millis_f64<S>(
    duration: &Option<Duration>,
    serializer: S,
) -> Result<S::Ok, S::Error>
where
    S: Serializer,
{
    // Utilize the new `as_millis_f64` method
    match duration {
        Some(d) => serializer.serialize_f64(d.as_millis_f64()),
        None => serializer.serialize_none(),
    }
}

pub fn deserialize_duration_from_millis_f64<'de, D>(
    deserializer: D,
) -> Result<Option<Duration>, D::Error>
where
    D: Deserializer<'de>,
{
    #[derive(Deserialize)]
    #[serde(untagged)]
    enum Milli {
        Float(f64),
        Str(String),
    }

    let opt = Option::<Milli>::deserialize(deserializer)?;
    let dur = match opt {
        None => None,
        Some(Milli::Float(ms)) => Some(Duration::from_secs_f64(ms / 1000.0)),
        Some(Milli::Str(s)) => {
            let ms: f64 = s.parse().map_err(de::Error::custom)?;
            Some(Duration::from_secs_f64(ms / 1000.0))
        }
    };

    Ok(dur)
}
