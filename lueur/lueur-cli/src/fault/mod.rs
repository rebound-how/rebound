

use std::pin::Pin;
use std::task::{Context, Poll};
use std::future::Future;
use std::fmt::Debug;
use std::marker::Unpin;


use async_trait::async_trait;
use axum::http;
use reqwest::ClientBuilder as ReqwestClientBuilder;
use reqwest::Request as ReqwestRequest;
use tokio::io::AsyncRead as TokioAsyncRead;
use tokio::io::AsyncWrite as TokioAsyncWrite;

pub mod bandwidth;
pub mod dns;
pub mod http_error;
pub mod jitter;
pub mod latency;
pub mod packet_loss;

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

#[async_trait]
pub trait FaultInjector: Send + Sync + std::fmt::Debug + std::fmt::Display {
    fn inject(
        &self,
        stream: Box<dyn Bidirectional + 'static>,
        _event: Box<dyn ProxyTaskEvent>,
        _side: StreamSide,
    ) -> Box<dyn Bidirectional + 'static>;

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
}

pub trait FutureDelay:
    Future<Output = ()> + Send + Debug
{
}

// Wrapper struct for any future implementing `Future<Output = ()>`

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
        // Just output something generic
        write!(f, "DelayWrapper(...)")
    }
}


// Implement `Future` for the wrapper
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

// Implement `FutureDelay` for the wrapper
impl<F> FutureDelay for DelayWrapper<F>
where
    F: Future<Output = ()> + Send,
{
}
