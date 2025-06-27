use std::fmt;
use std::io::Result as IoResult;
use std::pin::Pin;
use std::task::Context;
use std::task::Poll;

use async_trait::async_trait;
use axum::http;
use pin_project::pin_project;
use tokio::io::AsyncRead;
use tokio::io::AsyncWrite;
use tokio::io::AsyncWriteExt;
use tokio::io::ReadBuf;
use tokio::io::split;

use super::Bidirectional;
use super::FaultInjector;
use crate::config::BlackholeSettings;
use crate::config::FaultKind;
use crate::errors::ProxyError;
use crate::event::FaultEvent;
use crate::event::ProxyTaskEvent;
use crate::types::Direction;
use crate::types::StreamSide;

#[pin_project]
#[derive(Debug)]
pub struct BlackholeRead<S> {
    #[pin]
    inner: S,
    event: Option<Box<dyn ProxyTaskEvent>>,
    side: StreamSide,
}

impl<S> BlackholeRead<S> {
    pub fn new(
        inner: S,
        settings: BlackholeSettings,
        event: Option<Box<dyn ProxyTaskEvent>>,
    ) -> Self {
        tracing::info!("Setting up a blackhole on {} side", settings.side);

        BlackholeRead { inner, side: settings.side.clone(), event }
    }
}

impl<S> AsyncRead for BlackholeRead<S>
where
    S: AsyncRead + Unpin,
{
    fn poll_read(
        self: Pin<&mut Self>,
        _cx: &mut Context<'_>,
        _buf: &mut ReadBuf<'_>,
    ) -> Poll<IoResult<()>> {
        let this = self.project();

        if let Some(event) = &*this.event {
            let _ = event.on_applied(FaultEvent::Blackhole {
                direction: Direction::Ingress,
                side: this.side.clone(),
            });
        }

        // Indefinitely block: never return Ready
        Poll::Pending
    }
}

#[pin_project]
#[derive(Debug)]
pub struct BlackholeWrite<S> {
    #[pin]
    inner: S,
    event: Option<Box<dyn ProxyTaskEvent>>,
    side: StreamSide,
}

impl<S> BlackholeWrite<S> {
    pub fn new(
        inner: S,
        settings: BlackholeSettings,
        event: Option<Box<dyn ProxyTaskEvent>>,
    ) -> Self {
        BlackholeWrite { inner, side: settings.side.clone(), event }
    }
}

impl<S> AsyncWrite for BlackholeWrite<S>
where
    S: AsyncWrite + Unpin,
{
    fn poll_write(
        self: Pin<&mut Self>,
        _cx: &mut Context<'_>,
        _buf: &[u8],
    ) -> Poll<IoResult<usize>> {
        let this = self.project();

        if let Some(event) = &*this.event {
            let _ = event.on_applied(FaultEvent::Blackhole {
                direction: Direction::Ingress,
                side: this.side.clone(),
            });
        }

        Poll::Pending
    }

    fn poll_flush(
        self: Pin<&mut Self>,
        _cx: &mut Context<'_>,
    ) -> Poll<IoResult<()>> {
        let this = self.project();

        if let Some(event) = &*this.event {
            let _ = event.on_applied(FaultEvent::Blackhole {
                direction: Direction::Ingress,
                side: this.side.clone(),
            });
        }

        Poll::Pending
    }

    fn poll_shutdown(
        self: Pin<&mut Self>,
        _cx: &mut Context<'_>,
    ) -> Poll<IoResult<()>> {
        let this = self.project();

        if let Some(event) = &*this.event {
            let _ = event.on_applied(FaultEvent::Blackhole {
                direction: Direction::Ingress,
                side: this.side.clone(),
            });
        }

        Poll::Pending
    }
}

#[pin_project]
#[derive(Debug)]
struct BlackholeBidirectional<R, W> {
    #[pin]
    reader: R,
    #[pin]
    writer: W,
}

impl<R, W> BlackholeBidirectional<R, W> {
    fn new(reader: R, writer: W) -> Self {
        Self { reader, writer }
    }
}

#[async_trait::async_trait]
impl<R, W> Bidirectional for BlackholeBidirectional<R, W>
where
    R: AsyncRead + Unpin + Send + std::fmt::Debug,
    W: AsyncWrite + Unpin + Send + std::fmt::Debug,
{
    async fn shutdown(&mut self) -> std::io::Result<()> {
        self.writer.shutdown().await
    }
}

impl<R, W> AsyncRead for BlackholeBidirectional<R, W>
where
    R: AsyncRead + Unpin,
    W: AsyncWrite + Unpin,
{
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<IoResult<()>> {
        self.project().reader.poll_read(cx, buf)
    }
}

impl<R, W> AsyncWrite for BlackholeBidirectional<R, W>
where
    R: AsyncRead + Unpin,
    W: AsyncWrite + Unpin,
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
        tracing::debug!("shutting down write side of blackhole fault");
        self.project().writer.poll_shutdown(cx)
    }
}

#[derive(Debug, Clone)]
pub struct BlackholeInjector {
    pub settings: BlackholeSettings,
}

impl From<&BlackholeSettings> for BlackholeInjector {
    fn from(settings: &BlackholeSettings) -> Self {
        BlackholeInjector { settings: settings.clone() }
    }
}

impl fmt::Display for BlackholeInjector {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "blackhole")
    }
}

#[async_trait]
impl FaultInjector for BlackholeInjector {
    fn is_enabled(&self) -> bool {
        self.settings.enabled
    }

    fn kind(&self) -> FaultKind {
        // e.g. FaultKind::Blackhole (assuming you have that in your enum)
        self.settings.kind
    }

    fn enable(&mut self) {
        self.settings.enabled = true;
    }

    fn disable(&mut self) {
        self.settings.enabled = false;
    }

    fn clone_box(&self) -> Box<dyn FaultInjector> {
        Box::new(self.clone())
    }

    /// The main hook to wrap the underlying stream in blackhole read/write if
    /// enabled.
    async fn inject(
        &self,
        stream: Box<dyn Bidirectional + 'static>,
        event: Box<dyn ProxyTaskEvent>,
        side: StreamSide,
    ) -> Result<
        Box<dyn Bidirectional + 'static>,
        (ProxyError, Box<dyn Bidirectional + 'static>),
    > {
        // If fault not enabled, pass through
        if !self.settings.enabled {
            return Ok(stream);
        }

        // If the side doesn't match (Client vs Server, etc.), pass through
        if side != self.settings.side {
            return Ok(stream);
        }

        let direction = self.settings.direction.clone();
        let (read_half, write_half) = split(stream);

        // Fire an event to record that blackhole is being applied
        let _ = event.with_fault(FaultEvent::Blackhole {
            side: self.settings.side.clone(),
            direction: direction.clone(),
        });

        // If direction includes ingress => blackhole the read side
        let blackhole_read = if direction.is_ingress() {
            Box::new(BlackholeRead::new(
                read_half,
                self.settings.clone(),
                Some(event.clone()),
            )) as Box<dyn super::BidirectionalReadHalf>
        } else {
            Box::new(read_half) as Box<dyn super::BidirectionalReadHalf>
        };

        // If direction includes egress => blackhole the write side
        let blackhole_write = if direction.is_egress() {
            Box::new(BlackholeWrite::new(
                write_half,
                self.settings.clone(),
                Some(event.clone()),
            )) as Box<dyn super::BidirectionalWriteHalf>
        } else {
            Box::new(write_half) as Box<dyn super::BidirectionalWriteHalf>
        };

        let combined =
            BlackholeBidirectional::new(blackhole_read, blackhole_write);
        Ok(Box::new(combined))
    }

    async fn apply_on_request_builder(
        &self,
        builder: reqwest::ClientBuilder,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::ClientBuilder, ProxyError> {
        // no effect at request builder level
        Ok(builder)
    }

    async fn apply_on_request(
        &self,
        req: reqwest::Request,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::Request, ProxyError> {
        // no effect
        Ok(req)
    }

    async fn apply_on_response(
        &self,
        resp: http::Response<Vec<u8>>,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, ProxyError> {
        // no effect
        Ok(resp)
    }
}
