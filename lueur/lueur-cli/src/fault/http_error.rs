use std::fmt;

use async_trait::async_trait;
use axum::http::Response;
use axum::http::{self};
use hyper::StatusCode;
use reqwest::ClientBuilder as ReqwestClientBuilder;
use reqwest::Request as ReqwestRequest;

use super::Bidirectional;
use super::FaultInjector;
use crate::config::HttpResponseSettings;
use crate::errors::ProxyError;
use crate::event::FaultEvent;
use crate::event::ProxyTaskEvent;
use crate::types::{Direction, StreamSide};

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
        HttpResponseFaultInjector { settings: settings.clone() }
    }
}

#[async_trait]
impl FaultInjector for HttpResponseFaultInjector {
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
            let _ = event.on_applied(
                FaultEvent::HttpResponseFault {
                    direction: Direction::Ingress,
                    side: StreamSide::Server, 
                    status_code: self.settings.http_response_status_code,
                    response_body: self.settings.http_response_body.clone(),
                }
            );

            let (parts, body) = resp.into_parts();
            let version = parts.version;
            let status =
                StatusCode::from_u16(self.settings.http_response_status_code)
                    .unwrap();
            let headers = parts.headers.clone();

            // Reconstruct the HTTP response with the limited body
            let mut intermediate = Response::new(body);
            *intermediate.version_mut() = version;
            *intermediate.status_mut() = status;
            *intermediate.headers_mut() = headers;

            tracing::debug!("Setting response status code {}", status);

            return Ok(intermediate);
        }
        Ok(resp)
    }

    /// Injects HTTP response faults into tunnel streams.
    fn inject(
        &self,
        stream: Box<dyn Bidirectional + 'static>,
        _event: Box<dyn ProxyTaskEvent>,
        _side: StreamSide,
    ) -> Box<dyn Bidirectional + 'static> {
        // HTTP Response Faults are primarily applied during request processing.
        // Tunnel stream faults like duplication, loss, etc., are different.
        // Therefore, no action is taken here.
        stream
    }
}
