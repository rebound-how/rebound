use std::fmt;
use std::sync::Arc;
use std::sync::Mutex;

use async_trait::async_trait;
use axum::http;
use metrics::MetricsInjector;
use reqwest::ClientBuilder;
use reqwest::Request as ReqwestRequest;
use serde::Deserialize;
use serde::Serialize;

use crate::config::FaultConfig;
use crate::config::FaultKind;
use crate::config::ProxyConfig;
use crate::errors::ProxyError;
use crate::event::ProxyTaskEvent;
use crate::fault::Bidirectional;
use crate::fault::FaultInjector;
use crate::fault::bandwidth::BandwidthLimitFaultInjector;
use crate::fault::blackhole::BlackholeInjector;
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
    injectors: Vec<Box<dyn FaultInjector>>,
}

impl CompositePlugin {
    /// Adds new FaultInjectors to the CompositePlugin after clearing the
    /// existing set
    pub fn set_injectors(&mut self, injectors: Vec<Box<dyn FaultInjector>>) {
        self.injectors.clear();
        for inj in injectors {
            self.injectors.push(inj);
        }
        self.injectors.push(Box::new(MetricsInjector::new()));
    }

    pub fn add_injector(&mut self, injector: Box<dyn FaultInjector>) {
        self.injectors.insert(self.injectors.len() - 1, injector);
    }

    pub fn disable_injector(&mut self, kind: FaultKind) {
        for injector in self.injectors.iter_mut() {
            if injector.kind() == kind {
                injector.disable();
                break;
            }
        }
    }

    pub fn enable_injector(&mut self, kind: FaultKind) {
        for injector in self.injectors.iter_mut() {
            if injector.kind() == kind {
                injector.enable();
                break;
            }
        }
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
pub fn load_injectors(config: &ProxyConfig) -> Vec<Box<dyn FaultInjector>> {
    let mut injectors: Vec<Box<dyn FaultInjector>> = Vec::new();
    let _: Vec<()> = config
        .faults
        .iter()
        .map(|fault| match fault {
            FaultConfig::Dns(settings) => {
                injectors.push(Box::new(FaultyResolverInjector::from(settings)))
            }
            FaultConfig::Latency(settings) => {
                injectors.push(Box::new(LatencyInjector::from(settings)))
            }
            FaultConfig::PacketLoss(settings) => {
                injectors.push(Box::new(PacketLossInjector::from(settings)))
            }
            FaultConfig::Bandwidth(settings) => injectors
                .push(Box::new(BandwidthLimitFaultInjector::from(settings))),
            FaultConfig::Jitter(settings) => {
                injectors.push(Box::new(JitterInjector::from(settings)))
            }
            FaultConfig::PacketDuplication(settings) => {}
            FaultConfig::HttpError(settings) => injectors
                .push(Box::new(HttpResponseFaultInjector::from(settings))),
            FaultConfig::Blackhole(settings) => {
                injectors.push(Box::new(BlackholeInjector::from(settings)))
            }
        })
        .collect();

    injectors
}

#[tracing::instrument]
pub fn load_injector(fault: &FaultConfig) -> Box<dyn FaultInjector> {
    match fault {
        FaultConfig::Dns(settings) => {
            Box::new(FaultyResolverInjector::from(settings))
        }
        FaultConfig::Latency(settings) => {
            Box::new(LatencyInjector::from(settings))
        }
        FaultConfig::PacketLoss(settings) => {
            Box::new(PacketLossInjector::from(settings))
        }
        FaultConfig::Bandwidth(settings) => {
            Box::new(BandwidthLimitFaultInjector::from(settings))
        }
        FaultConfig::Jitter(settings) => {
            Box::new(JitterInjector::from(settings))
        }
        FaultConfig::PacketDuplication(settings) => todo!(),
        FaultConfig::HttpError(settings) => {
            Box::new(HttpResponseFaultInjector::from(settings))
        }
        FaultConfig::Blackhole(settings) => {
            Box::new(BlackholeInjector::from(settings))
        }
    }
}

#[async_trait]
impl ProxyPlugin for CompositePlugin {
    #[tracing::instrument]
    async fn prepare_client(
        &self,
        builder: ClientBuilder,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<ClientBuilder, ProxyError> {
        let mut current_builder = builder;
        for injector in &self.injectors {
            if injector.is_enabled() {
                current_builder = injector
                    .apply_on_request_builder(current_builder, event.clone())
                    .await?;
            }
        }
        Ok(current_builder)
    }

    #[tracing::instrument]
    async fn process_request(
        &self,
        req: ReqwestRequest,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<ReqwestRequest, ProxyError> {
        let mut current_req = req;
        for injector in &self.injectors {
            if injector.is_enabled() {
                current_req = injector
                    .apply_on_request(current_req, event.clone())
                    .await?;
            }
        }
        Ok(current_req)
    }

    #[tracing::instrument]
    async fn process_response(
        &self,
        resp: http::Response<Vec<u8>>,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, ProxyError> {
        let mut current_resp = resp;
        for injector in &self.injectors {
            if injector.is_enabled() {
                current_resp = injector
                    .apply_on_response(current_resp, event.clone())
                    .await?;
            }
        }
        Ok(current_resp)
    }

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
            if injector.is_enabled() {
                let mut client = modified_client_stream;
                let mut server = modified_server_stream;

                client =
                    injector.inject(client, event.clone(), StreamSide::Client);
                server =
                    injector.inject(server, event.clone(), StreamSide::Server);

                modified_client_stream = client;
                modified_server_stream = server;
            }
        }

        Ok((modified_client_stream, modified_server_stream))
    }
}
