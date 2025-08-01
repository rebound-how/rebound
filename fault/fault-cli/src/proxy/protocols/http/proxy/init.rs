use std::net::IpAddr;
use std::net::SocketAddr;
use std::sync::Arc;

use anyhow::Result;
use tokio::task;

use crate::cli::ProxyAwareCommandCommon;
use crate::errors::ProxyError;
use crate::event::TaskManager;
use crate::proxy::ProxyState;
use crate::proxy::protocols::http;
use crate::types::ProxyAddrConfig;

pub async fn initialize_http_proxy(
    proxy_nic_config: &ProxyAddrConfig,
    state: Arc<ProxyState>,
    shutdown_rx: kanal::AsyncReceiver<()>,
    task_manager: Arc<TaskManager>,
) -> Result<task::JoinHandle<Result<(), ProxyError>>> {
    let proxy_address = proxy_nic_config.proxy_address();

    let (readiness_tx, readiness_rx) = oneshot::channel::<()>();

    let handle = tokio::spawn(async move {
        let proxy_address = proxy_address.clone();

        http::proxy::run_http_proxy(
            proxy_address,
            state,
            shutdown_rx,
            readiness_tx,
            task_manager,
        )
        .await
    });

    // Wait for the proxy to signal readiness
    let _ = readiness_rx.await.map_err(|e| {
        ProxyError::Internal(format!(
            "Failed to receive readiness signal: {}",
            e
        ))
    });

    tracing::info!(
        "HTTP Proxy server is listening on {}",
        proxy_nic_config.proxy_address()
    );

    Ok(handle)
}

pub fn get_http_proxy_address(
    common: &ProxyAwareCommandCommon,
) -> ProxyAddrConfig {
    let proxy_address = common.http_proxy_address.clone();

    let addr = proxy_address.unwrap_or("127.0.0.1:3180".to_string());
    let socket_addr: SocketAddr = addr
        .parse()
        .map_err(|e| format!("Invalid HTTP proxy address '{}': {}", addr, e))
        .unwrap();
    let sock_proxy_ip = socket_addr.ip();
    let proxy_port = socket_addr.port();

    let proxy_ip = match sock_proxy_ip {
        IpAddr::V4(ipv4) => ipv4,
        IpAddr::V6(_ipv6) => {
            panic!("IPV6 addresses are not supported for proxy");
        }
    };

    ProxyAddrConfig { proxy_ip, proxy_port }
}
