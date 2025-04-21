use std::net::SocketAddr;
use std::sync::Arc;
use std::time::Duration;

use axum::body::Body;
use axum::body::to_bytes;
use axum::http::HeaderMap as AxumHeaderMap;
use axum::http::Request as AxumRequest;
use axum::http::Response as AxumResponse;
use axum::response::IntoResponse;
use hyper::StatusCode;
use reqwest::header::HeaderMap as ReqwestHeaderMap;
use tokio::sync::Mutex;
use tokio::time::Instant;
use url::Url;

use super::ProxyState;
use crate::errors::ProxyError;
use crate::event::ProxyTaskEvent;
use crate::plugin::ProxyPlugin;
use crate::report::types::DnsTiming;
use crate::resolver::TimingResolver;

/// Converts Axum's HeaderMap to Reqwest's HeaderMap.
fn convert_headers_to_reqwest(
    axum_headers: &AxumHeaderMap,
) -> ReqwestHeaderMap {
    let mut reqwest_headers = ReqwestHeaderMap::new();
    for (key, value) in axum_headers.iter() {
        // Optionally filter out headers like Host if needed
        reqwest_headers.insert(key.clone(), value.clone());
    }
    reqwest_headers
}

/// Converts Reqwest's HeaderMap to Axum's HeaderMap.
fn convert_headers_to_axum(
    reqwest_headers: &ReqwestHeaderMap,
) -> AxumHeaderMap {
    let mut axum_headers = AxumHeaderMap::new();
    for (key, value) in reqwest_headers.iter() {
        axum_headers.insert(key.clone(), value.clone());
    }
    axum_headers
}

pub async fn handle_request(
    source_addr: SocketAddr,
    req: AxumRequest<Body>,
    state: Arc<ProxyState>,
    upstream: Url,
    passthrough: bool,
    event: Box<dyn ProxyTaskEvent>,
) -> Result<AxumResponse<Body>, ProxyError> {
    let forward = Forward::new(state.clone());
    forward.execute(source_addr, req, upstream, passthrough, event).await
}

/// Struct responsible for forwarding requests.
#[derive(Debug, Clone)]
pub struct Forward {
    // Shared plugins loaded into the proxy
    state: Arc<ProxyState>,
}

impl Forward {
    /// Creates a new instance of `Forward`.
    pub fn new(state: Arc<ProxyState>) -> Self {
        Self { state }
    }

    /// Executes an Axum request by forwarding it to the target server using
    /// Reqwest.
    ///
    /// Applies plugins after request conversion and after receiving the
    /// response.
    #[tracing::instrument]
    pub async fn execute(
        &self,
        source_addr: SocketAddr,
        request: AxumRequest<Body>,
        upstream: Url,
        passthrough: bool,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<AxumResponse<Body>, ProxyError> {
        let start = Instant::now();
        let _ = event.on_started(upstream.to_string(), source_addr.to_string());

        let method = request.method().clone();
        let headers = request.headers().clone();

        let plugins = self.state.faults_plugin.clone();

        // Extract the request body as bytes
        let body_bytes =
            to_bytes(request.into_body(), usize::MAX).await.map_err(|e| {
                tracing::error!("Failed to read request body: {}", e);
                ProxyError::Internal(format!(
                    "Failed to read request body: {}",
                    e
                ))
            })?;

        let request_bytes = body_bytes.len();

        let mut client_builder = reqwest::Client::builder()
            .pool_idle_timeout(Duration::from_secs(5));

        let dns_timing = Arc::new(Mutex::new(DnsTiming::new()));
        let resolver =
            Arc::new(TimingResolver::new(dns_timing.clone(), event.clone()));
        client_builder = client_builder.dns_resolver(resolver);

        if !passthrough {
            let plugins_lock = plugins.load();
            client_builder = plugins_lock
                .prepare_client(client_builder, event.clone())
                .await
                .unwrap();
        }

        let client = client_builder.build().unwrap();

        // Build the Reqwest request builder
        let req_builder = client
            .request(method.clone(), upstream)
            .headers(convert_headers_to_reqwest(&headers))
            .body(body_bytes.to_vec());

        let mut upstream_req = req_builder.build().map_err(|e| {
            ProxyError::Internal(format!(
                "Failed to build reqwest request: {}",
                e
            ))
        })?;

        let status;
        let resp_headers;
        let resp_body_bytes;
        let mut axum_response;

        if !passthrough {
            let plugins_lock = plugins.load();
            axum_response = match plugins_lock
                .process_request(upstream_req, event.clone())
                .await
            {
                Ok(req) => {
                    // Execute the Reqwest request
                    upstream_req = req;
                    let response = match client.execute(upstream_req).await {
                        Ok(resp) => resp,
                        Err(e) => {
                            let _ = event.on_response(500);

                            let _ = event.on_completed(
                                start.elapsed(),
                                request_bytes as u64,
                                0,
                            );
                            tracing::error!(
                                "Failed to execute reqwest request: {}",
                                e
                            );
                            return Err(ProxyError::Internal(format!(
                                "Failed to execute reqwest request: {}",
                                e
                            )));
                        }
                    };

                    // Extract the response status, headers, and body
                    status = response.status();
                    resp_headers = response.headers().clone();
                    resp_body_bytes = response.bytes().await.map_err(|e| {
                        tracing::error!("Failed to read response body: {}", e);
                        ProxyError::Internal(format!(
                            "Failed to read response body: {}",
                            e
                        ))
                    })?;

                    // Build the Axum response
                    let dummy: AxumResponse<Body> = AxumResponse::default();
                    let (mut parts, _) = dummy.into_parts();

                    parts.status = status;
                    parts.headers = convert_headers_to_axum(&resp_headers);

                    axum_response = AxumResponse::from_parts(
                        parts,
                        resp_body_bytes.to_vec(),
                    );

                    axum_response = {
                        let plugins_lock = plugins.load();
                        let resp = axum_response;
                        plugins_lock
                            .process_response(resp, event.clone())
                            .await
                            .unwrap()
                    };

                    axum_response
                }
                Err(e) => match e {
                    ProxyError::GrpcAbort(response) => response,
                    _ => {
                        //let _ = event.on_error(Box::new(e));
                        let resp = e.into_response();
                        return Ok(resp);
                    }
                },
            };

            drop(plugins_lock);
        } else {
            axum_response = match client.execute(upstream_req).await {
                Ok(r) => {
                    let dummy: AxumResponse<Body> = AxumResponse::default();
                    let (mut parts, _) = dummy.into_parts();
                    parts.status = r.status();
                    resp_headers = r.headers().clone();
                    resp_body_bytes = r.bytes().await.map_err(|e| {
                        tracing::error!("Failed to read response body: {}", e);
                        ProxyError::Internal(format!(
                            "Failed to read response body: {}",
                            e
                        ))
                    })?;

                    parts.headers = convert_headers_to_axum(&resp_headers);
                    AxumResponse::from_parts(parts, resp_body_bytes.to_vec())
                }
                Err(e) => {
                    let _ = event.on_error(Box::new(e));
                    let resp = (
                        StatusCode::INTERNAL_SERVER_ERROR,
                        "Oops, something went wrong",
                    )
                        .into_response();
                    return Ok(resp);
                }
            }
        }

        let (new_parts, new_body) = axum_response.into_parts();

        let new_status = &new_parts.status;
        let _ = event.on_response(new_status.as_u16());

        let response_bytes = new_body.len();
        let axum_response =
            AxumResponse::from_parts(new_parts, Body::from(new_body));

        let _ = event.on_completed(
            start.elapsed(),
            request_bytes as u64,
            response_bytes as u64,
        );
        Ok(axum_response)
    }
}
