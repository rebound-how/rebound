use std::error::Error;
use std::io::ErrorKind;
use std::net::IpAddr;
use std::net::SocketAddr;
use std::sync::Arc;

use async_std_resolver::resolver_from_system_conf;
use axum::body::Body;
use axum::http::Request as AxumRequest;
use axum::http::Response as AxumResponse;
use hyper::upgrade::Upgraded;
use hyper_util::rt::TokioIo;
use tokio::io::AsyncWriteExt;
use tokio::io::split;
use tokio::net::TcpStream;
use tokio::sync::Mutex;
use tokio::time::Instant;
use tracing::error;
use url::Url;

use crate::errors::ProxyError;
use crate::event::ProxyTaskEvent;
use crate::fault::Bidirectional;
use crate::plugin::ProxyPlugin;
use crate::proxy::ProxyState;
use crate::types::ConnectRequest;

#[async_trait::async_trait]
impl Bidirectional for TokioIo<Upgraded> {
    async fn shutdown(&mut self) -> std::io::Result<()> {
        AsyncWriteExt::shutdown(self).await
    }
}

/// Handles CONNECT method requests by establishing a TCP tunnel,
/// injecting any configured network faults, and applying plugin middleware.
#[tracing::instrument(skip_all)]
pub async fn handle_connect(
    source_addr: SocketAddr,
    req: AxumRequest<Body>,
    app_state: Arc<ProxyState>,
    upstream: Url,
    passthrough: bool,
    event: Box<dyn ProxyTaskEvent>,
) -> Result<AxumResponse<Body>, ProxyError> {
    let target_host = upstream.host().unwrap().to_string();
    let target_port = upstream.port_or_known_default().unwrap();

    tracing::debug!("Tunneling {}", upstream);

    let connect_request =
        ConnectRequest { target_host: target_host.clone(), target_port };

    let host = connect_request.target_host;

    // Acquire a read lock for plugins
    let faults_plugins = app_state.faults_plugin.clone();

    tokio::spawn(async move {
        let event = event.clone();
        let upstream_str = upstream.to_string();

        let port = connect_request.target_port;
        let start = Instant::now();
        let addresses = resolve_addresses(host.clone()).await;
        let dns_resolution_time = start.elapsed().as_millis_f64();

        let addr: SocketAddr = SocketAddr::new(addresses[0], port);

        tracing::debug!("Using addr {} for remote host {}", addr, upstream);

        match hyper::upgrade::on(req).await {
            Ok(upgraded) => match TcpStream::connect(addr).await {
                Ok(raw_server_stream) => {
                    let start = Instant::now();
                    let _ =
                        event.on_started(upstream_str, source_addr.to_string());
                    let _ =
                        event.on_resolved(host.clone(), dns_resolution_time);

                    let client_stream: Box<dyn Bidirectional + 'static> =
                        Box::new(TokioIo::new(upgraded));

                    let server_stream: Box<dyn Bidirectional + 'static> =
                        Box::new(raw_server_stream);

                    let mut modified_client_stream = client_stream;
                    let mut modified_server_stream = server_stream;

                    if !passthrough {
                        let faults = faults_plugins.load();
                        match faults
                            .inject_tunnel_faults(
                                modified_client_stream,
                                modified_server_stream,
                                event.clone(),
                            )
                            .await
                        {
                            Ok((client, server)) => {
                                modified_client_stream = client;
                                modified_server_stream = server;
                            }
                            Err(e) => {
                                tracing::error!(
                                    "Plugin failed to inject tunnel faults: {}",
                                    e
                                );
                                return;
                            }
                        }
                        drop(faults);
                    }

                    match bidirectional_copy(
                        modified_client_stream,
                        modified_server_stream,
                    )
                    .await
                    {
                        Ok((bytes_from_client, bytes_to_server)) => {
                            let _ = event.on_response(0);
                            let _ = event.on_completed(
                                start.elapsed(),
                                bytes_from_client,
                                bytes_to_server,
                            );
                        }
                        Err(e) => {
                            tracing::error!(
                                "Error in bidirectional copy (Host {}): {}",
                                host,
                                e
                            );
                            let _ = event.on_error(e);
                        }
                    };
                }
                Err(e) => {
                    error!(
                        "Failed to connect to target {}:{} - {}",
                        target_host, target_port, e
                    );

                    let _ = event.on_error(Box::new(e));
                }
            },
            Err(e) => {
                error!("Upgrade error: {}", e);
                let _ = event.on_error(Box::new(e));
            }
        }
    });

    Ok(AxumResponse::new(Body::empty()))
}

pub async fn resolve_addresses(host: String) -> Vec<IpAddr> {
    let dns_resolver;

    dns_resolver = resolver_from_system_conf().await.unwrap();
    let response = dns_resolver.lookup_ip(host.clone()).await.unwrap();
    let filtered = response.into_iter().collect::<Vec<_>>();

    tracing::debug!("Domain {} Found addresses {:?}", host.clone(), filtered);

    filtered
}

struct TransferredBytesSize {
    pub size: u64,
}

// see https://stackoverflow.com/a/78335511/1363905
async fn bidirectional_copy(
    incoming: Box<dyn Bidirectional + 'static>,
    outbound: Box<dyn Bidirectional + 'static>,
) -> Result<(u64, u64), Box<dyn Error>> {
    let c2s = Arc::new(Mutex::new(TransferredBytesSize { size: 0 }));
    let s2c = Arc::new(Mutex::new(TransferredBytesSize { size: 0 }));

    // Split the streams into read and write halves.
    let (mut read_inbound, mut write_inbound) = split(incoming);
    let (mut read_outbound, mut write_outbound) = split(outbound);

    let c2s_clone = Arc::clone(&c2s);
    let s2c_clone = Arc::clone(&s2c);

    // Connect the client reader to the server writer.
    // That is, whenever we receive data from the client, we forward it to the
    // server.
    let client_to_server = async {
        let count =
            tokio::io::copy(&mut read_inbound, &mut write_outbound).await?;
        c2s_clone.lock().await.size = count;

        match write_outbound.shutdown().await {
            Err(ref err)
                if matches!(
                    err.kind(),
                    ErrorKind::UnexpectedEof | ErrorKind::NotConnected
                ) =>
            {
                tracing::debug!("write_outbound shutdown ignored: {:?}", err);
            }
            Err(err) => {
                tracing::debug!(
                    error = err.to_string(),
                    "error shutting down write_outbound!"
                );
                return Err(err);
            }
            _ => {}
        }

        Ok(())
    };

    // Connect the server reader to the client writer.
    // That is, whenever we receive data from the server, we forward it to the
    // client.
    let server_to_client = async {
        let count =
            tokio::io::copy(&mut read_outbound, &mut write_inbound).await?;
        s2c_clone.lock().await.size = count;

        match write_inbound.shutdown().await {
            Err(ref err)
                if matches!(
                    err.kind(),
                    ErrorKind::UnexpectedEof | ErrorKind::NotConnected
                ) =>
            {
                tracing::debug!("write_inbound shutdown ignored: {:?}", err);
            }
            Err(err) => {
                tracing::debug!(
                    error = err.to_string(),
                    "error shutting down write_inbound!"
                );
                return Err(err);
            }
            _ => {}
        }

        Ok(())
    };

    let (res_c2s, res_s2c) = tokio::join!(client_to_server, server_to_client);

    match (res_c2s, res_s2c) {
        (Ok(_), Ok(_)) => {}
        (Err(ref e), Ok(_)) | (Ok(_), Err(ref e))
            if e.kind() == ErrorKind::UnexpectedEof =>
        {
            tracing::debug!("One direction ended with unexpected EOF: {:?}", e);
            let _ = write_outbound.shutdown().await;
            let _ = write_inbound.shutdown().await;
        }
        (Err(e1), Err(_e2)) => return Err(Box::new(e1)),
        (Err(e), _) | (_, Err(e)) => return Err(Box::new(e)),
    }

    // Explicitly drop read halves to close those ends
    drop(read_inbound);
    drop(read_outbound);

    let c2s_count = c2s.lock().await.size;
    let s2c_count = s2c.lock().await.size;

    Ok((c2s_count, s2c_count))
}
