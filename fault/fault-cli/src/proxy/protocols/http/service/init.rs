use std::sync::Arc;

use anyhow::Result;
use tokio::sync::mpsc;
use tokio::task;

use crate::errors::ProxyError;
use crate::event::TaskManager;
use crate::proxy::ProxyState;
use crate::proxy::protocols::http::service::run_http_proxy;
use crate::types::ProxyMap;

pub async fn initialize_http_service_proxies(
    proxied_protos: Vec<ProxyMap>,
    state: Arc<ProxyState>,
    shutdown_rx: kanal::AsyncReceiver<()>,
    task_manager: Arc<TaskManager>,
) -> Result<Vec<task::JoinHandle<std::result::Result<(), ProxyError>>>> {
    let count = proxied_protos.len();

    if count == 0 {
        return Ok(Vec::new());
    }

    let (readiness_tx, mut readiness_rx) = mpsc::channel::<()>(count);

    let mut handles = Vec::new();

    for proto in proxied_protos {
        let handle = tokio::spawn(run_http_proxy(
            proto,
            state.clone(),
            shutdown_rx.clone(),
            readiness_tx.clone(),
            task_manager.clone(),
        ));
        handles.push(handle);
    }

    let mut pending = count;

    while readiness_rx.recv().await.is_some() {
        pending -= 1;

        if pending == 0 {
            break;
        }
    }

    Ok(handles)
}
