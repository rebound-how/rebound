use std::net::SocketAddr;
use std::sync::Arc;

use ::oneshot::Sender;
use axum::body::Body;
use axum::http::Request;
use axum::response::IntoResponse;
use hyper::body::Incoming;
use hyper::server::conn::http1;
use hyper_util::rt::TokioIo;
use tokio::sync::mpsc;
use url::Url;

use crate::errors::ProxyError;
use crate::event::TaskManager;
use crate::proxy::ProxyState;
use crate::types::ProxyMap;

pub mod handler;
pub mod init;

#[tracing::instrument(skip_all)]
async fn handle_http_request(
    source_addr: SocketAddr,
    proto: ProxyMap,
    req: Request<Body>,
    state: Arc<ProxyState>,
    task_manager: Arc<TaskManager>,
) -> Result<hyper::Response<Body>, ProxyError> {
    let req = req.map(Body::new);

    let path = match req.uri().path_and_query() {
        Some(path) => path.to_string(),
        None => "/".to_string(),
    };

    let state: Arc<ProxyState> = state.clone();
    let hosts: arc_swap::Guard<Arc<Vec<String>>> = state.upstream_hosts.load();
    let upstream_host = get_upstream_host(&proto);

    let passthrough = if hosts.contains(&String::from("*")) {
        false
    } else {
        !hosts.contains(&upstream_host)
    };

    let upstream = format!("{}{}", upstream_host, path);
    let upstream_url: Url = upstream.parse().unwrap();

    let event = if !passthrough {
        task_manager.new_fault_event(upstream_url.to_string()).await.unwrap()
    } else {
        task_manager
            .new_passthrough_event(upstream_url.to_string())
            .await
            .unwrap()
    };

    let r = handler::handle_request(
        source_addr,
        upstream_host,
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

pub async fn run_http_proxy(
    proto: ProxyMap,
    state: Arc<ProxyState>,
    shutdown_rx: kanal::AsyncReceiver<()>,
    readiness_tx: mpsc::Sender<()>,
    task_manager: Arc<TaskManager>,
) -> Result<(), ProxyError> {
    let proxy_address = &proto.proxy.proxy_address();
    let addr: SocketAddr = proxy_address.parse().map_err(|e| {
        ProxyError::Internal(format!(
            "Failed to parse proxy address {}: {}",
            proxy_address, e
        ))
    })?;

    let proxy_listener =
        tokio::net::TcpListener::bind(addr).await.map_err(|e| {
            ProxyError::IoError(std::io::Error::new(
                e.kind(),
                format!("Failed to bind to address {}: {}", addr, e),
            ))
        })?;

    let _ = readiness_tx.send(()).await.map_err(|e| {
        ProxyError::Internal(format!("Failed to send readiness signal: {}", e))
    });

    loop {
        tokio::select! {
            _ = shutdown_rx.recv() => {
                tracing::info!("Shutdown signal received. Stopping listener.");
                break;
            },
            accept_result = proxy_listener.accept() => {
                match accept_result {
                    Ok((stream, addr)) => {
                        tracing::debug!("Accepted connection from {}", addr);

                        let io = TokioIo::new(stream);
                        let task_manager = task_manager.clone();
                        let state = state.clone();
                        let proto = proto.clone();

                        let hyper_service =
                        hyper::service::service_fn(move |request: Request<Incoming>| {
                            handle_http_request(
                                addr,
                                proto.clone(),
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

    tracing::debug!("Proxy is now finished, bye bye");

    Ok(())
}

//
// -------------------- Private functions -----------------------------------
//

fn get_upstream_host(proto: &ProxyMap) -> String {
    if proto.remote_requires_tls() {
        format!(
            "https://{}:{}",
            proto.remote.remote_host, proto.remote.remote_port
        )
    } else {
        format!(
            "http://{}:{}",
            proto.remote.remote_host, proto.remote.remote_port
        )
    }
}
