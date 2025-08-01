use std::fmt;

use async_trait::async_trait;
use axum::http::Response;
use axum::http::{self};
use http::HeaderMap;
use hyper::StatusCode;
use reqwest::Body;
use reqwest::ClientBuilder as ReqwestClientBuilder;
use reqwest::Request as ReqwestRequest;

use super::Bidirectional;
use super::FaultInjector;
use crate::config::FaultKind;
use crate::config::HttpResponseSettings;
use crate::errors::ProxyError;
use crate::event::FaultEvent;
use crate::event::ProxyTaskEvent;
use crate::fault::BoxChunkStream;
use crate::types::Direction;
use crate::types::StreamSide;

#[derive(Debug, Clone)]
pub struct HttpResponseFaultInjector {
    pub settings: HttpResponseSettings,
}

impl fmt::Display for HttpResponseFaultInjector {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "http")
    }
}

impl From<&HttpResponseSettings> for HttpResponseFaultInjector {
    fn from(settings: &HttpResponseSettings) -> Self {
        tracing::info!("Setting up HTTP error");
        HttpResponseFaultInjector { settings: settings.clone() }
    }
}

#[async_trait]
impl FaultInjector for HttpResponseFaultInjector {
    fn is_enabled(&self) -> bool {
        self.settings.enabled
    }

    fn kind(&self) -> FaultKind {
        self.settings.kind
    }

    fn enable(&mut self) {
        self.settings.enabled = true
    }

    fn disable(&mut self) {
        self.settings.enabled = false
    }

    fn clone_box(&self) -> Box<dyn FaultInjector> {
        Box::new(self.clone())
    }

    async fn apply_on_request_builder(
        &self,
        builder: ReqwestClientBuilder,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<ReqwestClientBuilder, ProxyError> {
        // No modifications needed for the client builder in this fault injector
        Ok(builder)
    }

    /// Applies bandwidth limiting to an outgoing request.
    async fn apply_on_request(
        &self,
        request: ReqwestRequest,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<ReqwestRequest, ProxyError> {
        Ok(request)
    }

    async fn apply_on_response(
        &self,
        resp: http::Response<Vec<u8>>,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, ProxyError> {
        if rand::random::<f64>()
            < self.settings.http_response_trigger_probability
        {
            let status_code = self.settings.http_response_status_code;
            let new_body = self.settings.http_response_body.clone();

            let _ = event.with_fault(FaultEvent::HttpResponseFault {
                direction: Direction::Ingress,
                side: StreamSide::Server,
                status_code,
                response_body: new_body.clone(),
            });

            let (parts, mut body) = resp.into_parts();
            let version = parts.version;
            let status = StatusCode::from_u16(status_code).unwrap();
            let mut headers = parts.headers.clone();

            if new_body.is_some() {
                body = new_body.clone().unwrap().into_bytes();
                // force to recompute length
                headers.remove("content-length");
            }

            let mut intermediate = Response::new(body);
            *intermediate.version_mut() = version;
            *intermediate.status_mut() = status;
            *intermediate.headers_mut() = headers;

            let _ = event.on_applied(FaultEvent::HttpResponseFault {
                direction: Direction::Ingress,
                side: StreamSide::Server,
                status_code: self.settings.http_response_status_code,
                response_body: new_body,
            });

            return Ok(intermediate);
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
        stream: Box<dyn Bidirectional + 'static>,
        _event: Box<dyn ProxyTaskEvent>,
        _side: StreamSide,
    ) -> Result<
        Box<dyn Bidirectional + 'static>,
        (ProxyError, Box<dyn Bidirectional + 'static>),
    > {
        // This is opaque data for us (tunneling is done over encrypted stream)
        // so we can't modify any of its content.
        // maybe someday we will...
        Ok(stream)
    }
}
