// src/fault/jitter.rs

use std::fmt;
use std::pin::Pin;
use std::task::Context;
use std::task::Poll;

use async_trait::async_trait;
use axum::http;
use pin_project::pin_project;
use rand::Rng;
use rand::SeedableRng;
use rand::rngs::SmallRng;
use tokio::io::AsyncRead;
use tokio::io::AsyncWrite;
use tokio::io::ReadBuf;
use tokio::time::Duration;
use tokio::time::Sleep;
use tokio::time::sleep;

use super::Bidirectional;
use super::FaultInjector;
use crate::config::JitterSettings;
use crate::event::ProxyTaskEvent;
use crate::types::Direction;
use crate::types::StreamSide;

/// Jitter Injector that introduces variable delays based on amplitude and
/// frequency.
#[derive(Debug)]
pub struct JitterInjector {
    settings: JitterSettings,
}

impl fmt::Display for JitterInjector {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "jitter")
    }
}

impl JitterInjector {
    /// Determines whether to inject jitter based on the configured frequency.
    fn should_jitter(&self, rng: &mut SmallRng) -> bool {
        rng.r#gen::<f64>() < self.settings.jitter_frequency
    }

    /// Generates a random jitter duration based on the configured amplitude.
    fn generate_jitter(&self, rng: &mut SmallRng) -> Duration {
        let millis = rng.gen_range(0.0..=self.settings.jitter_amplitude);
        Duration::from_millis(millis as u64)
    }
}

impl From<&JitterSettings> for JitterInjector {
    fn from(settings: &JitterSettings) -> Self {
        JitterInjector { settings: settings.clone() }
    }
}

impl Clone for JitterInjector {
    fn clone(&self) -> Self {
        Self { settings: self.settings.clone() }
    }
}

#[async_trait]
impl FaultInjector for JitterInjector {
    /// Injects jitter into a bidirectional stream.
    fn inject(
        &self,
        stream: Box<dyn Bidirectional + 'static>,
        _event: Box<dyn ProxyTaskEvent>,
        _side: StreamSide,
    ) -> Box<dyn Bidirectional + 'static> {
        let direction = self.settings.direction.clone();
        Box::new(JitterStream::new(stream, self.clone(), &direction))
    }

    async fn apply_on_response(
        &self,
        resp: http::Response<Vec<u8>>,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, crate::errors::ProxyError> {
        Ok(resp)
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
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::Request, crate::errors::ProxyError> {
        Ok(request)
    }
}

/// A wrapper around a bidirectional stream that injects jitter.
#[derive(Debug)]
#[pin_project]
pub struct JitterStream {
    #[pin]
    stream: Box<dyn Bidirectional + 'static>,
    #[pin]
    injector: JitterInjector,
    #[pin]
    rng: SmallRng,
    #[pin]
    read_sleep: Option<Pin<Box<Sleep>>>,
    #[pin]
    write_sleep: Option<Pin<Box<Sleep>>>,
    #[pin]
    direction: Direction,
}

impl JitterStream {
    /// Creates a new JitterStream.
    fn new(
        stream: Box<dyn Bidirectional + 'static>,
        injector: JitterInjector,
        direction: &Direction,
    ) -> Self {
        Self {
            stream,
            injector,
            rng: SmallRng::from_entropy(),
            read_sleep: None,
            write_sleep: None,
            direction: direction.clone(),
        }
    }
}

impl AsyncRead for JitterStream {
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<std::io::Result<()>> {
        let mut this = self.project();

        if this.direction.is_ingress() {
            if let Some(sleep_fut) = this.read_sleep.as_mut().as_pin_mut() {
                match sleep_fut.poll(cx) {
                    Poll::Ready(_) => {
                        this.read_sleep.set(None);
                    }
                    Poll::Pending => {
                        return Poll::Pending;
                    }
                }
            } else {
                let injector = this.injector;
                let mut rng = this.rng;
                if injector.should_jitter(&mut rng) {
                    let jitter_duration = injector.generate_jitter(&mut rng);
                    this.read_sleep.set(Some(Box::pin(sleep(jitter_duration))));
                }
            }
        }

        Pin::new(&mut **this.stream).poll_read(cx, buf)
    }
}

impl AsyncWrite for JitterStream {
    fn poll_write(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &[u8],
    ) -> Poll<std::io::Result<usize>> {
        let mut this = self.project();

        if this.direction.is_egress() {
            if let Some(sleep_fut) = this.write_sleep.as_mut().as_pin_mut() {
                match sleep_fut.poll(cx) {
                    Poll::Ready(_) => {
                        this.write_sleep.set(None);
                    }
                    Poll::Pending => {
                        return Poll::Pending;
                    }
                }
            } else {
                let injector = this.injector;
                let mut rng = this.rng;
                if injector.should_jitter(&mut rng) {
                    let jitter_duration = injector.generate_jitter(&mut rng);
                    this.write_sleep
                        .set(Some(Box::pin(sleep(jitter_duration))));
                }
            }
        }

        Pin::new(&mut **this.stream).poll_write(cx, buf)
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
