use std::fmt;
use std::io::Cursor;
use std::io::Result as IoResult;
use std::pin::Pin;
use std::task::Context;
use std::task::Poll;

use async_trait::async_trait;
use axum::http;
use bytes::BytesMut;
use futures::StreamExt;
use http::HeaderMap;
use http::StatusCode;
use hyper::http::Response;
use pin_project::pin_project;
use rand::SeedableRng;
use rand::rngs::SmallRng;
use rand_distr::Distribution;
use rand_distr::Normal;
use rand_distr::Pareto;
use rand_distr::Uniform;
use reqwest::Body;
use tokio::io::AsyncRead;
use tokio::io::AsyncWrite;
use tokio::io::AsyncWriteExt;
use tokio::io::ReadBuf;
use tokio::io::split;
use tokio::time::Duration;
use tokio::time::Sleep;
use tokio::time::sleep;
use tokio_util::io::ReaderStream;

use super::Bidirectional;
use super::BidirectionalReadHalf;
use super::BidirectionalWriteHalf;
use super::FaultInjector;
use crate::config::FaultKind;
use crate::config::LatencySettings;
use crate::errors::ProxyError;
use crate::event::FaultEvent;
use crate::event::ProxyTaskEvent;
use crate::fault::BoxChunkStream;
use crate::types::Direction;
use crate::types::LatencyDistribution;
use crate::types::StreamSide;

#[derive(Debug)]
pub struct LatencyInjector {
    settings: LatencySettings,
}

impl From<&LatencySettings> for LatencyInjector {
    fn from(settings: &LatencySettings) -> Self {
        tracing::info!("Setting up latency on {} side", settings.side);
        LatencyInjector { settings: settings.clone() }
    }
}

impl fmt::Display for LatencyInjector {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "latency")
    }
}

impl Clone for LatencyInjector {
    fn clone(&self) -> Self {
        Self { settings: self.settings.clone() }
    }
}

impl LatencyInjector {
    #[tracing::instrument]
    fn get_delay(&self, rng: &mut SmallRng) -> Duration {
        match &self.settings.distribution {
            LatencyDistribution::Normal => {
                let normal = Normal::new(
                    self.settings.latency_mean,
                    self.settings.latency_stddev,
                )
                .unwrap();
                let mut sample = normal.sample(rng);
                while sample < 0.0 {
                    sample = normal.sample(rng);
                }

                let millis = sample.floor() as u64;
                let nanos =
                    ((sample - millis as f64) * 1_000_000.0).round() as u32;
                Duration::from_millis(millis)
                    + Duration::from_nanos(nanos as u64)
            }
            LatencyDistribution::Pareto => {
                let pareto = Pareto::new(
                    self.settings.latency_scale,
                    self.settings.latency_shape,
                )
                .unwrap();
                let mut sample = pareto.sample(rng);
                while sample < 0.0 {
                    sample = pareto.sample(rng);
                }

                let millis = sample.floor() as u64;
                let nanos =
                    ((sample - millis as f64) * 1_000_000.0).round() as u32;
                Duration::from_millis(millis)
                    + Duration::from_nanos(nanos as u64)
            }
            LatencyDistribution::ParetoNormal => {
                let pareto = Pareto::new(
                    self.settings.latency_scale,
                    self.settings.latency_shape,
                )
                .unwrap();
                let mut pareto_sample = pareto.sample(rng);
                while pareto_sample < 0.0 {
                    pareto_sample = pareto.sample(rng);
                }

                let normal = Normal::new(
                    self.settings.latency_mean,
                    self.settings.latency_stddev,
                )
                .unwrap();
                let mut normal_sample = normal.sample(rng);
                while normal_sample < 0.0 {
                    normal_sample = normal.sample(rng);
                }

                let total = pareto_sample + normal_sample;
                let millis = total.floor() as u64;
                let nanos =
                    ((total - millis as f64) * 1_000_000.0).round() as u32;
                Duration::from_millis(millis)
                    + Duration::from_nanos(nanos as u64)
            }
            LatencyDistribution::Uniform => {
                let uniform = Uniform::new(
                    self.settings.latency_min,
                    self.settings.latency_max,
                )
                .unwrap();
                let mut sample = uniform.sample(rng);
                while sample < 0.0 {
                    sample = uniform.sample(rng);
                }

                let millis = sample.floor() as u64;
                let nanos =
                    ((sample - millis as f64) * 1_000_000.0).round() as u32;
                Duration::from_millis(millis)
                    + Duration::from_nanos(nanos as u64)
            }
        }
    }
}

/// A bidirectional stream that wraps limited reader and writer.
#[derive(Debug)]
#[pin_project]
struct LatencyBidirectional<R, W> {
    #[pin]
    reader: R,
    #[pin]
    writer: W,
}

impl<R, W> LatencyBidirectional<R, W>
where
    R: AsyncRead + Send + Unpin,
    W: AsyncWrite + Send + Unpin,
{
    fn new(reader: R, writer: W) -> Self {
        Self { reader, writer }
    }
}

#[async_trait::async_trait]
impl<R, W> Bidirectional for LatencyBidirectional<R, W>
where
    R: AsyncRead + Unpin + Send + std::fmt::Debug,
    W: AsyncWrite + Unpin + Send + std::fmt::Debug,
{
    async fn shutdown(&mut self) -> std::io::Result<()> {
        self.writer.shutdown().await
    }
}

impl<R, W> AsyncRead for LatencyBidirectional<R, W>
where
    R: AsyncRead + Send + Unpin,
    W: AsyncWrite + Send + Unpin,
{
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<IoResult<()>> {
        self.project().reader.poll_read(cx, buf)
    }
}

impl<R, W> AsyncWrite for LatencyBidirectional<R, W>
where
    R: AsyncRead + Send + Unpin,
    W: AsyncWrite + Send + Unpin,
{
    fn poll_write(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &[u8],
    ) -> Poll<IoResult<usize>> {
        self.project().writer.poll_write(cx, buf)
    }

    fn poll_flush(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<IoResult<()>> {
        self.project().writer.poll_flush(cx)
    }

    fn poll_shutdown(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<IoResult<()>> {
        tracing::debug!("shutting down write side of Latency fault");
        self.project().writer.poll_shutdown(cx)
    }
}

#[async_trait]
impl FaultInjector for LatencyInjector {
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

    /// Injects latency into a bidirectional stream.
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
        if side != self.settings.side {
            return Ok(stream);
        }

        let (read_half, write_half) = split(stream);

        let direction = self.settings.direction.clone();

        let _ = event.with_fault(FaultEvent::Latency {
            direction: direction.clone(),
            side: self.settings.side.clone(),
            delay: None,
        });

        // Wrap the read half if ingress or both directions are specified
        let limited_read: Box<dyn BidirectionalReadHalf> =
            if direction.is_ingress() {
                match LatencyStreamRead::new(
                    read_half,
                    self.clone(),
                    Some(event.clone()),
                ) {
                    Ok(lr) => Box::new(lr),
                    Err(rh) => {
                        Box::new(rh) // Fallback to the original read half
                    }
                }
            } else {
                Box::new(read_half) as Box<dyn BidirectionalReadHalf>
            };

        // Wrap the write half if egress or both directions are specified
        let limited_write: Box<dyn BidirectionalWriteHalf> =
            if direction.is_egress() {
                match LatencyStreamWrite::new(
                    write_half,
                    self.clone(),
                    Some(event.clone()),
                ) {
                    Ok(lw) => Box::new(lw),
                    Err(wh) => Box::new(wh),
                }
            } else {
                Box::new(write_half) as Box<dyn BidirectionalWriteHalf>
            };

        // Combine the limited read and write into a new bidirectional stream
        let limited_bidirectional =
            LatencyBidirectional::new(limited_read, limited_write);

        Ok(Box::new(limited_bidirectional))
    }

    #[tracing::instrument]
    async fn apply_on_response(
        &self,
        resp: http::Response<Vec<u8>>,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, crate::errors::ProxyError> {
        if self.settings.side == StreamSide::Server {
            let _ = event.with_fault(FaultEvent::Latency {
                direction: Direction::Ingress,
                side: StreamSide::Server,
                delay: None,
            });

            let (parts, body) = resp.into_parts();
            let version = parts.version;
            let status = parts.status;
            let headers = parts.headers.clone();

            let owned_body = Cursor::new(body);

            let reader = LatencyStreamRead::new(
                owned_body,
                self.clone(),
                Some(event.clone()),
            )
            .unwrap();

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

            return Ok(intermediate);
        }

        Ok(resp)
    }

    #[tracing::instrument]
    async fn apply_on_request_builder(
        &self,
        builder: reqwest::ClientBuilder,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::ClientBuilder, crate::errors::ProxyError> {
        Ok(builder)
    }

    #[tracing::instrument]
    async fn apply_on_request(
        &self,
        request: reqwest::Request,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::Request, crate::errors::ProxyError> {
        if self.settings.side == StreamSide::Client {
            let _ = event.with_fault(FaultEvent::Latency {
                direction: Direction::Egress,
                side: StreamSide::Client,
                delay: None,
            });

            let original_body = request.body();
            if let Some(body) = original_body {
                if let Some(bytes) = body.as_bytes() {
                    let owned_bytes = Cursor::new(bytes.to_vec());

                    let latency_read = LatencyStreamRead::new(
                        owned_bytes,
                        self.clone(),
                        Some(event.clone()),
                    )
                    .unwrap();

                    let reader_stream = ReaderStream::new(latency_read);

                    let new_body = Body::wrap_stream(reader_stream);
                    let mut builder = request.try_clone().ok_or_else(|| {
                        ProxyError::Other("Couldn't clone request".into())
                    })?;
                    *builder.body_mut() = Some(new_body);

                    return Ok(builder);
                } else {
                    // If the body doesn't have bytes, leave it unchanged
                    return Ok(request);
                }
            } else {
                // If there's no body, leave the request unchanged
                return Ok(request);
            }
        }

        Ok(request)
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

#[derive(Debug)]
#[pin_project]
pub struct LatencyStreamRead<S> {
    #[pin]
    stream: S,
    #[pin]
    injector: LatencyInjector,
    #[pin]
    rng: SmallRng,
    event: Option<Box<dyn ProxyTaskEvent>>,
    side: StreamSide,
    read_sleep: Option<Pin<Box<Sleep>>>,
    #[pin]
    delay: Duration,
    applied_count: usize,
}

impl<S> LatencyStreamRead<S>
where
    S: AsyncRead + Unpin + std::fmt::Debug,
{
    /// Creates a new LatencyStreamRead with the specified bandwidth
    /// options.
    ///
    /// # Arguments
    ///
    /// * `inner` - The underlying stream to wrap.
    /// * `options` - The bandwidth throttling options.
    /// * `event` - An optional event handler for fault events.
    pub fn new(
        inner: S,
        injector: LatencyInjector,
        event: Option<Box<dyn ProxyTaskEvent>>,
    ) -> Result<Self, S> {
        let side = injector.settings.side.clone();
        Ok(LatencyStreamRead {
            stream: inner,
            injector,
            rng: SmallRng::from_os_rng(),
            event: event.clone(),
            side,
            read_sleep: None,
            delay: Duration::new(0, 0),
            applied_count: 0,
        })
    }
}

impl<S: AsyncRead + Unpin + std::fmt::Debug> AsyncRead
    for LatencyStreamRead<S>
{
    #[tracing::instrument]
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<std::io::Result<()>> {
        let mut this = self.project();

        let injector: Pin<&mut LatencyInjector> = this.injector;
        let settings = &injector.settings;

        // when in global mode, we don't add latency on each read op, just once
        if settings.global && *this.applied_count == 1 {
            return Pin::new(&mut this.stream).poll_read(cx, buf);
        }

        let mut rng = this.rng;
        if this.read_sleep.is_none() {
            let delay = injector.get_delay(&mut rng);
            *this.delay = delay;
            this.read_sleep.replace(Box::pin(sleep(delay)));
        }

        if let Some(delay) = this.read_sleep.as_mut() {
            match delay.as_mut().poll(cx) {
                Poll::Ready(_) => {
                    // we are done with the delay
                    this.read_sleep.take();
                    let event = this.event;
                    if event.is_some() {
                        let _ = event.clone().unwrap().on_applied(
                            FaultEvent::Latency {
                                direction: Direction::Ingress,
                                side: this.side.clone(),
                                delay: Some(*this.delay),
                            },
                        );
                    }
                    *this.applied_count += 1;
                    return this.stream.poll_read(cx, buf);
                }
                Poll::Pending => {
                    return Poll::Pending;
                }
            }
        }

        Pin::new(&mut this.stream).poll_read(cx, buf)
    }
}

#[derive(Debug)]
#[pin_project]
pub struct LatencyStreamWrite<S> {
    #[pin]
    stream: S,
    #[pin]
    injector: LatencyInjector,
    #[pin]
    rng: SmallRng,
    event: Option<Box<dyn ProxyTaskEvent>>,
    side: StreamSide,
    write_sleep: Option<Pin<Box<Sleep>>>,
    applied_count: usize,
}

impl<S> LatencyStreamWrite<S>
where
    S: AsyncWrite + Unpin,
{
    /// Creates a new LatencyStreamWrite with the specified bandwidth
    /// options.
    ///
    /// # Arguments
    ///
    /// * `inner` - The underlying stream to wrap.
    /// * `options` - The bandwidth throttling options.
    /// * `event` - An optional event handler for fault events.
    pub fn new(
        inner: S,
        injector: LatencyInjector,
        event: Option<Box<dyn ProxyTaskEvent>>,
    ) -> Result<Self, S> {
        let side = injector.settings.side.clone();
        Ok(LatencyStreamWrite {
            stream: inner,
            injector,
            rng: SmallRng::from_os_rng(),
            event: event.clone(),
            side,
            write_sleep: None,
            applied_count: 0,
        })
    }
}

impl<S: AsyncWrite + Unpin + std::fmt::Debug> AsyncWrite
    for LatencyStreamWrite<S>
{
    #[tracing::instrument]
    fn poll_write(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &[u8],
    ) -> Poll<std::io::Result<usize>> {
        let mut this = self.project();

        let injector: Pin<&mut LatencyInjector> = this.injector;
        let settings = &injector.settings;

        // when in global mode, we don't add latency on each write op, just once
        if settings.global && *this.applied_count == 1 {
            return Pin::new(&mut this.stream).poll_write(cx, buf);
        }

        let mut rng = this.rng;

        if this.write_sleep.is_none() {
            let delay = injector.get_delay(&mut rng);
            let event = this.event;
            if event.is_some() {
                let _ =
                    event.clone().unwrap().on_applied(FaultEvent::Latency {
                        direction: Direction::Egress,
                        side: this.side.clone(),
                        delay: Some(delay),
                    });
            }
            this.write_sleep.replace(Box::pin(sleep(delay)));
        }

        if let Some(delay) = this.write_sleep.as_mut() {
            match delay.as_mut().poll(cx) {
                Poll::Ready(_) => {
                    this.write_sleep.take();
                    *this.applied_count += 1;
                    return this.stream.poll_write(cx, buf);
                }
                Poll::Pending => {
                    return Poll::Pending;
                }
            }
        }

        Pin::new(&mut this.stream).poll_write(cx, buf)
    }

    #[tracing::instrument]
    fn poll_flush(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<std::io::Result<()>> {
        let mut this = self.project();
        Pin::new(&mut this.stream).poll_flush(cx)
    }

    #[tracing::instrument]
    fn poll_shutdown(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<std::io::Result<()>> {
        let mut this = self.project();
        Pin::new(&mut this.stream).poll_shutdown(cx)
    }
}
