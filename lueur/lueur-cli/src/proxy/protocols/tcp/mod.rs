use std::io::ErrorKind;
use std::net::IpAddr;
use std::net::SocketAddr;
use std::sync::Arc;

use anyhow::Result;
use init::resolve_remote_host;
use tokio::sync::mpsc;
use tokio::time::Instant;

use crate::errors::ProxyError;
use crate::event::TaskManager;
use crate::proxy::ProxyState;
use crate::types::ProxyMap;

pub mod init;
pub mod stream;

pub async fn run_tcp_proxy(
    proxied_proto: ProxyMap,
    state: Arc<ProxyState>,
    shutdown_rx: kanal::AsyncReceiver<()>,
    readiness_tx: mpsc::Sender<()>,
    task_manager: Arc<TaskManager>,
) -> Result<(), ProxyError> {
    let addr: SocketAddr = SocketAddr::new(
        IpAddr::V4(proxied_proto.proxy.proxy_ip),
        proxied_proto.proxy.proxy_port,
    );

    let state_cloned = state.clone();

    let proxy_listener =
        tokio::net::TcpListener::bind(addr).await.map_err(|e| {
            ProxyError::IoError(std::io::Error::new(
                e.kind(),
                format!("Failed to bind ebpf proxy to address {}: {}", addr, e),
            ))
        })?;

    let _ = readiness_tx.send(()).await.map_err(|e| {
        ProxyError::Internal(format!("Failed to send readiness signal: {}", e))
    });

    tracing::debug!("Listening for incoming TCP traffic on address {}", addr);

    let remote_host = proxied_proto.remote.remote_host.clone();

    loop {
        tokio::select! {
            _ = shutdown_rx.recv() => {
                tracing::info!("Shutdown signal received. Stopping listener.");
                break;
            },
            accept_result = proxy_listener.accept() => {
                match accept_result {
                    Ok((stream, addr)) => {
                        tracing::debug!("TCP proxy accepted connection from {}", addr);

                        let state = state_cloned.clone();
                        let proto = proxied_proto.clone();

                        let host = format!("{}:{}", remote_host, proto.remote.remote_port);

                        let event = task_manager
                            .new_fault_event(host.clone())
                            .await
                            .unwrap();

                        let _ = event.on_started(host, addr.to_string());

                        let start = Instant::now();
                        let remote_addr = resolve_remote_host(remote_host.clone()).await.unwrap();

                        let _ = event
                            .on_resolved(remote_host.clone(), start.elapsed().as_millis_f64());

                        // where are we sending traffic to
                        let connect_to: SocketAddr = SocketAddr::new(
                            remote_addr,
                            proto.remote.remote_port
                        );

                        tokio::spawn(async move {
                            let proto = proto.clone();

                            match stream::handle_stream(
                                stream,
                                connect_to,
                                &state,
                                false,
                                event.clone(),
                                Some(proto.clone())
                            ).await {
                                Ok((bytes_from_client, bytes_to_server)) => {
                                    let _ = event.on_response(0);
                                    let _ = event.on_completed(
                                        start.elapsed(),
                                        bytes_from_client,
                                        bytes_to_server,
                                    );
                                },
                                Err(e) if is_unexpected_eof(&e) => {
                                    tracing::debug!("EOF reached on stream: {}", e);
                                    let _ = event.on_response(0);
                                    let _ = event.on_completed(
                                        start.elapsed(),
                                        0,
                                        0,
                                    );
                                }
                                Err(e) => {
                                    tracing::error!("Error handling stream from {}: {:?}", addr, e);
                                    let _ = event.on_error(Box::new(e));
                                }
                            };
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

    tracing::debug!(
        "TCP proxy {}:{} is now finished, bye bye",
        proxied_proto.proxy.proxy_ip,
        proxied_proto.proxy.proxy_port
    );

    Ok(())
}

fn is_unexpected_eof(err: &ProxyError) -> bool {
    match err {
        ProxyError::IoError(ioerr) => ioerr.kind() == ErrorKind::UnexpectedEof,
        _ => false,
    }
}
