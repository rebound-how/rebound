use std::fmt;
use std::fmt::Debug;
use std::io::Cursor;
use std::io::Result as IoResult;
use std::pin::Pin;
use std::task::Context;
use std::task::Poll;

use async_trait::async_trait;
use axum::http;
use bytes::BytesMut;
use futures::StreamExt;
use pin_project::pin_project;
use rand::Rng;
use rand::SeedableRng;
use rand::rngs::SmallRng;
use reqwest::Body;
use reqwest::Request as ReqwestRequest;
use tokio::io::AsyncRead;
use tokio::io::AsyncWrite;
use tokio::io::ReadBuf;
use tokio::io::split;
use tokio_util::io::ReaderStream;

use super::Bidirectional;
use super::BidirectionalReadHalf;
use super::BidirectionalWriteHalf;
use super::FaultInjector;
use crate::config::FaultKind;
use crate::config::PacketLossSettings;
use crate::errors::ProxyError;
use crate::event::FaultEvent;
use crate::event::ProxyTaskEvent;
use crate::types::Direction;
use crate::types::StreamSide;

/// Enumeration of packet loss strategies.
#[derive(Debug, Clone)]
pub enum PacketLossStrategy {
    /// Multi-State Markov Model packet loss strategy.
    MultiStateMarkov {
        transition_matrix: Vec<Vec<f64>>, /* Rows and columns correspond to
                                           * states */
        loss_probabilities: Vec<f64>, // Packet loss probability for each state
    },
}

impl Default for PacketLossStrategy {
    fn default() -> Self {
        PacketLossStrategy::MultiStateMarkov {
            transition_matrix: vec![
                // Excellent state transitions
                vec![0.9, 0.1, 0.0, 0.0, 0.0],
                // Good state transitions
                vec![0.05, 0.9, 0.05, 0.0, 0.0],
                // Fair state transitions
                vec![0.0, 0.1, 0.8, 0.1, 0.0],
                // Poor state transitions
                vec![0.0, 0.0, 0.2, 0.7, 0.1],
                // Bad state transitions
                vec![0.0, 0.0, 0.0, 0.3, 0.7],
            ],
            loss_probabilities: vec![
                0.0, // Excellent: No packet loss in an optimal state.
                0.1, /* Good: Still a relatively good state but with a small
                      * chance. */
                0.3, /* Fair: Noticeable loss; simulates moderate network
                      * degradation. */
                0.6, // Poor: High probability of loss.
                0.9, // Bad: Nearly all packets get dropped.
            ],
        }
    }
}

/// Enumeration representing the different network states in the Markov model.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum MultiState {
    Excellent,
    Good,
    Fair,
    Poor,
    Bad,
    // Extend with more states if needed
}

impl fmt::Display for MultiState {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            MultiState::Excellent => write!(f, "excellent"),
            MultiState::Good => write!(f, "good"),
            MultiState::Fair => write!(f, "fair"),
            MultiState::Poor => write!(f, "poor"),
            MultiState::Bad => write!(f, "bad"),
        }
    }
}

impl MultiState {
    /// Creates a `MultiState` from a given index.
    fn from_index(index: usize) -> Self {
        match index {
            0 => MultiState::Excellent,
            1 => MultiState::Good,
            2 => MultiState::Fair,
            3 => MultiState::Poor,
            4 => MultiState::Bad,
            _ => MultiState::Good, // Default fallback
        }
    }

    /// Converts a `MultiState` to its corresponding index.
    fn to_index(self) -> usize {
        match self {
            MultiState::Excellent => 0,
            MultiState::Good => 1,
            MultiState::Fair => 2,
            MultiState::Poor => 3,
            MultiState::Bad => 4,
        }
    }
}

/// PacketLossLimitedRead wraps an AsyncRead stream and applies packet loss
/// based on the Multi-State Markov Model.
#[derive(Debug)]
#[pin_project]
pub struct PacketLossLimitedRead<S> {
    #[pin]
    inner: S,
    strategy: PacketLossStrategy,
    state: MultiState,                        // Current state
    transition_matrix: Option<Vec<Vec<f64>>>, // Only for MultiStateMarkov
    loss_probabilities: Option<Vec<f64>>,     // Only for MultiStateMarkov
    event: Option<Box<dyn ProxyTaskEvent>>,
    side: StreamSide,
    rng: SmallRng,
}

impl<S> PacketLossLimitedRead<S> {
    /// Creates a new PacketLossLimitedRead.
    ///
    /// # Arguments
    ///
    /// * `inner` - The underlying AsyncRead stream.
    /// * `options` - The packet loss options.
    /// * `event` - An optional event handler for fault events.
    pub fn new(
        inner: S,
        settings: PacketLossSettings,
        event: Option<Box<dyn ProxyTaskEvent>>,
    ) -> Self {
        let strategy = PacketLossStrategy::default();
        let (transition_matrix, loss_probabilities) = match strategy {
            PacketLossStrategy::MultiStateMarkov {
                ref transition_matrix,
                ref loss_probabilities,
            } => (
                Some(transition_matrix.clone()),
                Some(loss_probabilities.clone()),
            ),
        };

        PacketLossLimitedRead {
            inner,
            strategy,
            state: MultiState::Good,
            transition_matrix,
            loss_probabilities,
            event,
            side: settings.side.clone(),
            rng: SmallRng::from_os_rng(),
        }
    }
}

impl<S> AsyncRead for PacketLossLimitedRead<S>
where
    S: AsyncRead + Unpin,
{
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<IoResult<()>> {
        let this = self.project();
        // Determine if the packet should be dropped based on the current state
        let should_drop = match &this.strategy {
            PacketLossStrategy::MultiStateMarkov {
                transition_matrix,
                loss_probabilities,
            } => {
                // Transition to the next state based on the current state
                let current_index = this.state.to_index();
                let transition_probs = &transition_matrix[current_index];
                let rand_val = this.rng.random::<f64>();
                let mut cumulative = 0.0;
                let mut new_state = current_index;
                for (i, &prob) in transition_probs.iter().enumerate() {
                    cumulative += prob;
                    if rand_val < cumulative {
                        new_state = i;
                        break;
                    }
                }
                *this.state = MultiState::from_index(new_state);

                // Determine packet loss based on the new state's loss
                // probability
                this.rng.random::<f64>() < loss_probabilities[new_state]
            }
        };

        if should_drop {
            // Drop the packet by not reading anything and returning Ok with 0
            // bytes
            if let Some(event) = &*this.event {
                let s: MultiState = *this.state;
                let _ = event.on_applied(FaultEvent::PacketLoss {
                    direction: Direction::Ingress,
                    side: this.side.clone(),
                    state: s.to_string(),
                });
            }
            buf.advance(0);
            Poll::Ready(Ok(()))
        } else {
            // Proceed to read normally
            this.inner.poll_read(cx, buf)
        }
    }
}

/// PacketLossLimitedWrite wraps an AsyncWrite stream and applies packet loss
/// based on the Multi-State Markov Model.
#[derive(Debug)]
#[pin_project]
pub struct PacketLossLimitedWrite<S> {
    #[pin]
    inner: S,
    strategy: PacketLossStrategy,
    state: MultiState,                        // Current state
    transition_matrix: Option<Vec<Vec<f64>>>, // Only for MultiStateMarkov
    loss_probabilities: Option<Vec<f64>>,     // Only for MultiStateMarkov
    event: Option<Box<dyn ProxyTaskEvent>>,
    side: StreamSide,
    rng: SmallRng,
}

impl<S> PacketLossLimitedWrite<S> {
    /// Creates a new PacketLossLimitedWrite.
    ///
    /// # Arguments
    ///
    /// * `inner` - The underlying AsyncWrite stream.
    /// * `options` - The packet loss options.
    /// * `event` - An optional event handler for fault events.
    pub fn new(
        inner: S,
        settings: PacketLossSettings,
        event: Option<Box<dyn ProxyTaskEvent>>,
    ) -> Self {
        let strategy = PacketLossStrategy::default();
        let (transition_matrix, loss_probabilities) = match strategy {
            PacketLossStrategy::MultiStateMarkov {
                ref transition_matrix,
                ref loss_probabilities,
            } => (
                Some(transition_matrix.clone()),
                Some(loss_probabilities.clone()),
            ),
        };

        PacketLossLimitedWrite {
            inner,
            strategy,
            state: MultiState::Good,
            transition_matrix,
            loss_probabilities,
            event,
            side: settings.side.clone(),
            rng: SmallRng::from_os_rng(),
        }
    }
}

impl<S> AsyncWrite for PacketLossLimitedWrite<S>
where
    S: AsyncWrite + Unpin,
{
    fn poll_write(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &[u8],
    ) -> Poll<IoResult<usize>> {
        let this = self.project();
        // Determine if the packet should be dropped based on the current state
        let should_drop = match &this.strategy {
            PacketLossStrategy::MultiStateMarkov {
                transition_matrix,
                loss_probabilities,
            } => {
                // Transition to the next state based on the current state
                let current_index = this.state.to_index();
                let transition_probs = &transition_matrix[current_index];
                let rand_val = this.rng.random::<f64>();
                let mut cumulative = 0.0;
                let mut new_state = current_index;
                for (i, &prob) in transition_probs.iter().enumerate() {
                    cumulative += prob;
                    if rand_val < cumulative {
                        new_state = i;
                        break;
                    }
                }
                *this.state = MultiState::from_index(new_state);

                // Determine packet loss based on the new state's loss
                // probability
                this.rng.random::<f64>() < loss_probabilities[new_state]
            }
        };

        if should_drop {
            // Drop the packet by not writing anything and returning Ok with 0
            // bytes
            if let Some(event) = &*this.event {
                let s: MultiState = *this.state;
                let _ = event.on_applied(FaultEvent::PacketLoss {
                    state: s.to_string(),
                    direction: Direction::Egress,
                    side: this.side.clone(),
                });
            }
            Poll::Ready(Ok(0))
        } else {
            // Proceed to write normally
            this.inner.poll_write(cx, buf)
        }
    }

    fn poll_flush(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<IoResult<()>> {
        let this = self.project();
        this.inner.poll_flush(cx)
    }

    fn poll_shutdown(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<IoResult<()>> {
        let this = self.project();
        this.inner.poll_shutdown(cx)
    }
}

/// PacketLossLimitedBidirectional wraps limited reader and writer with packet
/// loss.
#[derive(Debug)]
#[pin_project]
struct PacketLossLimitedBidirectional<R, W> {
    #[pin]
    reader: R,
    #[pin]
    writer: W,
}

impl<R, W> PacketLossLimitedBidirectional<R, W>
where
    R: AsyncRead + Send + Unpin + std::fmt::Debug,
    W: AsyncWrite + Send + Unpin + std::fmt::Debug,
{
    /// Creates a new PacketLossLimitedBidirectional.
    fn new(reader: R, writer: W) -> Self {
        Self { reader, writer }
    }
}

impl<R, W> AsyncRead for PacketLossLimitedBidirectional<R, W>
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

impl<R, W> AsyncWrite for PacketLossLimitedBidirectional<R, W>
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
        self.project().writer.poll_shutdown(cx)
    }
}

#[derive(Debug, Clone)]
pub struct PacketLossInjector {
    pub settings: PacketLossSettings,
}

impl From<&PacketLossSettings> for PacketLossInjector {
    fn from(settings: &PacketLossSettings) -> Self {
        PacketLossInjector { settings: settings.clone() }
    }
}

impl fmt::Display for PacketLossInjector {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "packet-loss")
    }
}

#[async_trait]
impl FaultInjector for PacketLossInjector {
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

    /// Injects packet loss into a bidirectional stream based on the direction.
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

        let _ = event.with_fault(FaultEvent::PacketLoss {
            state: "".to_owned(),
            direction: direction.clone(),
            side: self.settings.side.clone(),
        });

        // Wrap the read half if ingress or both directions are specified
        let limited_read: Box<dyn BidirectionalReadHalf> =
            if direction.is_ingress() {
                Box::new(PacketLossLimitedRead::new(
                    read_half,
                    self.settings.clone(),
                    Some(event.clone()),
                ))
            } else {
                Box::new(read_half) as Box<dyn BidirectionalReadHalf>
            };

        // Wrap the write half if egress or both directions are specified
        let limited_write: Box<dyn BidirectionalWriteHalf> =
            if direction.is_egress() {
                Box::new(PacketLossLimitedWrite::new(
                    write_half,
                    self.settings.clone(),
                    Some(event.clone()),
                ))
            } else {
                Box::new(write_half) as Box<dyn BidirectionalWriteHalf>
            };

        // Combine the limited read and write into a new bidirectional stream
        let limited_bidirectional =
            PacketLossLimitedBidirectional::new(limited_read, limited_write);

        Ok(Box::new(limited_bidirectional))
    }

    /// Applies packet loss to a request builder.
    async fn apply_on_request_builder(
        &self,
        builder: reqwest::ClientBuilder,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::ClientBuilder, ProxyError> {
        // No modifications needed for the request builder in this fault
        // injector
        Ok(builder)
    }

    /// Applies packet loss to an outgoing request.
    async fn apply_on_request(
        &self,
        request: ReqwestRequest,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<ReqwestRequest, ProxyError> {
        if self.settings.side == StreamSide::Client {
            let _ = event.with_fault(FaultEvent::PacketLoss {
                state: "".to_owned(),
                direction: Direction::Egress,
                side: StreamSide::Client,
            });

            let original_body = request.body();
            if let Some(body) = original_body {
                if let Some(bytes) = body.as_bytes() {
                    let owned_bytes = Cursor::new(bytes.to_vec());

                    // Wrap the owned bytes with PacketLossLimitedRead
                    let packet_loss_limited_read = PacketLossLimitedRead::new(
                        owned_bytes,
                        self.settings.clone(),
                        Some(event.clone()),
                    );

                    // Convert the PacketLossLimitedRead into a ReaderStream
                    let reader_stream =
                        ReaderStream::new(packet_loss_limited_read);

                    // Replace the request body with the limited stream
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

    /// Applies packet loss to an incoming response.
    async fn apply_on_response(
        &self,
        resp: http::Response<Vec<u8>>,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, ProxyError> {
        if self.settings.side == StreamSide::Server {
            let _ = event.with_fault(FaultEvent::PacketLoss {
                state: "".to_owned(),
                direction: Direction::Ingress,
                side: StreamSide::Server,
            });

            // Split the response into parts and body
            let (parts, body) = resp.into_parts();
            let version = parts.version;
            let status = parts.status;
            let headers = parts.headers.clone();

            // Convert the body into an owned Cursor<Vec<u8>>
            let owned_body = Cursor::new(body);

            // Wrap the owned body with PacketLossLimitedRead
            let packet_loss_limited_read = PacketLossLimitedRead::new(
                owned_body,
                self.settings.clone(),
                Some(event.clone()),
            );

            // Convert the PacketLossLimitedRead into a ReaderStream
            let reader_stream = ReaderStream::new(packet_loss_limited_read);

            // Read the limited stream into a buffer
            let mut buffer = BytesMut::new();
            tokio::pin!(reader_stream);
            while let Some(chunk) = reader_stream.next().await {
                buffer.extend_from_slice(&chunk?);
            }
            let response_body = buffer.to_vec();

            // Reconstruct the HTTP response with the limited body
            let mut new_response = http::Response::new(response_body);
            *new_response.version_mut() = version;
            *new_response.status_mut() = status;
            *new_response.headers_mut() = headers;

            return Ok(new_response);
        }

        Ok(resp)
    }
}
