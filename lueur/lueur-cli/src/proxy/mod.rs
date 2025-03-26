pub mod forward;
#[cfg(all(
    target_os = "linux",
    any(feature = "stealth", feature = "stealth-auto-build")
))]
pub mod stealth;
pub mod tunnel;

use std::net::SocketAddr;
use std::sync::Arc;

use ::oneshot::Sender;
use axum::body::Body;
use axum::http::Request;
use axum::response::IntoResponse;
use hyper::Method;
use hyper::body::Incoming;
use hyper::server::conn::http1;
use hyper_util::rt::TokioIo;
use tokio::sync::RwLock;
use tokio::sync::broadcast;
use tokio::sync::watch;
use url::Url;

use crate::config::FaultConfig;
use crate::config::FaultKind;
use crate::config::ProxyConfig;
use crate::errors::ProxyError;
use crate::event::TaskManager;
use crate::fault;
use crate::fault::FaultInjector;
use crate::plugin::CompositePlugin;
use crate::plugin::load_injector;
use crate::plugin::load_injectors;
use crate::resolver::map_localhost_to_nic;
use crate::types::FaultConfiguration;

/// Shared application state
#[derive(Debug, Clone)]
pub struct ProxyState {
    pub plugins: Arc<RwLock<CompositePlugin>>,
    pub shared_config: Arc<RwLock<ProxyConfig>>,
    pub upstream_hosts: Arc<RwLock<Vec<String>>>,
    pub stealth: bool,
}

impl ProxyState {
    pub fn new(stealth: bool) -> Self {
        Self {
            plugins: Arc::new(RwLock::new(CompositePlugin::empty())),
            shared_config: Arc::new(RwLock::new(ProxyConfig::default())),
            upstream_hosts: Arc::new(RwLock::new(Vec::new())),
            stealth,
        }
    }

    /// Update the faults
    pub async fn set_faults(&self, new_faults: Vec<Box<dyn FaultInjector>>) {
        let mut plugins = self.plugins.write().await;
        plugins.set_injectors(new_faults);
    }

    /// Update the shared configuration.
    pub async fn update_config(&self, new_config: ProxyConfig) {
        tracing::debug!("Applying proxy configuration: {:?}", new_config);
        let mut config = self.shared_config.write().await;
        *config = new_config;
    }

    /// Update the upstream hosts.
    pub async fn update_upstream_hosts(&self, new_hosts: Vec<String>) {
        tracing::debug!("Allowed hosts {:?}", new_hosts);
        let mut hosts = self.upstream_hosts.write().await;
        *hosts = new_hosts;
    }

    pub async fn set_fault(&self, fault: FaultConfiguration) {
        tracing::debug!("Setting fault on config: {:?}", fault);
        let mut config = self.shared_config.write().await;

        let fault_config = fault.build().unwrap();
        let kind = fault_config.kind();

        if let Some(existing) = config.find_mut_by_kind(kind) {
            *existing = fault_config;
        } else {
            config.faults.push(fault_config);
        }
    }

    pub async fn enable_fault(
        &self,
        fault_type: FaultKind,
        fault_config: FaultConfig,
    ) {
        tracing::debug!("Enabling fault {:?}", fault_type);
        let mut config = self.shared_config.write().await;
        let mut plugins = self.plugins.write().await;

        if let Some(existing) = config.find_mut_by_kind(fault_type) {
            existing.enable();
            plugins.enable_injector(fault_type);
        } else {
            let injector = load_injector(&fault_config);
            plugins.add_injector(injector);
            config.add_fault(fault_config);
        }
    }

    pub async fn disable_fault(
        &self,
        fault_type: FaultKind,
        fault_config: FaultConfig,
    ) {
        tracing::debug!("Disabling fault {:?}", fault_type);
        let mut config = self.shared_config.write().await;
        let mut plugins = self.plugins.write().await;

        if let Some(existing) = config.find_mut_by_kind(fault_type) {
            existing.disable();
            plugins.disable_injector(fault_type);
        }
    }
}

#[tracing::instrument]
async fn handle_new_connection(
    req: Request<Body>,
    state: Arc<ProxyState>,
    task_manager: Arc<TaskManager>,
) -> Result<hyper::Response<Body>, ProxyError> {
    let req = req.map(Body::new);

    let state = state.clone();
    let method = req.method().clone();
    let scheme = req.uri().scheme_str().unwrap_or("http").to_string();
    let authority: Option<String> =
        req.uri().authority().map(|a| a.as_str().to_string());
    let host_header = req
        .headers()
        .get(axum::http::header::HOST)
        .and_then(|v| v.to_str().ok().map(|s| s.to_string()));

    let path = match req.uri().path_and_query() {
        Some(path) => path.to_string(),
        None => "/".to_string(),
    };

    let upstream = match determine_upstream(
        scheme,
        authority,
        host_header,
        path,
        state.stealth,
    )
    .await
    {
        Ok(url) => url,
        Err(e) => {
            tracing::error!("Failed to determine upstream: {}", e);
            return Err(e);
        }
    };

    let mut passthrough = true;

    let hosts = state.upstream_hosts.read().await;
    let upstream_host = get_host(&upstream);
    if hosts.contains(&String::from("*")) {
        tracing::debug!("All upstreams are allowed");
        passthrough = false;
    } else if hosts.contains(&upstream_host) {
        tracing::debug!("Upstream host in allowed list");
        passthrough = false;
    } else {
        tracing::debug!("Upstream host {} NOT in allowed list", upstream_host);
    }

    let upstream_url: Url = upstream.parse().unwrap();
    let event;

    if !passthrough {
        event = task_manager
            .new_fault_event(upstream_url.to_string())
            .await
            .unwrap();
    } else {
        event = task_manager
            .new_passthrough_event(upstream_url.to_string())
            .await
            .unwrap();
    }

    tracing::debug!("Upstream {}", upstream_url);

    if method == Method::CONNECT {
        tracing::debug!("Processing tunnel request to {}", upstream_url);
        let r = tunnel::handle_connect(
            req,
            state.clone(),
            upstream_url,
            passthrough,
            event.clone(),
        )
        .await;

        let resp = match r {
            Ok(r) => r,
            Err(e) => e.into_response(),
        };
        Ok(resp)
    } else {
        tracing::debug!("Processing forward request to {}", upstream_url);
        let r = forward::handle_request(
            req,
            state.clone(),
            upstream_url,
            passthrough,
            event.clone(),
        )
        .await;

        let resp = match r {
            Ok(r) => r,
            Err(e) => e.into_response(),
        };
        Ok(resp)
    }
}

pub async fn run_proxy(
    proxy_address: String,
    state: Arc<ProxyState>,
    mut shutdown_rx: broadcast::Receiver<()>,
    readiness_tx: Sender<()>,
    mut config_rx: watch::Receiver<ProxyConfig>,
    task_manager: Arc<TaskManager>,
) -> Result<(), ProxyError> {
    let addr: SocketAddr = proxy_address.parse().map_err(|e| {
        ProxyError::Internal(format!(
            "Failed to parse proxy address {}: {}",
            proxy_address, e
        ))
    })?;

    let state_cloned = state.clone();
    let state = state_cloned.clone();
    let config_change_handle = tokio::spawn(async move {
        let state = state.clone();

        loop {
            match config_rx.changed().await {
                Ok(_) => {
                    let new_config = config_rx.borrow_and_update().clone();
                    let faults = load_injectors(&new_config);
                    state.update_config(new_config).await;
                    state.set_faults(faults).await;
                }
                Err(e) => {
                    tracing::debug!("Exited proxy config loop: {}", e);
                    break;
                }
            };
        }
    });

    let proxy_listener =
        tokio::net::TcpListener::bind(addr).await.map_err(|e| {
            ProxyError::IoError(std::io::Error::new(
                e.kind(),
                format!("Failed to bind to address {}: {}", addr, e),
            ))
        })?;

    let _ = readiness_tx.send(()).map_err(|e| {
        ProxyError::Internal(format!("Failed to send readiness signal: {}", e))
    });

    loop {
        tokio::select! {
            _ = shutdown_rx.recv() => {
                tracing::info!("Shutdown signal received. Stopping listener.");
                config_change_handle.abort();
                break;
            },
            accept_result = proxy_listener.accept() => {
                match accept_result {
                    Ok((stream, addr)) => {
                        tracing::debug!("Accepted connection from {}", addr);

                        let io = TokioIo::new(stream);
                        let state = state_cloned.clone();
                        let task_manager = task_manager.clone();

                        let hyper_service =
                        hyper::service::service_fn(move |request: Request<Incoming>| {
                            handle_new_connection(
                                request.map(Body::new),
                                state.clone(),
                                task_manager.clone()
                            )
                        });

                        tokio::task::spawn(async move {
                            if let Err(err) = http1::Builder::new()
                                .preserve_header_case(true)
                                .title_case_headers(true)
                                .serve_connection(io, hyper_service)
                                .with_upgrades()
                                .await
                            {
                                tracing::error!("Failed to serve connection: {:?}", err);
                            }
                        });
                    }
                    Err(e) => {
                        tracing::error!("Failed to accept connection: {}", e);
                        continue;
                    }
                }
            }
        }
    }

    tracing::debug!("Proxy is now finised, bye bye");

    Ok(())
}

#[cfg(all(
    target_os = "linux",
    any(feature = "stealth", feature = "stealth-auto-build")
))]
pub async fn run_ebpf_proxy(
    ebpf_proxy_address: String,
    state: Arc<ProxyState>,
    mut shutdown_rx: broadcast::Receiver<()>,
    readiness_tx: Sender<()>,
    mut config_rx: watch::Receiver<ProxyConfig>,
    task_manager: Arc<TaskManager>,
) -> Result<(), ProxyError> {
    let addr: SocketAddr = ebpf_proxy_address.parse().map_err(|e| {
        ProxyError::Internal(format!(
            "Failed to parse eBpf proxy address {}: {}",
            ebpf_proxy_address, e
        ))
    })?;

    let state_cloned = state.clone();
    let state = state_cloned.clone();
    let config_change_handle = tokio::spawn(async move {
        let state = state.clone();

        loop {
            match config_rx.changed().await {
                Ok(_) => {
                    let new_config = config_rx.borrow_and_update().clone();
                    let faults = load_injectors(&new_config);
                    state.update_config(new_config).await;
                    state.set_faults(faults).await;
                }
                Err(e) => {
                    tracing::debug!("Exited proxy config loop: {}", e);
                    break;
                }
            };
        }
    });

    let proxy_listener =
        tokio::net::TcpListener::bind(addr).await.map_err(|e| {
            ProxyError::IoError(std::io::Error::new(
                e.kind(),
                format!("Failed to bind ebpf proxy to address {}: {}", addr, e),
            ))
        })?;

    let _ = readiness_tx.send(()).map_err(|e| {
        ProxyError::Internal(format!("Failed to send readiness signal: {}", e))
    });

    tracing::debug!("Listening for incoming request via eBPF redirection");

    loop {
        tokio::select! {
            _ = shutdown_rx.recv() => {
                tracing::info!("Shutdown signal received. Stopping listener.");
                config_change_handle.abort();
                break;
            },
            accept_result = proxy_listener.accept() => {
                match accept_result {
                    Ok((stream, addr)) => {
                        tracing::debug!("Accepted connection from {}", addr);

                        let event = task_manager
                            .new_fault_event("".to_string())
                            .await
                            .unwrap();

                        let _ = stealth::handle_stream(
                            stream,
                            state_cloned.clone(),
                            false,
                            event
                        ).await;
                    }
                    Err(e) => {
                        tracing::error!("Failed to accept connection: {}", e);
                        continue;
                    }
                }
            }
        }
    }

    tracing::debug!("ebpf proxy is now finished, bye bye");

    Ok(())
}

///
/// -------------------- Private functions -----------------------------------

async fn determine_upstream(
    scheme: String,
    authority: Option<String>,
    host_header: Option<String>,
    path: String,
    stealth: bool,
) -> Result<String, ProxyError> {
    let upstream = if let Some(auth) = authority {
        let mut scheme = scheme;

        if let Some((_, port_str)) = auth.split_once(':') {
            scheme = match port_str {
                "443" => "https".to_string(),
                _ => "http".to_string(),
            };
        };

        format!("{}://{}{}", scheme, auth, path)
    } else if let Some(host_str) = host_header {
        let mut scheme = scheme;
        if let Some((_, port_str)) = host_str.split_once(':') {
            scheme = match port_str {
                "443" => "https".to_string(),
                _ => "http".to_string(),
            };
        };

        let (mut host, port) =
            parse_domain_with_scheme(scheme.as_str(), &host_str);
        if stealth && host.as_str() == "localhost" {
            host = map_localhost_to_nic()
        }
        format!("{}://{}:{}{}", scheme, host, port, path)
    } else {
        return Err(ProxyError::InvalidRequest(
            "Unable to determine upstream target".into(),
        ));
    };

    Ok(upstream)
}

fn parse_domain_with_scheme(scheme: &str, domain: &str) -> (String, String) {
    let default_port = match scheme {
        "https" => "443",
        _ => "80",
    };

    if let Some((host, port_str)) = domain.split_once(':') {
        let port = if port_str.is_empty() { default_port } else { port_str };
        (host.to_string(), port.to_string())
    } else {
        (domain.to_string(), default_port.to_string())
    }
}

fn get_host(upstream_url: &str) -> String {
    let url = Url::parse(upstream_url).unwrap();
    let host = url.host_str().ok_or("Missing host").unwrap().to_string();
    let port = url.port_or_known_default().unwrap();
    format!("{}:{}", host, port)
}
