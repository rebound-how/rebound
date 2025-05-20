use std::sync::Arc;

use anyhow::Result;
use tokio::task;

use crate::errors::ProxyError;
use crate::event::TaskManager;
use crate::proxy::ProxyState;
use crate::proxy::protocols::ebpf;
use crate::types::EbpfProxyAddrConfig;

pub async fn initialize_ebpf_proxy(
    ebpf_proxy_config: &EbpfProxyAddrConfig,
    state: Arc<ProxyState>,
    shutdown_rx: kanal::AsyncReceiver<()>,
    task_manager: Arc<TaskManager>,
) -> Result<task::JoinHandle<Result<(), ProxyError>>> {
    let proxy_address = ebpf_proxy_config.proxy_address();

    // Create a oneshot channel for readiness signaling
    let (readiness_tx, readiness_rx) = oneshot::channel::<()>();

    let handle = tokio::spawn(async move {
        ebpf::run_ebpf_proxy(
            proxy_address.clone(),
            state.clone(),
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
        "eBPF Proxy server is listening on {}",
        ebpf_proxy_config.proxy_address()
    );

    Ok(handle)
}
