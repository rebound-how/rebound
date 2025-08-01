use std::fmt;
use std::io::Cursor;
use std::io::Result as IoResult;
use std::num::NonZeroU32;
use std::pin::Pin;
use std::sync::Arc;
use std::task::Context;
use std::task::Poll;

use async_trait::async_trait;
use axum::http;
use bytes::BytesMut;
use futures::FutureExt;
use futures::StreamExt;
use governor::Quota;
use governor::RateLimiter;
use governor::clock::DefaultClock;
use governor::state::InMemoryState;
use governor::state::direct::NotKeyed;
use http::HeaderMap;
use http::StatusCode;
use pin_project::pin_project;
use reqwest::Body;
use reqwest::ClientBuilder;
use reqwest::Request;
use tokio::io::AsyncRead;
use tokio::io::AsyncWrite;
use tokio::io::AsyncWriteExt;
use tokio::io::ReadBuf;
use tokio::io::split;
use tokio_util::io::ReaderStream;

use super::Bidirectional;
use super::BidirectionalReadHalf;
use super::BidirectionalWriteHalf;
use super::FaultInjector;
use crate::config::BandwidthSettings;
use crate::config::FaultKind;
use crate::errors::ProxyError;
use crate::event::FaultEvent;
use crate::event::ProxyTaskEvent;
use crate::fault::BoxChunkStream;
use crate::fault::DelayWrapper;
use crate::fault::FutureDelay;
use crate::types::Direction;
use crate::types::StreamSide;

type Limiter = RateLimiter<NotKeyed, InMemoryState, DefaultClock>;

/// BandwidthLimitedWrite wraps an AsyncWrite stream and limits the write
/// bandwidth.
#[derive(Debug)]
#[pin_project]
pub struct BandwidthLimitedWrite<S> {
    #[pin]
    inner: S,
    limiter: Option<Arc<Limiter>>,
    event: Option<Box<dyn ProxyTaskEvent>>,
    #[pin]
    delay: Option<Pin<Box<dyn FutureDelay>>>,
    max_write_size: usize,
    side: StreamSide,
}

impl<S> BandwidthLimitedWrite<S>
where
    S: AsyncWrite + Unpin,
{
    /// Creates a new BandwidthLimitedWrite with the specified bandwidth
    /// options.
    ///
    /// # Arguments
    ///
    /// * `inner` - The underlying stream to wrap.
    /// * `options` - The bandwidth throttling options.
    /// * `event` - An optional event handler for fault events.
    pub fn new(
        inner: S,
        settings: BandwidthSettings,
        event: Option<Box<dyn ProxyTaskEvent>>,
    ) -> Result<Self, S> {
        // Initialize egress limiter based on strategy
        let rate_bps = settings
            .bandwidth_unit
            .to_bytes_per_second(settings.bandwidth_rate);
        if rate_bps == 0 {
            return Err(inner);
        }
        let quota = match NonZeroU32::new(rate_bps as u32) {
            Some(q) => Quota::per_second(q),
            None => return Err(inner), /* Fail if quota cannot be
                                        * created */
        };

        Ok(BandwidthLimitedWrite {
            inner,
            limiter: Some(Arc::new(RateLimiter::direct(quota))),
            event,
            delay: None,
            side: settings.side,
            max_write_size: rate_bps,
        })
    }
}

/// BandwidthLimitedRead wraps an AsyncRead stream and limits the read
/// bandwidth.
#[derive(Debug)]
#[pin_project]
pub struct BandwidthLimitedRead<S> {
    #[pin]
    inner: S,
    limiter: Option<Arc<Limiter>>,
    #[pin]
    delay: Option<Pin<Box<dyn FutureDelay>>>,
    event: Option<Box<dyn ProxyTaskEvent>>,
    max_read_size: usize,
    side: StreamSide,
}

impl<S> BandwidthLimitedRead<S>
where
    S: AsyncRead + Unpin,
{
    /// Creates a new BandwidthLimitedRead with the specified bandwidth options.
    ///
    /// # Arguments
    ///
    /// * `inner` - The underlying stream to wrap.
    /// * `options` - The bandwidth throttling options.
    /// * `event` - An optional event handler for fault events.
    pub fn new(
        inner: S,
        settings: BandwidthSettings,
        event: Option<Box<dyn ProxyTaskEvent>>,
    ) -> Result<Self, S> {
        let rate_bps = settings
            .bandwidth_unit
            .to_bytes_per_second(settings.bandwidth_rate);
        if rate_bps == 0 {
            return Err(inner);
        }
        let quota = match NonZeroU32::new(rate_bps as u32) {
            Some(q) => Quota::per_second(q),
            None => return Err(inner), /* Fail if quota cannot be
                                        * created */
        };

        Ok(BandwidthLimitedRead {
            inner,
            limiter: Some(Arc::new(RateLimiter::direct(quota))),
            event,
            delay: None,
            side: settings.side,
            max_read_size: rate_bps,
        })
    }
}

impl<S: AsyncWrite + Unpin> AsyncWrite for BandwidthLimitedWrite<S> {
    fn poll_write(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &[u8],
    ) -> Poll<IoResult<usize>> {
        tracing::info!("poll_write: {}", buf.len());

        let mut this = self.project();

        let limiter = match this.limiter.as_ref().cloned() {
            Some(l) => l,
            None => return Pin::new(&mut this.inner).poll_write(cx, buf),
        };

        let requested = buf.len();
        let to_write = requested.min(*this.max_write_size);
        if to_write == 0 {
            return Poll::Ready(Ok(0));
        }
        let permit = NonZeroU32::new(to_write as u32).unwrap();

        if this.delay.is_none() {
            let lim = limiter.clone();
            let fut = async move {
                if let Err(err) = lim.until_n_ready(permit).await {
                    tracing::warn!("Rate limiter error: {}", err);
                }
            };
            this.delay.set(Some(Box::pin(DelayWrapper::new(fut))));
        }

        if let Some(delay) = this.delay.as_mut().as_pin_mut() {
            match delay.poll(cx) {
                Poll::Pending => {
                    return Poll::Pending;
                }
                Poll::Ready(_) => {
                    this.delay.set(None);
                }
            }
        }

        match Pin::new(&mut this.inner).poll_write(cx, &buf[..to_write]) {
            Poll::Ready(Ok(written)) => {
                tracing::info!(
                    "Buffer size {} => limited bandwidth write {} bytes",
                    requested,
                    written
                );
                if let Some(evt) = &*this.event {
                    let _ = evt.on_applied(FaultEvent::Bandwidth {
                        direction: Direction::Egress,
                        side: this.side.clone(),
                        bps: Some(written),
                    });
                }
                Poll::Ready(Ok(written))
            }
            other => other,
        }
    }

    fn poll_flush(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<IoResult<()>> {
        let mut this = self.project();
        Pin::new(&mut this.inner).poll_flush(cx)
    }

    fn poll_shutdown(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<IoResult<()>> {
        let mut this = self.project();
        Pin::new(&mut this.inner).poll_shutdown(cx)
    }
}

impl<S: AsyncRead + Unpin> AsyncRead for BandwidthLimitedRead<S> {
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<IoResult<()>> {
        let mut this = self.project();

        if let Some(limiter) = this.limiter.as_ref().cloned() {
            let requested_read = buf.remaining();
            let to_read = std::cmp::min(*this.max_read_size, requested_read);
            if to_read == 0 {
                return Poll::Ready(Ok(()));
            }

            let permit_nz = match NonZeroU32::new(to_read as u32) {
                Some(nz) => nz,
                None => return Poll::Ready(Ok(())),
            };

            let fut = limiter.until_n_ready(permit_nz);
            let mut fut = Box::pin(fut);

            match fut.as_mut().poll(cx) {
                Poll::Ready(Ok(())) => {
                    let mut limited_buf =
                        ReadBuf::new(&mut buf.initialize_unfilled()[..to_read]);

                    match this.inner.poll_read(cx, &mut limited_buf) {
                        Poll::Ready(Ok(())) => {
                            let filled = limited_buf.filled().len();
                            buf.advance(filled);

                            tracing::info!(
                                "Buffer size {} => limited bandwidth to read {} bytes",
                                requested_read,
                                filled
                            );
                            if let Some(event) = &*this.event {
                                let _ =
                                    event.on_applied(FaultEvent::Bandwidth {
                                        direction: Direction::Ingress,
                                        side: this.side.clone(),
                                        bps: Some(filled),
                                    });
                            }

                            Poll::Ready(Ok(()))
                        }
                        other => other,
                    }
                }
                Poll::Ready(Err(_)) => Poll::Ready(Err(std::io::Error::new(
                    std::io::ErrorKind::Other,
                    "Rate limiter error",
                ))),
                Poll::Pending => Poll::Pending,
            }
        } else {
            this.inner.poll_read(cx, buf)
        }
    }
}

/// A bidirectional stream that wraps limited reader and writer.
#[derive(Debug)]
#[pin_project]
struct BandwidthLimitedBidirectional<R, W> {
    #[pin]
    reader: R,
    #[pin]
    writer: W,
}

impl<R, W> BandwidthLimitedBidirectional<R, W>
where
    R: AsyncRead + Send + Unpin + std::fmt::Debug,
    W: AsyncWrite + Send + Unpin + std::fmt::Debug,
{
    fn new(reader: R, writer: W) -> Self {
        Self { reader, writer }
    }
}

#[async_trait::async_trait]
impl<R, W> Bidirectional for BandwidthLimitedBidirectional<R, W>
where
    R: AsyncRead + Unpin + Send + std::fmt::Debug,
    W: AsyncWrite + Unpin + Send + std::fmt::Debug,
{
    async fn shutdown(&mut self) -> std::io::Result<()> {
        self.writer.shutdown().await
    }
}

impl<R, W> AsyncRead for BandwidthLimitedBidirectional<R, W>
where
    R: AsyncRead + Send + Unpin + std::fmt::Debug,
    W: AsyncWrite + Send + Unpin + std::fmt::Debug,
{
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<IoResult<()>> {
        self.project().reader.poll_read(cx, buf)
    }
}

impl<R, W> AsyncWrite for BandwidthLimitedBidirectional<R, W>
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
        tracing::debug!("shutting down write side of bandwidth fault");
        self.project().writer.poll_shutdown(cx)
    }
}

#[derive(Debug, Clone)]
pub struct BandwidthLimitFaultInjector {
    pub settings: BandwidthSettings,
}

impl From<&BandwidthSettings> for BandwidthLimitFaultInjector {
    fn from(settings: &BandwidthSettings) -> Self {
        BandwidthLimitFaultInjector { settings: settings.clone() }
    }
}

impl fmt::Display for BandwidthLimitFaultInjector {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "bandwidth")
    }
}

#[async_trait]
impl FaultInjector for BandwidthLimitFaultInjector {
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

        let _ = event.with_fault(FaultEvent::Bandwidth {
            direction: direction.clone(),
            side: self.settings.side.clone(),
            bps: None,
        });

        // Wrap the read half if ingress or both directions are specified
        let limited_read: Box<dyn BidirectionalReadHalf> =
            if direction.is_ingress() {
                match BandwidthLimitedRead::new(
                    read_half,
                    self.settings.clone(),
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
                match BandwidthLimitedWrite::new(
                    write_half,
                    self.settings.clone(),
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
            BandwidthLimitedBidirectional::new(limited_read, limited_write);

        Ok(Box::new(limited_bidirectional))
    }

    async fn apply_on_request_builder(
        &self,
        builder: ClientBuilder,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<ClientBuilder, ProxyError> {
        Ok(builder)
    }

    /// Applies bandwidth limiting to an outgoing request.
    async fn apply_on_request(
        &self,
        request: Request,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<Request, ProxyError> {
        if self.settings.side == StreamSide::Client {
            let _ = event.with_fault(FaultEvent::Bandwidth {
                direction: Direction::Egress,
                side: StreamSide::Client,
                bps: None,
            });

            let original_body = request.body();
            if let Some(body) = original_body {
                if let Some(bytes) = body.as_bytes() {
                    let owned_bytes = Cursor::new(bytes.to_vec());

                    // Wrap the owned bytes with BandwidthLimitedRead
                    let bandwidth_limited_read = BandwidthLimitedRead::new(
                        owned_bytes,
                        self.settings.clone(),
                        Some(event.clone()),
                    )
                    .unwrap();

                    let reader_stream =
                        ReaderStream::new(bandwidth_limited_read);

                    let new_body = Body::wrap_stream(reader_stream);
                    let mut builder = request.try_clone().ok_or_else(|| {
                        ProxyError::Other("Couldn't clone request".into())
                    })?;
                    *builder.body_mut() = Some(new_body);

                    return Ok(builder);
                } else {
                    return Ok(request);
                }
            } else {
                return Ok(request);
            }
        }

        Ok(request)
    }

    async fn apply_on_response(
        &self,
        resp: http::Response<Vec<u8>>,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, ProxyError> {
        if self.settings.side == StreamSide::Server {
            let _ = event.with_fault(FaultEvent::Bandwidth {
                direction: Direction::Ingress,
                side: StreamSide::Server,
                bps: None,
            });

            let (parts, body) = resp.into_parts();
            let version = parts.version;
            let status = parts.status;
            let headers = parts.headers.clone();

            let owned_body = Cursor::new(body);

            let reader = BandwidthLimitedRead::new(
                owned_body,
                self.settings.clone(),
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
            let mut intermediate = http::Response::new(response_body);
            *intermediate.version_mut() = version;
            *intermediate.status_mut() = status;
            *intermediate.headers_mut() = headers;

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
}
