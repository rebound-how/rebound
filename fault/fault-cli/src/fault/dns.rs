use std::fmt;
use std::net::SocketAddr;
use std::sync::Arc;

use async_trait::async_trait;
use axum::http;
use hickory_resolver::TokioResolver;
use http::HeaderMap;
use http::StatusCode;
use rand::Rng;
use rand::SeedableRng;
use rand::rngs::SmallRng;
use reqwest::Body;
use reqwest::dns::Addrs;
use reqwest::dns::Name;
use reqwest::dns::Resolve;
use reqwest::dns::Resolving;
use tokio::sync::RwLock;

use super::Bidirectional;
use super::FaultInjector;
use crate::config::DnsSettings;
use crate::config::FaultKind;
use crate::errors::ProxyError;
use crate::event::FaultEvent;
use crate::event::ProxyTaskEvent;
use crate::fault::BoxChunkStream;
use crate::types::Direction;
use crate::types::StreamSide;

/// Custom DNS Resolver that simulates DNS failures
#[derive(Clone, Debug)]
pub struct FaultyResolverInjector {
    inner: Arc<RwLock<TokioResolver>>,
    settings: DnsSettings,
    event: Option<Box<dyn ProxyTaskEvent>>,
    side: StreamSide,
    rng: SmallRng,
}

impl fmt::Display for FaultyResolverInjector {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "dns")
    }
}

impl From<&DnsSettings> for FaultyResolverInjector {
    fn from(settings: &DnsSettings) -> Self {
        let resolver = TokioResolver::builder_tokio().unwrap().build();
        FaultyResolverInjector {
            inner: Arc::new(RwLock::new(resolver)),
            settings: settings.clone(),
            event: None,
            side: StreamSide::Client,
            rng: SmallRng::from_os_rng(),
        }
    }
}

impl FaultyResolverInjector {
    fn should_apply_fault_resolver(&mut self) -> bool {
        self.rng.random_bool(self.settings.rate)
    }

    pub fn with_event(&mut self, event: Box<dyn ProxyTaskEvent>) {
        self.event = Some(event);
    }
}

impl Resolve for FaultyResolverInjector {
    fn resolve(&self, hostname: Name) -> Resolving {
        let mut self_clone = self.clone();

        Box::pin(async move {
            let host = hostname.as_str();
            let apply_fault = self_clone.should_apply_fault_resolver();
            tracing::debug!("Apply a dns resolver {}", apply_fault);

            if apply_fault {
                let _ = match self_clone.event {
                    Some(event) => event.with_fault(FaultEvent::Dns {
                        direction: Direction::Egress,
                        side: self_clone.side.clone(),
                        triggered: Some(true),
                    }),
                    None => Ok(()),
                };
                let io_error =
                    std::io::Error::other("Simulated DNS resolution failure");
                return Err(io_error.into());
            }

            let _ = match self_clone.event {
                Some(event) => event.with_fault(FaultEvent::Dns {
                    direction: Direction::Egress,
                    side: self_clone.side.clone(),
                    triggered: Some(false),
                }),
                None => Ok(()),
            };

            let resolver = self_clone.inner.read().await;
            let lookup = resolver.lookup_ip(host).await?;
            let ips = lookup.into_iter().collect::<Vec<_>>();
            let addrs: Addrs =
                Box::new(ips.into_iter().map(|addr| SocketAddr::new(addr, 0)));

            Ok(addrs)
        })
    }
}

#[async_trait]
impl FaultInjector for FaultyResolverInjector {
    /// Injects latency into a bidirectional stream.
    async fn inject(
        &self,
        stream: Box<dyn Bidirectional + 'static>,
        _event: Box<dyn ProxyTaskEvent>,
        _side: StreamSide,
    ) -> Result<
        Box<dyn Bidirectional + 'static>,
        (ProxyError, Box<dyn Bidirectional + 'static>),
    > {
        Ok(stream)
    }

    async fn apply_on_response(
        &self,
        resp: http::Response<Vec<u8>>,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, ProxyError> {
        Ok(resp)
    }

    async fn apply_on_request_builder(
        &self,
        builder: reqwest::ClientBuilder,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::ClientBuilder, ProxyError> {
        let mut cloned = self.clone();
        cloned.with_event(event);

        let resolver: Arc<FaultyResolverInjector> = Arc::new(cloned);
        tracing::debug!("Adding faulty dns resolver on builder");
        let builder = builder.dns_resolver(resolver);
        Ok(builder)
    }

    async fn apply_on_request(
        &self,
        request: reqwest::Request,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::Request, ProxyError> {
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
}
