use std::fmt;

use async_trait::async_trait;
use axum::http::Response;
use axum::http::header::HeaderValue;
use http::HeaderMap;
use http::StatusCode;
use regex::Regex;
use reqwest::Body;
use reqwest::Request as ReqwestRequest;
use serde::Deserialize;
use serde::Serialize;
use serde_json::Value;

use crate::config::FaultKind;
use crate::errors::ProxyError;
use crate::event::ProxyTaskEvent;
use crate::fault::BoxChunkStream;
use crate::fault::FaultInjector;
use crate::types::StreamSide;

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct ContentInjectSettings {
    pub pattern: String,
    pub replacement: String,
    pub probability: f64,
    pub kind: FaultKind,
}

#[derive(Clone, Debug)]
pub struct ContentInjector {
    settings: ContentInjectSettings,
    regex: Regex,
}

impl ContentInjector {
    pub fn new(settings: ContentInjectSettings) -> Self {
        let regex = Regex::new(&settings.pattern)
            .expect("Invalid regex for content fault");
        ContentInjector { settings, regex }
    }
}

impl fmt::Display for ContentInjector {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "content")
    }
}

#[async_trait]
impl FaultInjector for ContentInjector {
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
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<ReqwestRequest, ProxyError> {
        if rand::random::<f64>() < self.settings.probability {
            let original_body = request.body();
            if let Some(body) = original_body {
                if let Some(bytes) = body.as_bytes() {
                    let body = String::from_utf8_lossy(bytes).to_string();
                    let new_body = self
                        .regex
                        .replace_all(&body, &self.settings.replacement)
                        .to_string();
                    request.headers_mut().insert(
                        axum::http::header::CONTENT_LENGTH,
                        HeaderValue::from_str(&new_body.len().to_string())
                            .unwrap(),
                    );
                    *request.body_mut() = Some(Body::from(new_body));
                }
            }
        }

        Ok(request)
    }

    async fn apply_on_response(
        &self,
        mut resp: Response<Vec<u8>>,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<Response<Vec<u8>>, ProxyError> {
        if rand::random::<f64>() < self.settings.probability {
            let body = String::from_utf8_lossy(resp.body()).to_string();
            let new_body = self
                .regex
                .replace_all(&body, &self.settings.replacement)
                .to_string();
            resp.headers_mut().insert(
                axum::http::header::CONTENT_LENGTH,
                HeaderValue::from_str(&new_body.len().to_string()).unwrap(),
            );
            *resp.body_mut() = new_body.into_bytes();
        }
        Ok(resp)
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
        Ok(stream)
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
        headers: HeaderMap,
        body: BoxChunkStream,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<(StatusCode, HeaderMap, BoxChunkStream), ProxyError> {
        Ok((status, headers, body))
    }
}
