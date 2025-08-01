use std::error::Error;
use std::fmt;
use std::sync::Arc;

use anyhow::Result;
use async_trait::async_trait;
use axum::http;
use http::HeaderMap;
use http::StatusCode;
use tokio::sync::RwLock;
use tonic::Request;
use tonic::transport::Channel;

use crate::config::FaultKind;
use crate::config::GrpcCapabilities;
use crate::config::GrpcSettings;
use crate::errors::ProxyError;
use crate::event::ProxyTaskEvent;
use crate::fault::Bidirectional;
use crate::fault::BoxChunkStream;
use crate::fault::grpc::GrpcInjector;
use crate::plugin::FaultInjector;
use crate::types::Direction;
use crate::types::ProtocolType;
use crate::types::StreamSide;

// Include the generated protobuf code.
pub mod service {
    tonic::include_proto!("plugin");
}

use service::plugin_service_client::PluginServiceClient;

#[derive(Debug, Clone)]
pub struct RemotePluginMeta {
    pub name: String,
    pub version: String,
    pub author: Option<String>,
    pub url: Option<String>,
    pub platform: Option<String>,
    pub direction: Option<Direction>,
}

// Struct to hold plugin metadata and client
#[derive(Debug, Clone)]
pub struct RemotePlugin {
    pub addr: String,
    pub meta: Option<RemotePluginMeta>,
    pub client: PluginServiceClient<Channel>,
    pub injector: GrpcInjector,
}

impl fmt::Display for RemotePlugin {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self.meta.clone() {
            Some(meta) => {
                write!(
                    f,
                    "gRPC Plugin:\n\
                    ---------------------\n\
                    Plugin Name          : {}\n\
                    Plugin Version        : {}\n\
                    Plugin Author     : {}\n\
                    Plugin Url      : {}\n\
                    Plugin Platform: {}\n\
                    Plugin Direction: {}",
                    meta.name,
                    meta.version,
                    meta.author.clone().unwrap_or("".to_string()),
                    meta.url.clone().unwrap_or("".to_string()),
                    meta.platform.clone().unwrap_or("".to_string()),
                    meta.direction.unwrap_or(Direction::Both),
                )
            }
            None => write!(f, "gRPC Plugin not loaded yet"),
        }
    }
}

#[derive(Debug, Default, Clone)]
pub struct RpcPluginManager {
    pub enabled: bool,
    pub plugins: Arc<RwLock<Vec<RemotePlugin>>>,
}

impl fmt::Display for RpcPluginManager {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "gRPC manager Plugin")
    }
}

impl PluginServiceClient<tonic::transport::Channel> {
    pub fn connect_lazy<D>(dst: D) -> Result<Self, tonic::transport::Error>
    where
        D: TryInto<tonic::transport::Endpoint>,
        D::Error: Into<Box<dyn Error + Send + Sync + 'static>>,
    {
        let conn = tonic::transport::Endpoint::new(dst)?.connect_lazy();
        Ok(Self::new(conn))
    }
}

impl RpcPluginManager {
    /// Creates a new RpcPluginManager.
    pub fn new() -> Self {
        Self { enabled: true, plugins: Arc::new(RwLock::new(Vec::new())) }
    }

    /// Adds a new gRPC server address to the manager.
    ///
    /// # Arguments
    ///
    /// * `addr` - The address of the gRPC server (e.g., "http://127.0.0.1:50051").
    ///
    /// # Returns
    ///
    /// * `Ok(())` if the plugin was successfully added.
    /// * `Err(ProxyError)` if there was an error connecting or fetching
    ///   metadata.
    #[tracing::instrument]
    pub async fn with_plugin(
        &self,
        addr: String,
    ) -> Result<RemotePlugin, ProxyError> {
        tracing::debug!("Connecting to gRPC plugins on {}", addr);

        // Establish a connection to the gRPC server
        let mut client = PluginServiceClient::connect_lazy(addr.clone())
            .map_err(|e| {
                ProxyError::RpcConnectionError(addr.clone(), e.to_string())
            })?;

        // Fetch plugin metadata
        let request = Request::new(service::GetPluginInfoRequest {});
        let plugin = match client.get_plugin_info(request).await {
            Ok(r) => {
                let info = r.into_inner();

                let capabilities =
                    load_plugin_capabilities(&info.name, client.clone())
                        .await?;

                let side = StreamSide::from_str(match &info.side {
                    0 => "client",
                    1 => "server",
                    2 => "server", // ANY is treated as server
                    _ => "server",
                })
                .unwrap();

                let direction = Direction::from_str(match &info.direction {
                    0 => "ingress",
                    1 => "egress",
                    _ => "both",
                })
                .unwrap();

                let injector = GrpcInjector::new(
                    GrpcSettings {
                        kind: FaultKind::Grpc,
                        enabled: true,
                        direction: direction.clone(),
                        side: side.clone(),
                        name: info.name.clone(),
                        capabilities,
                    },
                    client.clone(),
                );

                let plugin = RemotePlugin {
                    addr,
                    meta: Some(RemotePluginMeta {
                        name: info.name,
                        version: info.version,
                        direction: Some(direction),
                        author: if info.author.is_empty() {
                            None
                        } else {
                            Some(info.author)
                        },
                        url: if info.url.is_empty() {
                            None
                        } else {
                            Some(info.url)
                        },
                        platform: if info.platform.is_empty() {
                            None
                        } else {
                            Some(info.platform)
                        },
                    }),
                    client,
                    injector,
                };

                tracing::info!("Loaded gRPC plugin {}", &plugin);

                plugin
            }
            Err(_) => {
                let injector = GrpcInjector::new(
                    GrpcSettings {
                        kind: FaultKind::Grpc,
                        enabled: false,
                        direction: Direction::Both,
                        side: StreamSide::Client,
                        name: "".to_string(),
                        capabilities: None,
                    },
                    client.clone(),
                );

                tracing::info!(
                    "Registered gRPC plugin '{}' but it looks offline. We'll try to reconnect later",
                    addr
                );

                RemotePlugin { addr, meta: None, client, injector }
            }
        };

        // Add to the plugins list
        let mut plugins = self.plugins.write().await;
        plugins.push(plugin.clone());

        Ok(plugin)
    }

    ///
    /// Supervise existing plugins so that, when they disconnect we disable them
    /// and they connect again, we enable them again as well.
    ///
    /// The underlying gRPC framework doesn't really give us any simple
    /// mechanism to figure the state of the connection, even though it
    /// seems to know about it, so we ping each plugin on its Health check
    /// endpoint. When the call failss, we consider the plugin to be
    /// unavailable. When it succeeds, we flip the state to enabled.
    ///
    /// When the plugin was unavailable at startup point, we couldn't fetch its
    /// metadata so in that case, we also issue a request to the info endpoint
    /// to fetch them and update the plugin in-place.
    ///
    /// This is by no means bullet proof and is mostly to bring a bit of
    /// resilience. But fault itself makes no promise when a plugin is or
    /// isn't available.
    ///
    /// # Arguments
    ///
    /// * `state` - The proxy state containing the plugins manager.
    pub async fn supervise_remote_plugins(&mut self) {
        let mut plugins = self.plugins.write().await;

        for plugin in plugins.iter_mut() {
            let request = service::HealthCheckRequest {};
            match plugin.client.health_check(request).await {
                Ok(r) => {
                    if r.into_inner().healthy {
                        update_plugin_info(plugin).await;
                    } else {
                        plugin.injector.disable();
                    }
                }
                Err(_) => plugin.injector.disable(),
            };
        }
    }
}

#[async_trait]
impl FaultInjector for RpcPluginManager {
    fn is_enabled(&self) -> bool {
        self.enabled
    }

    fn kind(&self) -> FaultKind {
        FaultKind::Grpc
    }

    fn enable(&mut self) {
        self.enabled = true
    }

    fn disable(&mut self) {
        self.enabled = false
    }

    fn clone_box(&self) -> Box<dyn FaultInjector> {
        Box::new(self.clone())
    }

    #[tracing::instrument]
    async fn apply_on_request_builder(
        &self,
        builder: reqwest::ClientBuilder,
        _event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::ClientBuilder, ProxyError> {
        Ok(builder)
    }

    /// Process a single HTTP request through each plugin from the manager.
    ///
    /// # Arguments
    ///
    /// * `req` - The incoming request from the client
    ///
    /// # Returns
    ///
    /// * `Ok(Request)` the updated request
    /// * `Err(ProxyError)` if there was an error
    #[tracing::instrument]
    async fn apply_on_request(
        &self,
        request: reqwest::Request,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<reqwest::Request, ProxyError> {
        let mut new_req = request;

        let lock = self.plugins.read().await;
        for plugin in lock.iter() {
            let injector = plugin.injector.clone();

            if injector.is_enabled() {
                new_req =
                    injector.apply_on_request(new_req, event.clone()).await?;
            }
        }

        Ok(new_req)
    }

    #[tracing::instrument]
    async fn apply_on_response(
        &self,
        resp: http::Response<Vec<u8>>,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Result<http::Response<Vec<u8>>, ProxyError> {
        let mut new_res = resp;

        let lock = self.plugins.read().await;
        for plugin in lock.iter() {
            let injector = plugin.injector.clone();

            if injector.is_enabled() {
                new_res =
                    injector.apply_on_response(new_res, event.clone()).await?;
            }
        }

        Ok(new_res)
    }

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
        let mut modified_stream = stream;

        let lock = self.plugins.read().await;
        for plugin in lock.iter() {
            if plugin.injector.is_enabled() {
                modified_stream = match plugin
                    .injector
                    .inject(modified_stream, event.clone(), side.clone())
                    .await
                {
                    Ok(s) => s,
                    Err((e, s)) => {
                        tracing::warn!("Plugin '{}' failed {}", plugin.addr, e);
                        s
                    }
                }
            }
        }

        Ok(modified_stream)
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

pub async fn load_remote_plugins_as_injectors(
    manager: Arc<RwLock<RpcPluginManager>>,
    addresses: Vec<String>,
) -> Result<(), ProxyError> {
    let manager = manager.write().await;

    for addr in addresses {
        tracing::debug!("Loading gRPC plugin at address: {}", addr);
        let _ = manager.with_plugin(addr.clone()).await;
    }

    Ok(())
}

pub async fn load_plugin_capabilities(
    name: &String,
    mut client: PluginServiceClient<Channel>,
) -> Result<Option<GrpcCapabilities>, ProxyError> {
    let request = Request::new(service::GetPluginCapabilitiesRequest {});
    let caps = client.get_plugin_capabilities(request).await.map_err(|e| {
        ProxyError::RpcCallError(
            name.clone(),
            format!("failed to fetch plugin '{}' capabilities", name),
            e,
        )
    })?;

    let c = caps.into_inner();
    Ok(Some(GrpcCapabilities {
        forward: c.can_handle_http_forward,
        tunnel: c.can_handle_tunnel,
        protocols: c
            .protocols
            .iter()
            .filter_map(ProtocolType::from_i32)
            .collect::<Vec<ProtocolType>>(),
    }))
}

async fn update_plugin_info(plugin: &mut RemotePlugin) {
    let request = Request::new(service::GetPluginInfoRequest {});

    match plugin.client.get_plugin_info(request).await {
        Ok(info_resp) => {
            let info = info_resp.into_inner();

            let capabilities =
                load_plugin_capabilities(&info.name, plugin.client.clone())
                    .await;

            match capabilities {
                Ok(c) => {
                    let side = StreamSide::from_str(match &info.side {
                        0 => "client",
                        1 => "server",
                        2 => "server", // ANY is treated as server
                        _ => "server",
                    })
                    .unwrap();

                    let direction =
                        Direction::from_str(match &info.direction {
                            0 => "ingress",
                            1 => "egress",
                            _ => "both",
                        })
                        .unwrap();

                    plugin.injector.settings.name = info.name.clone();
                    plugin.injector.settings.direction = direction.clone();
                    plugin.injector.settings.side = side.clone();
                    plugin.injector.settings.capabilities = c;

                    plugin.meta = Some(RemotePluginMeta {
                        name: info.name.clone(),
                        version: info.version,
                        direction: Some(direction.clone()),
                        author: if info.author.is_empty() {
                            None
                        } else {
                            Some(info.author)
                        },
                        url: if info.url.is_empty() {
                            None
                        } else {
                            Some(info.url)
                        },
                        platform: if info.platform.is_empty() {
                            None
                        } else {
                            Some(info.platform)
                        },
                    });

                    tracing::info!("Loaded gRPC plugin {}", &plugin);

                    plugin.injector.enable()
                }
                Err(_) => plugin.injector.disable(),
            }
        }
        Err(_) => plugin.injector.disable(),
    };
}
