use std::io::ErrorKind;
use std::net::SocketAddr;
use std::sync::Arc;
use std::sync::atomic::AtomicU64;
use std::sync::atomic::Ordering;
use std::time::Duration;

use anyhow::Result;
use rustls_pki_types::ServerName;
use rustls_platform_verifier::ConfigVerifierExt;
use socket2::SockRef;
use socket2::TcpKeepalive;
use tokio::io::AsyncWriteExt;
use tokio::io::split;
use tokio::net::TcpStream;
use tokio::select;
use tokio::sync::Mutex;
use tokio_rustls::TlsConnector;
use tokio_rustls::rustls::ClientConfig;
use tracing::error;

use crate::errors::ProxyError;
use crate::event::ProxyTaskEvent;
use crate::fault::Bidirectional;
use crate::fault::TlsBidirectional;
use crate::plugin::ProxyPlugin;
use crate::proxy::ProxyState;
use crate::types::ProxyMap;

#[tracing::instrument(skip_all)]
pub async fn handle_stream(
    stream: TcpStream,
    connect_to: SocketAddr,
    state: &ProxyState,
    passthrough: bool,
    event: Box<dyn ProxyTaskEvent>,
    protocol: Option<ProxyMap>,
) -> Result<(u64, u64), ProxyError> {
    if protocol.is_some() {
        let proxy_protocol = protocol.unwrap();
        let remote_host = proxy_protocol.remote.remote_host.clone();

        if proxy_protocol.remote_requires_tls() {
            process_tcp_stream(
                stream,
                connect_to,
                state,
                passthrough,
                event,
                true,
                remote_host,
            )
            .await
        } else {
            process_tcp_stream(
                stream,
                connect_to,
                state,
                passthrough,
                event,
                false,
                remote_host,
            )
            .await
        }
    } else {
        process_tcp_stream(
            stream,
            connect_to,
            state,
            passthrough,
            event,
            false,
            "".to_string(),
        )
        .await
    }
}

struct TransferredBytesSize {
    pub size: u64,
}

// see https://stackoverflow.com/a/78335511/1363905
async fn bidirectional_copy(
    incoming: Box<dyn Bidirectional + 'static>,
    outbound: Box<dyn Bidirectional + 'static>,
) -> Result<(u64, u64), ProxyError> {
    let c2s = Arc::new(AtomicU64::new(0));
    let s2c = Arc::new(AtomicU64::new(0));

    let (mut read_inbound, mut write_inbound) = split(incoming);
    let (mut read_outbound, mut write_outbound) = split(outbound);

    let mut c2s_done = false;
    let mut s2c_done = false;

    loop {
        select! {
            result = tokio::io::copy(&mut read_inbound, &mut write_outbound), if !c2s_done => {
                match result {
                    Ok(count) => {
                        c2s.store(count, Ordering::Relaxed);
                        if let Err(e) = write_outbound.shutdown().await {
                            if e.kind() != ErrorKind::UnexpectedEof {
                                return Err(ProxyError::IoError(e));
                            }
                        }
                    }
                    Err(e) => {
                        if e.kind() != ErrorKind::UnexpectedEof {
                            return Err(ProxyError::IoError(e));
                        }
                        tracing::debug!("Client to server ended with EOF: {:?}", e);
                    }
                }
                c2s_done = true;
            }

            result = tokio::io::copy(&mut read_outbound, &mut write_inbound), if !s2c_done => {
                match result {
                    Ok(count) => {
                        s2c.store(count, Ordering::Relaxed);
                        if let Err(e) = write_inbound.shutdown().await {
                            if e.kind() != ErrorKind::UnexpectedEof {
                                return Err(ProxyError::IoError(e));
                            }
                        }
                    }
                    Err(e) => {
                        if e.kind() != ErrorKind::UnexpectedEof {
                            return Err(ProxyError::IoError(e));
                        }
                        tracing::debug!("Server to client ended with EOF: {:?}", e);
                    }
                }
                s2c_done = true;
            }

            else => {
                // Both sides are done
                break;
            }
        }
    }

    drop(read_inbound);
    drop(read_outbound);

    let c2s_total = c2s.load(Ordering::Relaxed);
    let s2c_total = s2c.load(Ordering::Relaxed);

    tracing::debug!("c2s {} bytes / s2c {} bytes", c2s_total, s2c_total);

    Ok((c2s_total, s2c_total))
}

async fn process_tcp_stream(
    stream: TcpStream,
    connect_to: SocketAddr,
    state: &ProxyState,
    passthrough: bool,
    event: Box<dyn ProxyTaskEvent>,
    remote_with_tls: bool,
    hostname: String,
) -> Result<(u64, u64), ProxyError> {
    let plugins = state.faults_plugin.load();

    stream.set_nodelay(true)?;

    let mut raw_server_stream =
        TcpStream::connect(connect_to).await.map_err(ProxyError::from)?;

    raw_server_stream.set_nodelay(true)?;

    let client_stream: Box<dyn Bidirectional + 'static> = Box::new(stream);
    let server_stream: Box<dyn Bidirectional + 'static> =
        Box::new(raw_server_stream);

    process_stream(
        client_stream,
        server_stream,
        passthrough,
        plugins,
        event,
        remote_with_tls,
        hostname,
    )
    .await
}

async fn process_stream(
    client_stream: Box<dyn Bidirectional + 'static>,
    server_stream: Box<dyn Bidirectional + 'static>,
    passthrough: bool,
    plugins: arc_swap::Guard<Arc<crate::plugin::CompositePlugin>>,
    event: Box<dyn ProxyTaskEvent>,
    remote_with_tls: bool,
    hostname: String,
) -> Result<(u64, u64), ProxyError> {
    let mut modified_client_stream = client_stream;
    let mut modified_server_stream = server_stream;

    if !passthrough {
        match plugins
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
                tracing::error!("Plugin failed to inject tunnel faults: {}", e);
                return Ok((0, 0));
            }
        }
    }

    if remote_with_tls {
        modified_server_stream =
            wrap_tls(modified_server_stream, hostname).await?;
    }

    let (bytes_from_client, bytes_to_server) =
        bidirectional_copy(modified_client_stream, modified_server_stream)
            .await?;

    Ok((bytes_from_client, bytes_to_server))
}

async fn wrap_tls(
    stream: Box<dyn Bidirectional + 'static>,
    hostname: String,
) -> Result<Box<dyn Bidirectional + 'static>, ProxyError> {
    let config = ClientConfig::with_platform_verifier()?;
    let tls_config = Arc::new(config);

    let domain = ServerName::try_from(hostname)
        .map_err(|_| ProxyError::Other("Invalid Server name".into()))?;
    let connector = TlsConnector::from(tls_config);
    let tls_stream = connector
        .connect(domain, stream)
        .await
        .map_err(|e| ProxyError::Other(e.to_string()))?;

    Ok(Box::new(TlsBidirectional { inner: tls_stream }))
}
