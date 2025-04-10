use std::io::ErrorKind;
use std::net::SocketAddr;
use std::sync::Arc;

use anyhow::Result;
use rustls_pki_types::ServerName;
use rustls_platform_verifier::ConfigVerifierExt;
use tokio::io::AsyncWriteExt;
use tokio::io::split;
use tokio::net::TcpStream;
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

#[tracing::instrument]
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
    let c2s = Arc::new(Mutex::new(TransferredBytesSize { size: 0 }));
    let s2c = Arc::new(Mutex::new(TransferredBytesSize { size: 0 }));

    // Split the streams into read and write halves.
    let (mut read_inbound, mut write_inbound) = split(incoming);
    let (mut read_outbound, mut write_outbound) = split(outbound);

    // Connect the client reader to the server writer.
    // That is, whenever we receive data from the client, we forward it to the
    // server.
    let client_to_server = async {
        let count =
            tokio::io::copy(&mut read_inbound, &mut write_outbound).await?;

        let mut lock = c2s.lock().await;
        lock.size = count;

        if let Err(err) = write_outbound.shutdown().await {
            match err.kind() {
                ErrorKind::UnexpectedEof => {}
                _ => {
                    error!(
                        error = err.to_string(),
                        error_kind = err.kind().to_string(),
                        "error shutting down write_outbound!"
                    );

                    return Err(err);
                }
            }
        }

        Ok(())
    };

    // Connect the server reader to the client writer.
    // That is, whenever we receive data from the server, we forward it to the
    // client.
    let server_to_client = async {
        let count =
            tokio::io::copy(&mut read_outbound, &mut write_inbound).await?;

        let mut lock = s2c.lock().await;
        lock.size = count;

        if let Err(err) = write_inbound.shutdown().await {
            match err.kind() {
                ErrorKind::UnexpectedEof => {}
                _ => {
                    error!(
                        error = err.to_string(),
                        error_kind = err.kind().to_string(),
                        "error shutting down write_inbound!"
                    );

                    return Err(err);
                }
            }
        }

        Ok(())
    };

    // Poll both tasks.
    tokio::try_join!(client_to_server, server_to_client)?;

    let lock = c2s.lock().await;
    let c2s_count = lock.size;

    let lock = s2c.lock().await;
    let s2c_count = lock.size;

    Ok((c2s_count, s2c_count))
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

    let raw_server_stream =
        TcpStream::connect(connect_to).await.map_err(ProxyError::from)?;

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
    let config = ClientConfig::with_platform_verifier();
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
