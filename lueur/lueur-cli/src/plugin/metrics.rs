use std::fmt;
use std::io::Cursor;
use std::pin::Pin;
use std::task::Context;
use std::task::Poll;

use axum::http;
use axum::async_trait;
use bytes::BytesMut;
use reqwest::Body;
use futures::StreamExt;
use pin_project::pin_project;
use tokio::io::AsyncRead;
use tokio::io::AsyncWrite;
use tokio::io::ReadBuf;
use tokio_util::io::ReaderStream;
use hyper::http::Response;

use crate::errors::ProxyError;
use crate::event::ProxyTaskEvent;
use crate::fault::Bidirectional;
use crate::fault::FaultInjector;
use crate::types::StreamSide;

#[derive(Debug)]
pub struct MetricsInjector {
}

impl MetricsInjector {
    pub fn new() -> MetricsInjector {
        Self { }
    }
}

impl fmt::Display for MetricsInjector {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "metrics")
    }
}

impl Clone for MetricsInjector {
    fn clone(&self) -> Self {
        Self { }
    }
}

#[async_trait]
impl FaultInjector for MetricsInjector {
    fn inject(
        &self,
        stream: Box<dyn Bidirectional + 'static>,
        event: Box<dyn ProxyTaskEvent>,
        _side: StreamSide,
    ) -> Box<dyn Bidirectional + 'static> {
        Box::new(WrapperStream::new(stream, self.clone(), event.clone()))
    }

    async fn apply_on_response(
        &self,
        resp: http::Response<Vec<u8>>,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, crate::errors::ProxyError> {
        let (parts, body) = resp.into_parts();
        let version = parts.version;
        let status = parts.status;
        let headers = parts.headers.clone();

        let owned_body = Cursor::new(body);

        let reader = WrapperStream::new(owned_body, self.clone(), event.clone());

        let mut reader_stream = ReaderStream::new(reader);

        let mut buffer = BytesMut::new();
        while let Some(chunk) = reader_stream.next().await {
            buffer.extend_from_slice(&chunk?);
        }
        let response_body = buffer.to_vec();

        // Reconstruct the HTTP response with the limited body
        let mut intermediate = Response::new(response_body);
        *intermediate.version_mut() = version;
        *intermediate.status_mut() = status;
        *intermediate.headers_mut() = headers;

        Ok(intermediate)
    }

    async fn apply_on_request_builder(
        &self,
        builder: reqwest::ClientBuilder,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::ClientBuilder, crate::errors::ProxyError> {
        Ok(builder)
    }

    async fn apply_on_request(
        &self,
        request: reqwest::Request,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::Request, crate::errors::ProxyError> {
        
        let original_body = request.body();
        if let Some(body) = original_body {
            if let Some(bytes) = body.as_bytes() {
                let owned_bytes = Cursor::new(bytes.to_vec());

                let latency_read = WrapperStream::new(owned_bytes, self.clone(), event.clone());

                let reader_stream = ReaderStream::new(latency_read);

                let new_body = Body::wrap_stream(reader_stream);
                let mut builder = request.try_clone().ok_or_else(|| {
                    ProxyError::Other("Couldn't clone request".into())
                })?;
                *builder.body_mut() = Some(new_body);

                Ok(builder)
            } else {
                // If the body doesn't have bytes, leave it unchanged
                Ok(request)
            }
        } else {
            // If there's no body, leave the request unchanged
            Ok(request)
        }
    }
}

#[derive(Debug)]
#[pin_project]
pub struct WrapperStream<S> {
    #[pin]
    stream: S,
    #[pin]
    injector: MetricsInjector,
    event: Box<dyn ProxyTaskEvent>,
    ttfb_event_sent: bool,
}

impl<S> WrapperStream<S> {
    fn new(
        stream: S,
        injector: MetricsInjector,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Self {
        Self {
            stream,
            injector,
            event,
            ttfb_event_sent: false
        }
    }
}

impl <S: AsyncRead + Unpin> AsyncRead for WrapperStream<S> {
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<std::io::Result<()>> {
        let mut this = self.project();

        if  !*this.ttfb_event_sent {
            *this.ttfb_event_sent = true;
            let _ = this.event.on_first_byte();
        }

        Pin::new(&mut this.stream).poll_read(cx, buf)
    }
}

impl <S: AsyncWrite + Unpin> AsyncWrite for WrapperStream<S> {
    fn poll_write(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &[u8],
    ) -> Poll<std::io::Result<usize>> {
        let mut this = self.project();
        Pin::new(&mut this.stream).poll_write(cx, buf)
    }

    fn poll_flush(
        mut self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<std::io::Result<()>> {
        Pin::new(&mut self.stream).poll_flush(cx)
    }

    fn poll_shutdown(
        mut self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<std::io::Result<()>> {
        Pin::new(&mut self.stream).poll_shutdown(cx)
    }
}
