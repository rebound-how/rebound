use std::error::Error;
use std::io::Cursor;
use std::io::Result as IoResult;
use std::pin::Pin;
use std::task::Context;
use std::task::Poll;
use std::time::Duration;

use async_trait::async_trait;
use axum::http::Response;
use bytes::BytesMut;
use futures::FutureExt;
use futures::StreamExt;
use futures::TryStreamExt;
use futures::ready;
use http::HeaderMap;
use http::StatusCode;
use hyper::body::Bytes;
use pin_project::pin_project;
use rand::SeedableRng as _;
use rand::rngs::SmallRng;
use rand_distr::Distribution;
use rand_distr::Normal;
use regex::Regex;
use reqwest::Body;
use reqwest::Request as ReqwestRequest;
use serde::Deserialize;
use serde::Serialize;
use serde_json::Value;
use tokio::io::AsyncRead;
use tokio::io::ReadBuf;
use tokio::time::Sleep;
use tokio::time::sleep;
use tokio_util::io::ReaderStream;

use crate::config::FaultKind;
use crate::errors::ProxyError;
use crate::event::FaultEvent;
use crate::event::ProxyTaskEvent;
use crate::fault::BoxChunkStream;
use crate::fault::DelayWrapper;
use crate::fault::FaultInjector;
use crate::fault::FutureDelay;
use crate::types::Direction;
use crate::types::LlmCase;
use crate::types::StreamSide;

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct OpenAiSettings {
    pub case: LlmCase,
    pub pattern: Option<String>,
    pub replacement: Option<String>,
    pub instruction: Option<String>,
    pub probability: f64,
    pub kind: FaultKind,
    pub side: StreamSide,
    pub direction: Direction,
}

/// Injector specialized for OpenAI‐style JSON payloads.
#[derive(Clone, Debug)]
pub struct OpenAiInjector {
    settings: OpenAiSettings,
    regex: Option<Regex>,
}

impl OpenAiInjector {
    pub fn new(settings: OpenAiSettings) -> Self {
        let regex = match &settings.pattern {
            Some(p) => {
                Some(Regex::new(&p).expect("Invalid regex for OpenAI injector"))
            }
            None => None,
        };
        OpenAiInjector { settings, regex }
    }
}

impl From<&OpenAiSettings> for OpenAiInjector {
    fn from(settings: &OpenAiSettings) -> Self {
        OpenAiInjector::new(settings.clone())
    }
}

impl std::fmt::Display for OpenAiInjector {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "openai")
    }
}

#[async_trait]
impl FaultInjector for OpenAiInjector {
    fn is_enabled(&self) -> bool {
        self.settings.probability > 0.0
    }

    fn kind(&self) -> FaultKind {
        self.settings.kind
    }

    fn enable(&mut self) {}
    fn disable(&mut self) {}

    fn clone_box(&self) -> Box<dyn FaultInjector> {
        Box::new(self.clone())
    }

    async fn apply_on_request(
        &self,
        mut request: ReqwestRequest,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<ReqwestRequest, ProxyError> {
        if self.settings.side != StreamSide::Client {
            return Ok(request);
        }

        if !self.settings.direction.is_egress() {
            return Ok(request);
        }

        if rand::random::<f64>() < self.settings.probability {
            let _ = event.with_fault(FaultEvent::Llm {
                direction: Direction::Egress,
                side: StreamSide::Client,
                case: self.settings.case,
            });

            let original_body = request.body();
            if let Some(body) = original_body {
                if let Some(bytes) = body.as_bytes() {
                    let new_body = mutate_request(
                        request.url().path(),
                        bytes.to_vec(),
                        &self.regex,
                        self.settings.replacement.clone(),
                        self.settings.instruction.clone(),
                    )?;

                    let headers = request.headers_mut();
                    headers.remove("content-length");

                    *request.body_mut() = Some(Body::from(new_body));

                    let _ = event.on_applied(FaultEvent::Llm {
                        direction: Direction::Egress,
                        side: StreamSide::Client,
                        case: self.settings.case,
                    });
                }
            }
        }

        Ok(request)
    }

    async fn apply_on_response(
        &self,
        resp: http::Response<Vec<u8>>,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, ProxyError> {
        if self.settings.side != StreamSide::Client {
            return Ok(resp);
        }

        let direction = self.settings.direction.clone();
        if !direction.is_ingress() {
            return Ok(resp);
        }

        if let Some(regex) = &self.regex {
            if let Some(replacement) = &self.settings.replacement {
                if rand::random::<f64>() < self.settings.probability {
                    let (parts, body) = resp.into_parts();
                    let version = parts.version;
                    let status = parts.status;

                    let _ = event.with_fault(FaultEvent::Llm {
                        direction: Direction::Ingress,
                        side: StreamSide::Server,
                        case: self.settings.case,
                    });

                    let mut headers = parts.headers.clone();

                    let new_body;

                    if body.len() > 0 {
                        // triggers recomputing of the content length
                        headers.remove("content-length");

                        new_body =
                            scramble_response(body, &regex, &replacement)?;
                    } else {
                        new_body = body;
                    }

                    let mut intermediate = Response::new(new_body);
                    *intermediate.version_mut() = version;
                    *intermediate.status_mut() = status;
                    *intermediate.headers_mut() = headers;

                    let _ = event.on_applied(FaultEvent::Llm {
                        direction: Direction::Ingress,
                        side: StreamSide::Server,
                        case: self.settings.case,
                    });

                    return Ok(intermediate);
                }
            }
        }

        Ok(resp)
    }

    async fn apply_on_response_stream(
        &self,
        status: StatusCode,
        headers: HeaderMap,
        body: BoxChunkStream,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<(StatusCode, HeaderMap, BoxChunkStream), ProxyError> {
        Ok((status, headers, body))
    }

    async fn inject(
        &self,
        stream: Box<dyn crate::fault::Bidirectional + 'static>,
        _event: Box<dyn ProxyTaskEvent>,
        _side: StreamSide,
    ) -> Result<
        Box<dyn crate::fault::Bidirectional + 'static>,
        (ProxyError, Box<dyn crate::fault::Bidirectional + 'static>),
    > {
        // no-op for TCP
        Ok(stream)
    }

    async fn apply_on_request_builder(
        &self,
        builder: reqwest::ClientBuilder,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::ClientBuilder, ProxyError> {
        Ok(builder)
    }
}

/// Settings for per‐token latency.
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct SlowStreamSettings {
    pub mean_ms: f64,
    pub stddev_ms: Option<f64>,
    pub probability: f64,
    pub kind: FaultKind,
    pub side: StreamSide,
    pub direction: Direction,
}

/// Injector that inserts a random delay before each chunk.
#[derive(Clone, Debug)]
pub struct SlowStreamInjector {
    settings: SlowStreamSettings,
}

impl SlowStreamInjector {
    pub fn new(settings: SlowStreamSettings) -> Self {
        SlowStreamInjector { settings }
    }
}

impl From<&SlowStreamSettings> for SlowStreamInjector {
    fn from(settings: &SlowStreamSettings) -> Self {
        SlowStreamInjector::new(settings.clone())
    }
}

impl std::fmt::Display for SlowStreamInjector {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "slow-stream")
    }
}

#[async_trait]
impl FaultInjector for SlowStreamInjector {
    fn is_enabled(&self) -> bool {
        self.settings.probability > 0.0
    }
    fn kind(&self) -> FaultKind {
        self.settings.kind
    }
    fn enable(&mut self) {}
    fn disable(&mut self) {}
    fn clone_box(&self) -> Box<dyn FaultInjector> {
        Box::new(self.clone())
    }

    // No‐op on TCP streams
    async fn inject(
        &self,
        stream: Box<dyn crate::fault::Bidirectional + 'static>,
        _event: Box<dyn ProxyTaskEvent>,
        _side: StreamSide,
    ) -> Result<
        Box<dyn crate::fault::Bidirectional + 'static>,
        (ProxyError, Box<dyn crate::fault::Bidirectional + 'static>),
    > {
        Ok(stream)
    }

    async fn apply_on_request(
        &self,
        req: ReqwestRequest,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<ReqwestRequest, ProxyError> {
        Ok(req)
    }

    async fn apply_on_response(
        &self,
        resp: http::Response<Vec<u8>>,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, ProxyError> {
        if self.settings.side == StreamSide::Server {
            let _ = event.with_fault(FaultEvent::Llm {
                direction: Direction::Egress,
                side: StreamSide::Server,
                case: LlmCase::SlowStream,
            });

            let delay_ms = self.settings.mean_ms;
            let stddev_ms = self.settings.stddev_ms.unwrap_or(0f64);
            let mut rng = SmallRng::from_os_rng();

            let delay = get_delay(&mut rng, &delay_ms, &stddev_ms);
            sleep(delay).await;

            let _ = event.on_applied(FaultEvent::Llm {
                direction: Direction::Egress,
                side: StreamSide::Server,
                case: LlmCase::SlowStream,
            });
        }

        Ok(resp)
    }

    async fn apply_on_request_builder(
        &self,
        builder: reqwest::ClientBuilder,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::ClientBuilder, ProxyError> {
        Ok(builder)
    }

    async fn apply_on_response_stream(
        &self,
        status: StatusCode,
        mut headers: HeaderMap,
        body: BoxChunkStream,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<(StatusCode, HeaderMap, BoxChunkStream), ProxyError> {
        if rand::random::<f64>() < self.settings.probability {
            let _ = event.with_fault(FaultEvent::Llm {
                direction: Direction::Egress,
                side: StreamSide::Server,
                case: LlmCase::SlowStream,
            });

            let mean = self.settings.mean_ms as f64;
            let stddev = self.settings.stddev_ms.map(|sd| sd as f64);
            let mut rng = SmallRng::from_os_rng();

            // wrap each chunk with an async delay
            let delayed = body.then(move |chunk_res| {
                let event = event.clone();

                let delay_ms = stddev
                    .map(|sd| {
                        Normal::new(mean, sd).unwrap().sample(&mut rng).max(0.0)
                    })
                    .unwrap_or(mean);
                let d = Duration::from_millis(delay_ms as u64);

                async move {
                    sleep(d).await;
                    let _ = event.on_applied(FaultEvent::Llm {
                        direction: Direction::Egress,
                        side: StreamSide::Server,
                        case: LlmCase::SlowStream,
                    });
                    chunk_res
                }
            });

            let boxed: BoxChunkStream = Box::pin(delayed);
            return Ok((status, headers, boxed));
        }

        Ok((status, headers, body))
    }
}

//
// -------------------- Private functions -----------------------------------
//

fn mutate_request(
    path: &str,
    body: Vec<u8>,
    regex: &Option<Regex>,
    replacement: Option<String>,
    instruction: Option<String>,
) -> Result<Vec<u8>, ProxyError> {
    let mut doc: Value = match serde_json::from_slice(&body) {
        Ok(j) => j,
        Err(_) => return Ok(body),
    };

    if path.starts_with("/v1/chat/completion") {
        if let Some(sp) = instruction {
            if let Some(arr) =
                doc.get_mut("messages").and_then(Value::as_array_mut)
            {
                let sys_msg = serde_json::json!({
                    "role": "system",
                    "content": sp,
                });
                arr.insert(arr.len(), sys_msg);
            }
        }

        if let Some(rgx) = regex {
            if let Some(rep) = replacement {
                if let Some(arr) =
                    doc.get_mut("messages").and_then(Value::as_array_mut)
                {
                    for msg in arr {
                        if let Some(content_val) = msg.get_mut("content") {
                            if let Some(orig) = content_val.as_str() {
                                let new =
                                    rgx.replace_all(orig, &rep).to_string();
                                *content_val = Value::String(new);
                            }
                        }
                    }
                }
            }
        }

        let out = serde_json::to_vec(&doc)
            .map_err(|e| ProxyError::Other(e.to_string()))?;

        return Ok(out);
    } else if path.starts_with("/v1/responses") {
        if let Some(sp) = instruction {
            doc["instructions"] = serde_json::Value::String(sp);
        }

        if let (Some(rgx), Some(rep)) = (regex, replacement) {
            if let Some(input_val) = doc.get_mut("input") {
                match input_val {
                    Value::String(s) => {
                        let new = rgx.replace_all(s, rep).to_string();
                        *input_val = Value::String(new);
                    }
                    Value::Array(arr) => {
                        for msg in arr {
                            if let Some(c) = msg.get_mut("content") {
                                if let Some(orig) = c.as_str() {
                                    let new =
                                        rgx.replace_all(orig, &rep).to_string();
                                    *c = Value::String(new);
                                }
                            }
                        }
                    }
                    _ => {}
                }
            }
        }

        let out = serde_json::to_vec(&doc)
            .map_err(|e| ProxyError::Other(e.to_string()))?;

        return Ok(out);
    }

    Ok(body)
}

fn scramble_response(
    body: Vec<u8>,
    regex: &Regex,
    replacement: &str,
) -> Result<Vec<u8>, ProxyError> {
    match serde_json::from_slice::<Value>(&body) {
        Ok(mut doc) => {
            if let Some(object) = doc.get("object").and_then(Value::as_str) {
                if object == "chat.completion" {
                    if let Some(choices) =
                        doc.get_mut("choices").and_then(Value::as_array_mut)
                    {
                        for choice in choices {
                            if let Some(message) = choice.get_mut("message") {
                                if let Some(content_val) =
                                    message.get_mut("content")
                                {
                                    if let Some(orig_str) = content_val.as_str()
                                    {
                                        let replaced = regex
                                            .replace_all(orig_str, replacement)
                                            .to_string();
                                        *content_val = Value::String(replaced);
                                    }
                                }
                            }
                        }
                    }
                    return Ok(serde_json::to_vec(&doc)
                        .map_err(|e| ProxyError::Other(e.to_string()))?);
                } else if object == "response" {
                    if let Some(outputs) =
                        doc.get_mut("output").and_then(Value::as_array_mut)
                    {
                        for output in outputs {
                            if let Some(content) = output
                                .get_mut("content")
                                .and_then(Value::as_array_mut)
                            {
                                for c in content {
                                    if let Some(text) = c.get_mut("text") {
                                        if let Some(orig_str) = text.as_str() {
                                            let replaced = regex
                                                .replace_all(
                                                    orig_str,
                                                    replacement,
                                                )
                                                .to_string();
                                            *text = Value::String(replaced);
                                        }
                                    }
                                }
                            }
                        }
                    }
                    return Ok(serde_json::to_vec(&doc)
                        .map_err(|e| ProxyError::Other(e.to_string()))?);
                }
            }
        }
        Err(e) => {
            tracing::error!("Failed to parse OpenAI-like response: {:?}", e)
        }
    }

    Ok(body)
}

fn get_delay(rng: &mut SmallRng, mean: &f64, stddev: &f64) -> Duration {
    let normal = Normal::new(*mean, *stddev).unwrap();
    let mut sample = normal.sample(rng);
    while sample < 0.0 {
        sample = normal.sample(rng);
    }

    let millis = sample.floor() as u64;
    let nanos = ((sample - millis as f64) * 1_000_000.0).round() as u32;
    Duration::from_millis(millis) + Duration::from_nanos(nanos as u64)
}
