use std::fmt::Debug;
use std::future::Future;
use std::marker::Unpin;
use std::pin::Pin;
use std::task::Context;
use std::task::Poll;

use async_trait::async_trait;
use axum::http;
use pin_project::pin_project;
use reqwest::ClientBuilder as ReqwestClientBuilder;
use reqwest::Request as ReqwestRequest;
use tokio::io::AsyncRead as TokioAsyncRead;
use tokio::io::AsyncWrite as TokioAsyncWrite;
use tokio_rustls::client::TlsStream;

pub mod bandwidth;
pub mod blackhole;
pub mod dns;
pub mod grpc;
pub mod http_error;
pub mod jitter;
pub mod latency;
pub mod packet_loss;

use crate::config::FaultKind;
use crate::errors::ProxyError;
use crate::event::ProxyTaskEvent;
use crate::types::StreamSide;

/// A composite trait that combines AsyncRead, AsyncWrite, Unpin, and Send.
pub trait Bidirectional:
    TokioAsyncRead + TokioAsyncWrite + Unpin + Send + std::fmt::Debug
{
}

impl<T> Bidirectional for T where
    T: TokioAsyncRead + TokioAsyncWrite + Unpin + Send + std::fmt::Debug
{
}

pub trait BidirectionalReadHalf:
    TokioAsyncRead + Unpin + Send + std::fmt::Debug
{
}

impl<T> BidirectionalReadHalf for T where
    T: TokioAsyncRead + Unpin + Send + std::fmt::Debug
{
}

pub trait BidirectionalWriteHalf:
    TokioAsyncWrite + Unpin + Send + std::fmt::Debug
{
}

impl<T> BidirectionalWriteHalf for T where
    T: TokioAsyncWrite + Unpin + Send + std::fmt::Debug
{
}

#[derive(Debug)]
#[pin_project]
pub struct TlsBidirectional {
    #[pin]
    pub inner: TlsStream<Box<dyn Bidirectional + 'static>>,
}

impl tokio::io::AsyncRead for TlsBidirectional {
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut std::task::Context<'_>,
        buf: &mut tokio::io::ReadBuf<'_>,
    ) -> std::task::Poll<std::io::Result<()>> {
        Pin::new(&mut self.get_mut().inner).poll_read(cx, buf)
    }
}

impl tokio::io::AsyncWrite for TlsBidirectional {
    fn poll_write(
        self: Pin<&mut Self>,
        cx: &mut std::task::Context<'_>,
        buf: &[u8],
    ) -> std::task::Poll<std::io::Result<usize>> {
        Pin::new(&mut self.get_mut().inner).poll_write(cx, buf)
    }

    fn poll_flush(
        self: Pin<&mut Self>,
        cx: &mut std::task::Context<'_>,
    ) -> std::task::Poll<std::io::Result<()>> {
        Pin::new(&mut self.get_mut().inner).poll_flush(cx)
    }

    fn poll_shutdown(
        self: Pin<&mut Self>,
        cx: &mut std::task::Context<'_>,
    ) -> std::task::Poll<std::io::Result<()>> {
        Pin::new(&mut self.get_mut().inner).poll_shutdown(cx)
    }
}

#[async_trait]
pub trait FaultInjector:
    Send + Sync + std::fmt::Debug + std::fmt::Display
{
    async fn inject(
        &self,
        stream: Box<dyn Bidirectional + 'static>,
        _event: Box<dyn ProxyTaskEvent>,
        _side: StreamSide,
    ) -> Result<
        Box<dyn Bidirectional + 'static>,
        (ProxyError, Box<dyn Bidirectional + 'static>),
    >;

    async fn apply_on_request_builder(
        &self,
        builder: ReqwestClientBuilder,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<ReqwestClientBuilder, ProxyError>;

    async fn apply_on_request(
        &self,
        request: ReqwestRequest,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<ReqwestRequest, ProxyError>;

    async fn apply_on_response(
        &self,
        resp: http::Response<Vec<u8>>,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, ProxyError>;

    fn is_enabled(&self) -> bool;
    fn kind(&self) -> FaultKind;

    fn enable(&mut self);
    fn disable(&mut self);

    fn clone_box(&self) -> Box<dyn FaultInjector>;
}

impl Clone for Box<dyn FaultInjector> {
    fn clone(&self) -> Box<dyn FaultInjector> {
        self.clone_box()
    }
}

pub trait FutureDelay: Future<Output = ()> + Send + Debug {}

pub struct DelayWrapper<F> {
    future: F,
}

impl<F> DelayWrapper<F> {
    pub fn new(future: F) -> Self {
        Self { future }
    }
}

impl<F> std::fmt::Debug for DelayWrapper<F> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "DelayWrapper(...)")
    }
}

impl<F> Future for DelayWrapper<F>
where
    F: Future<Output = ()> + Send,
{
    type Output = ();

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        let inner = unsafe { self.map_unchecked_mut(|s| &mut s.future) };
        Future::poll(inner, cx)
    }
}

impl<F> FutureDelay for DelayWrapper<F> where F: Future<Output = ()> + Send {}
