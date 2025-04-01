use std::sync::Arc;

use anyhow::Result;
use tokio::sync::broadcast;
use tokio::sync::watch;
use tokio::task;

use crate::config::ProxyConfig;
use crate::errors::ProxyError;
use crate::event::TaskManager;
use crate::proxy::protocols::ebpf;
use crate::state::AppState;
use crate::types::EbpfProxyAddrConfig;

pub async fn initialize_ebpf_proxy(
    ebpf_proxy_config: &EbpfProxyAddrConfig,
    state: AppState,
    shutdown_rx: broadcast::Receiver<()>,
    config_rx: watch::Receiver<ProxyConfig>,
    task_manager: Arc<TaskManager>,
) -> Result<task::JoinHandle<std::result::Result<(), ProxyError>>> {
    let proxy_address = ebpf_proxy_config.proxy_address();

    // Create a oneshot channel for readiness signaling
    let (readiness_tx, readiness_rx) = oneshot::channel::<()>();

    let handle = tokio::spawn(ebpf::run_ebpf_proxy(
        proxy_address.clone(),
        state.proxy_state,
        shutdown_rx,
        readiness_tx,
        config_rx,
        task_manager,
    ));

    // Wait for the proxy to signal readiness
    let _ = readiness_rx.await.map_err(|e| {
        ProxyError::Internal(format!(
            "Failed to receive readiness signal: {}",
            e
        ))
    });

    tracing::info!("eBPF Proxy server is listening on {}", proxy_address);

    Ok(handle)
}
