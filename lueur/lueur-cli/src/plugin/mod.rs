use std::fmt;
use std::sync::Arc;

use axum::async_trait;
use axum::http;
use metrics::MetricsInjector;
use reqwest::ClientBuilder;
use reqwest::Request as ReqwestRequest;
use serde::Deserialize;
use serde::Serialize;

use crate::config::FaultConfig;
use crate::config::ProxyConfig;
use crate::errors::ProxyError;
use crate::event::ProxyTaskEvent;
use crate::fault::Bidirectional;
use crate::fault::FaultInjector;
use crate::fault::bandwidth::BandwidthLimitFaultInjector;
use crate::fault::dns::FaultyResolverInjector;
use crate::fault::http_error::HttpResponseFaultInjector;
use crate::fault::jitter::JitterInjector;
use crate::fault::latency::LatencyInjector;
use crate::fault::packet_loss::PacketLossInjector;
use crate::types::StreamSide;

pub(crate) mod metrics;
pub(crate) mod rpc;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RemotePluginInfo {
    name: String,
    version: String,
    author: String,
    url: String,
}

#[async_trait]
pub trait ProxyPlugin: Send + Sync + std::fmt::Debug + fmt::Display {
    /// Adjust the client builder for forward request proxying
    async fn prepare_client(
        &self,
        builder: ClientBuilder,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<ClientBuilder, ProxyError>;

    /// Processes and potentially modifies an outgoing Reqwest HTTP request.
    async fn process_request(
        &self,
        req: ReqwestRequest,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<ReqwestRequest, ProxyError>;

    /// Processes and potentially modifies an incoming Reqwest HTTP response.
    async fn process_response(
        &self,
        resp: http::Response<Vec<u8>>,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, ProxyError>;

    async fn inject_tunnel_faults(
        &self,
        client_stream: Box<dyn Bidirectional + 'static>,
        server_stream: Box<dyn Bidirectional + 'static>,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<
        (Box<dyn Bidirectional + 'static>, Box<dyn Bidirectional + 'static>),
        ProxyError,
    >;
}

/// CompositePlugin that aggregates multiple FaultInjectors.
#[derive(Debug)]
pub struct CompositePlugin {
    injectors: Vec<Arc<dyn FaultInjector>>,
}

impl CompositePlugin {
    /// Adds new FaultInjectors to the CompositePlugin after clearing the
    /// existing set
    pub fn set_injectors(&mut self, injectors: Vec<Arc<dyn FaultInjector>>) {
        self.injectors.clear();
        self.injectors.extend(injectors);
        self.injectors.push(Arc::new(MetricsInjector::new()));
    }

    /// Creates a new CompositePlugin with no FaultInjectors.
    pub fn empty() -> Self {
        Self { injectors: Vec::new() }
    }
}

impl fmt::Display for CompositePlugin {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Composite Plugin with {} injectors", self.injectors.len())
    }
}

impl From<&ProxyConfig> for CompositePlugin {
    fn from(config: &ProxyConfig) -> Self {
        CompositePlugin { injectors: load_injectors(config) }
    }
}

#[tracing::instrument]
pub fn load_injectors(config: &ProxyConfig) -> Vec<Arc<dyn FaultInjector>> {
    let mut injectors: Vec<Arc<dyn FaultInjector>> = Vec::new();
    let _: Vec<()> = config
        .faults
        .iter()
        .map(|fault| match fault {
            FaultConfig::Dns(settings) => {
                injectors.push(Arc::new(FaultyResolverInjector::from(settings)))
            }
            FaultConfig::Latency(settings) => {
                injectors.push(Arc::new(LatencyInjector::from(settings)))
            }
            FaultConfig::PacketLoss(settings) => {
                injectors.push(Arc::new(PacketLossInjector::from(settings)))
            }
            FaultConfig::Bandwidth(settings) => injectors
                .push(Arc::new(BandwidthLimitFaultInjector::from(settings))),
            FaultConfig::Jitter(settings) => {
                injectors.push(Arc::new(JitterInjector::from(settings)))
            }
            FaultConfig::PacketDuplication(settings) => {}
            FaultConfig::HttpError(settings) => injectors
                .push(Arc::new(HttpResponseFaultInjector::from(settings))),
        })
        .collect();

    injectors
}

#[async_trait]
impl ProxyPlugin for CompositePlugin {
    /// Adjust the client builder by sequentially applying each FaultInjector.
    #[tracing::instrument]
    async fn prepare_client(
        &self,
        builder: ClientBuilder,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<ClientBuilder, ProxyError> {
        let mut current_builder = builder;
        for injector in &self.injectors {
            current_builder = injector
                .apply_on_request_builder(current_builder, event.clone())
                .await?;
        }
        Ok(current_builder)
    }

    /// Process the HTTP request by sequentially applying each FaultInjector.
    #[tracing::instrument]
    async fn process_request(
        &self,
        req: ReqwestRequest,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<ReqwestRequest, ProxyError> {
        let mut current_req = req;
        for injector in &self.injectors {
            current_req =
                injector.apply_on_request(current_req, event.clone()).await?;
        }
        Ok(current_req)
    }

    /// Process the HTTP response by sequentially applying each FaultInjector.
    #[tracing::instrument]
    async fn process_response(
        &self,
        resp: http::Response<Vec<u8>>,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, ProxyError> {
        let mut current_resp = resp;
        for injector in &self.injectors {
            current_resp =
                injector.apply_on_response(current_resp, event.clone()).await?;
        }
        Ok(current_resp)
    }

    /// Inject tunnel faults by sequentially applying each FaultInjector.
    #[tracing::instrument]
    async fn inject_tunnel_faults(
        &self,
        client_stream: Box<dyn Bidirectional + 'static>,
        server_stream: Box<dyn Bidirectional + 'static>,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<
        (Box<dyn Bidirectional + 'static>, Box<dyn Bidirectional + 'static>),
        ProxyError,
    > {
        let mut modified_client_stream = client_stream;
        let mut modified_server_stream = server_stream;

        for injector in &self.injectors {
            tracing::debug!("Injector {}", injector);

            let mut client = modified_client_stream;
            let mut server = modified_server_stream;

            tracing::debug!("Wrapping client stream with {}", injector);
            client = injector.inject(client, event.clone(), StreamSide::Client);

            tracing::debug!("Wrapping server stream with {}", injector);
            server = injector.inject(server, event.clone(),StreamSide::Server);

            modified_client_stream = client;
            modified_server_stream = server;
        }

        Ok((modified_client_stream, modified_server_stream))
    }
}
