use std::fmt;
use std::fmt::Debug;
use std::io;
use std::pin::Pin;
use std::str::FromStr;
use std::task::Context;
use std::task::Poll;
use std::time::Duration;

use async_trait::async_trait;
use axum::body::Body;
use axum::http;
use futures::Future;
use futures::ready;
use http::HeaderMap;
use hyper::StatusCode;
use pin_project::pin_project;
use reqwest::Body as ReqwestBody;
use tokio::io::AsyncRead;
use tokio::io::AsyncWrite;
use tokio::io::ReadBuf;
use tonic::transport::Channel;

use super::Bidirectional;
use super::FaultInjector;
use crate::config::FaultKind;
use crate::config::GrpcSettings;
use crate::errors::ProxyError;
use crate::event::FaultEvent;
use crate::event::ProxyTaskEvent;
use crate::fault::BoxChunkStream;
use crate::plugin::rpc::service;
use crate::plugin::rpc::service::plugin_service_client::PluginServiceClient;
use crate::types::Direction;
use crate::types::StreamSide;

// Plugin instructions about the chunk
enum ProcessAction {
    /// No change to the data.
    PassThrough,
    /// Replace the original chunk with the provided data.
    Replace,
    /// Do not send any data yet (buffering).
    Buffer,
    /// Close the tunnel immediately.
    Close,
}

impl ProcessAction {
    fn from_i32(value: i32) -> ProcessAction {
        match value {
            1 => ProcessAction::PassThrough,
            2 => ProcessAction::Replace,
            3 => ProcessAction::Buffer,
            4 => ProcessAction::Close,
            _ => ProcessAction::PassThrough,
        }
    }
}

pub trait FutureGrpcResult:
    Future<
        Output = Result<
            tonic::Response<service::ProcessTunnelDataResponse>,
            ProxyError,
        >,
    > + Send
    + Debug
{
}

pub struct GrpcResultWrapper<F> {
    future: F,
}

impl<F> GrpcResultWrapper<F> {
    pub fn new(future: F) -> Self {
        tracing::info!("Setting up a grpc wrapper");

        Self { future }
    }
}

impl<F> std::fmt::Debug for GrpcResultWrapper<F> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "GrpcResultWrapper(...)")
    }
}

impl<F> Future for GrpcResultWrapper<F>
where
    F: Future<
            Output = Result<
                tonic::Response<service::ProcessTunnelDataResponse>,
                ProxyError,
            >,
        > + Send,
{
    type Output =
        Result<tonic::Response<service::ProcessTunnelDataResponse>, ProxyError>;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        let inner = unsafe { self.map_unchecked_mut(|s| &mut s.future) };
        Future::poll(inner, cx)
    }
}

impl<F> FutureGrpcResult for GrpcResultWrapper<F> where
    F: Future<
            Output = Result<
                tonic::Response<service::ProcessTunnelDataResponse>,
                ProxyError,
            >,
        > + Send
{
}

#[derive(Debug)]
#[pin_project]
pub struct GrpcPluginStream {
    #[pin]
    inner: Box<dyn Bidirectional + 'static>,
    plugin: PluginServiceClient<Channel>,
    side: StreamSide,
    direction: Direction,
    event: Box<dyn ProxyTaskEvent>,
    pending_read: Vec<u8>,
    processing_future_read: Option<Pin<Box<dyn FutureGrpcResult>>>,
    pending_write: Vec<u8>,
    #[pin]
    processing_future_write: Option<Pin<Box<dyn FutureGrpcResult>>>,
}

#[async_trait::async_trait]
impl Bidirectional for GrpcPluginStream {
    async fn shutdown(&mut self) -> std::io::Result<()> {
        self.inner.shutdown().await
    }
}

impl GrpcPluginStream {
    pub fn new(
        inner: Box<dyn Bidirectional + 'static>,
        plugin: PluginServiceClient<Channel>,
        side: StreamSide,
        direction: Direction,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Self {
        Self {
            inner,
            plugin,
            side,
            direction,
            event,
            pending_read: Vec::new(),
            processing_future_read: None,
            pending_write: Vec::new(),
            processing_future_write: None,
        }
    }

    /// Initiate asynchronous processing of the given chunk via the plugin.
    pub fn process_read_chunk(
        &mut self,
        chunk: Vec<u8>,
    ) -> Result<(), ProxyError> {
        let mut plugin = self.plugin.clone();
        let d = 0;

        let s = match self.side {
            StreamSide::Client => 0,
            StreamSide::Server => 1,
        };

        let id = self.event.get_id().to_string();

        let fut = async move {
            tracing::warn!("read chunk is: {}", chunk.len());
            let req = service::ProcessTunnelDataRequest {
                id,
                direction: d,
                side: s,
                chunk,
            };

            plugin.process_tunnel_data(tonic::Request::new(req)).await.map_err(
                |e| {
                    tracing::error!(
                        "Failed processing read tunneled data {}",
                        e
                    );
                    return ProxyError::GrpcError(e);
                },
            )
        };
        self.processing_future_read =
            Some(Box::pin(GrpcResultWrapper::new(fut)));

        Ok(())
    }

    /// Initiate asynchronous processing of the given chunk for writes via the
    /// plugin.
    pub fn process_write_chunk(
        &mut self,

        chunk: Vec<u8>,
    ) -> Result<(), ProxyError> {
        let mut plugin = self.plugin.clone();
        let d = 1;

        let s = match self.side {
            StreamSide::Client => 0,
            StreamSide::Server => 1,
        };

        let id = self.event.get_id().to_string();

        let fut = async move {
            tracing::warn!("write chunk is: {}", chunk.len());
            let req = service::ProcessTunnelDataRequest {
                id,
                direction: d,
                side: s,
                chunk,
            };

            plugin.process_tunnel_data(tonic::Request::new(req)).await.map_err(
                |e| {
                    tracing::error!(
                        "Failed processing write tunneled data: {}",
                        e
                    );
                    ProxyError::GrpcError(e)
                },
            )
        };

        // Notice we assign the future to the write-specific field.
        self.processing_future_write =
            Some(Box::pin(GrpcResultWrapper::new(fut)));
        Ok(())
    }
}

impl AsyncRead for GrpcPluginStream {
    fn poll_read(
        mut self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<io::Result<()>> {
        // If we have pending data from a previous plugin call, deliver it.
        if !self.pending_read.is_empty() {
            let to_copy =
                std::cmp::min(buf.remaining(), self.pending_read.len());
            buf.put_slice(&self.pending_read[..to_copy]);
            self.pending_read.drain(..to_copy);
            return Poll::Ready(Ok(()));
        }

        // If we already initiated a plugin call, poll it.
        if let Some(fut) = &mut self.processing_future_read {
            match fut.as_mut().poll(cx) {
                Poll::Ready(Ok(result)) => {
                    self.processing_future_read = None;
                    let resp = result.into_inner();
                    match resp.action {
                        Some(service::process_tunnel_data_response::Action::PassThrough(r)) => {
                            // Buffer the processed data so we can deliver it.
                            self.pending_read.extend(r.chunk);
                        }
                        Some(service::process_tunnel_data_response::Action::Replace(r)) => {
                            self.pending_read.extend(r.modified_chunk);
                        }
                        Some(service::process_tunnel_data_response::Action::Buffer(m)) => {
                            // the plugin may have told us roughly how long we may need
                            // before it might release its held data buffer
                            if let Some(delay_ms) = Some(m.estimated_time_to_release_ms) {
                                let delay = tokio::time::sleep(Duration::from_millis(delay_ms as u64));
                                tokio::spawn(async move { delay.await; });
                            }

                            return Poll::Pending;
                        }
                        Some(service::process_tunnel_data_response::Action::Close(_)) => {
                            // Indicate end-of-stream by returning 0 bytes.
                            return Poll::Ready(Ok(()));
                        }
                        None => {
                            return Poll::Ready(Err(io::Error::new(
                                io::ErrorKind::Other,
                                "Missing action in plugin response",
                            )));
                        }
                    }
                    // Try again now that we may have pending data.
                    return self.poll_read(cx, buf);
                }
                Poll::Ready(Err(e)) => {
                    return Poll::Ready(Err(io::Error::other(e.to_string())));
                }
                Poll::Pending => {
                    // The plugin call is still pending.
                    return Poll::Pending;
                }
            }
        }

        // Otherwise, attempt to read from the inner stream.
        let mut temp_buf = [0u8; 4096];
        let mut read_buf = ReadBuf::new(&mut temp_buf);
        match Pin::new(&mut self.inner).poll_read(cx, &mut read_buf) {
            Poll::Ready(Ok(())) => {
                let n = read_buf.filled().len();
                if n == 0 {
                    // End-of-stream.
                    return Poll::Ready(Ok(()));
                }
                let chunk = read_buf.filled().to_vec();
                self.process_read_chunk(chunk)
                    .map_err(|e| io::Error::other(e.to_string()))?;
                cx.waker().wake_by_ref();
                Poll::Pending
            }
            other => other,
        }
    }
}

impl AsyncWrite for GrpcPluginStream {
    fn poll_write(
        mut self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &[u8],
    ) -> Poll<Result<usize, io::Error>> {
        {
            let mut this = self.as_mut().project();

            // 1) If there's pending data, flush it first.
            if !this.pending_write.is_empty() {
                let inner = this.inner.as_mut();
                let n = ready!(inner.poll_write(cx, &this.pending_write))?;
                this.pending_write.drain(..n);
                // If still not empty, we need another poll to flush the rest
                if !this.pending_write.is_empty() {
                    return Poll::Pending;
                }
                // If fully flushed, from the caller's perspective we've
                // "written" its buf.
                return Poll::Ready(Ok(buf.len()));
            }

            // 2) If there's an active plugin future, poll it.
            if let Some(fut) =
                this.processing_future_write.as_mut().as_pin_mut()
            {
                match fut.poll(cx) {
                    Poll::Ready(Ok(resp)) => {
                        // Future is done, remove it
                        this.processing_future_write.set(None);
                        let resp = resp.into_inner();

                        // Check the oneof action in the response
                        match resp.action {
                            Some(service::process_tunnel_data_response::Action::Replace(r)) => {
                                // Store the plugin output in `pending_write`.
                                this.pending_write.extend(r.modified_chunk);
                            }
                            Some(service::process_tunnel_data_response::Action::PassThrough(r)) => {
                                // If plugin returns an empty chunk in pass-through,
                                // assume we should forward the original data.
                                if r.chunk.is_empty() {
                                    this.pending_write.extend(buf);
                                } else {
                                    this.pending_write.extend(r.chunk);
                                }
                            }
                            Some(service::process_tunnel_data_response::Action::Buffer(_)) => {
                                // Plugin wants more data, so we do nothing except wait.
                                return Poll::Pending;
                            }
                            Some(service::process_tunnel_data_response::Action::Close(_)) => {
                                // The plugin signals to close. Treat that as 0 bytes written.
                                return Poll::Ready(Ok(0));
                            }
                            None => {
                                return Poll::Ready(Err(io::Error::new(
                                    io::ErrorKind::Other,
                                    "Missing action in plugin response",
                                )));
                            }
                        }

                        // We now have data in `pending_write`, so schedule
                        // another poll to actually
                        // write it to the inner stream
                        cx.waker().wake_by_ref();
                        return Poll::Pending;
                    }
                    Poll::Ready(Err(e)) => {
                        return Poll::Ready(Err(io::Error::new(
                            io::ErrorKind::Other,
                            e.to_string(),
                        )));
                    }
                    Poll::Pending => {
                        return Poll::Pending;
                    }
                }
            }
        }

        // 3) If there's no pending data and no active plugin future, we
        //    initiate a new plugin call.
        // We'll store that future in `processing_future_write`.
        // In your real code, you'd do something like:
        match self.as_mut().get_mut().process_write_chunk(buf.to_vec()) {
            Ok(()) => {
                // Now that the plugin future is set up, re-poll.
                cx.waker().wake_by_ref();
                Poll::Pending
            }
            Err(e) => Poll::Ready(Err(io::Error::new(
                io::ErrorKind::Other,
                e.to_string(),
            ))),
        }
    }

    fn poll_flush(
        mut self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<Result<(), io::Error>> {
        self.project().inner.poll_flush(cx)
    }

    fn poll_shutdown(
        mut self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<Result<(), io::Error>> {
        tracing::debug!("shutting down write side of gRPC plugin fault");
        self.project().inner.poll_shutdown(cx)
    }
}

#[derive(Debug, Clone)]
pub struct GrpcInjector {
    pub settings: GrpcSettings,
    pub client: PluginServiceClient<Channel>,
}

impl GrpcInjector {
    pub fn new(
        settings: GrpcSettings,
        client: PluginServiceClient<Channel>,
    ) -> Self {
        Self { settings, client }
    }
}

impl fmt::Display for GrpcInjector {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "grpc")
    }
}

#[async_trait]
impl FaultInjector for GrpcInjector {
    fn is_enabled(&self) -> bool {
        self.settings.enabled
    }

    fn kind(&self) -> FaultKind {
        FaultKind::Grpc
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

    #[tracing::instrument]
    async fn inject(
        &self,
        stream: Box<dyn Bidirectional + 'static>,
        event: Box<dyn ProxyTaskEvent>,
        side: StreamSide,
    ) -> Result<
        Box<dyn Bidirectional + 'static>,
        (ProxyError, Box<dyn Bidirectional + 'static>),
    > {
        /*if let Some(c) = self.settings.clone().capabilities {
            if !c.tunnel {
                return Ok(stream);
            }
        };*/

        if side != self.settings.side {
            return Ok(stream);
        }

        let direction = self.settings.direction.clone();

        let _ = event.with_fault(FaultEvent::Grpc {
            direction: direction.clone(),
            side: self.settings.side.clone(),
        });

        Ok(Box::new(GrpcPluginStream::new(
            stream,
            self.client.clone(),
            side.clone(),
            self.settings.direction.clone(),
            event,
        )))
    }

    #[tracing::instrument]
    async fn apply_on_response(
        &self,
        resp: http::Response<Vec<u8>>,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, crate::errors::ProxyError> {
        if let Some(c) = self.settings.clone().capabilities {
            if !c.forward {
                return Ok(resp);
            }
        };

        // Extract status, version, and headers
        let (parts, modified_response) = resp.into_parts();

        let status: http::StatusCode = parts.status;
        let version = parts.version;

        let headers = parts
            .headers
            .iter()
            .map(|(name, value)| service::HttpHeader {
                name: name.to_string(),
                // Convert the header value to a string; if conversion fails,
                // use an empty string.
                value: value.to_str().unwrap_or_default().to_string(),
            })
            .collect::<Vec<_>>();

        let mut new_resp = service::HttpResponse {
            status_code: u32::from(status.as_u16()),
            headers,
            body: modified_response,
        };

        let req = service::ProcessHttpResponseRequest {
            response: Some(new_resp.clone()),
        };

        let response = self
            .client
            .clone()
            .process_http_response(tonic::Request::new(req))
            .await
            .map_err(|e| {
                ProxyError::RpcCallError(
                    self.settings.name.clone(),
                    "ProcessResponse".to_string(),
                    e,
                )
            })?;

        let resp: service::ProcessHttpResponseResponse = response.into_inner();

        if resp.action == 0 {
            new_resp = match resp.modified_response {
                Some(r) => r,
                None => new_resp,
            }
        }

        // Build a new http::Response with the modified body
        let mut builder =
            http::Response::builder().status(status).version(version);

        for header in new_resp.headers.iter() {
            let header_name =
                http::HeaderName::from_bytes(header.name.as_bytes())?;
            let header_value = http::HeaderValue::from_str(&header.value)?;
            builder = builder.header(header_name, header_value);
        }

        // forces the proxy to recompute the length
        let _ =
            builder.headers_mut().unwrap().remove("content-length").unwrap();

        let http_response = builder.body(new_resp.body)?;

        Ok(http_response)
    }

    #[tracing::instrument]
    async fn apply_on_request_builder(
        &self,
        builder: reqwest::ClientBuilder,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::ClientBuilder, crate::errors::ProxyError> {
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

    #[tracing::instrument]
    async fn apply_on_request(
        &self,
        request: reqwest::Request,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::Request, crate::errors::ProxyError> {
        if let Some(c) = self.settings.clone().capabilities {
            if !c.forward {
                return Ok(request);
            }
        };

        // Extract method, URL, and headers from the request before consuming
        // the body.
        let method = request.method().clone();
        let mut url = request.url().clone();

        // Consume the request to access its body.
        let body = request.body().unwrap();

        // Fully read the request body into memory as bytes.
        // `body.bytes()` reads the entire body and returns `Bytes`.
        let body_bytes = body.as_bytes().unwrap();

        // Convert the Bytes into a Vec<u8> for passing to the plugins
        let modified_request = body_bytes.to_vec();

        let headers = request
            .headers()
            .iter()
            .map(|(name, value)| service::HttpHeader {
                name: name.to_string(),
                // Convert the header value to a string; if conversion fails,
                // use an empty string.
                value: value.to_str().unwrap_or_default().to_string(),
            })
            .collect::<Vec<_>>();

        let mut fullpath = url.path().to_string();
        if let Some(query) = request.url().query() {
            fullpath.push('?');
            fullpath.push_str(query);
        }

        let mut new_request = service::HttpRequest {
            method: method.to_string(),
            path: fullpath,
            headers,
            body: modified_request,
        };

        let http_req = service::ProcessHttpRequestRequest {
            request: Some(new_request.clone()),
        };

        let response = self
            .client
            .clone()
            .process_http_request(tonic::Request::new(http_req))
            .await
            .map_err(|e| {
                ProxyError::RpcCallError(
                    self.settings.name.clone(),
                    "ProcessRequest".to_string(),
                    e,
                )
            })?;

        let resp = response.into_inner();

        // continue
        if resp.action == 0 {
            new_request = match resp.modified_request {
                Some(r) => r,
                None => new_request,
            }
        // abort
        } else if resp.action == 1 {
            // when a plugin asks to abort, it returns an actual response
            // to be immediately sent to the client
            let abort_response = resp.abort_response.unwrap();

            let axum_response: http::Response<Body> = http::Response::default();
            let (mut parts, _) = axum_response.into_parts();

            parts.status =
                StatusCode::from_u16(abort_response.status_code as u16)
                    .unwrap();

            for header in abort_response.headers.iter() {
                let header_name =
                    http::HeaderName::from_bytes(header.name.as_bytes())?;
                let header_value = http::HeaderValue::from_str(&header.value)?;
                parts.headers.append(header_name, header_value);
            }

            let http_response =
                http::Response::from_parts(parts, abort_response.body);

            return Err(ProxyError::GrpcAbort(http_response));
        }

        // Rebuild a new `reqwest::Request` using the same method, URL, and
        // headers. Assign the modified body as the request body.
        let new_method =
            reqwest::Method::from_str(new_request.method.as_str()).unwrap();
        url.set_path(&new_request.path);
        let mut new_req = reqwest::Request::new(new_method, url);

        let mut header_map = http::HeaderMap::new();
        for header in new_request.headers {
            let header_name =
                http::HeaderName::from_bytes(header.name.as_bytes())?;
            let header_value = http::HeaderValue::from_str(&header.value)?;
            header_map.append(header_name, header_value);
        }
        *new_req.headers_mut() = header_map;
        *new_req.body_mut() = Some(reqwest::Body::from(new_request.body));

        Ok(new_req)
    }
}
