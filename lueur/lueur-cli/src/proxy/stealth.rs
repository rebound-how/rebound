#[cfg(all(
    target_os = "linux",
    any(feature = "stealth", feature = "stealth-auto-build")
))]
use std::error::Error;
use std::io::ErrorKind;
use std::mem::MaybeUninit;
use std::net::IpAddr;
use std::net::Ipv4Addr;
use std::net::SocketAddr;
use std::os::fd::AsRawFd;
use std::sync::Arc;

use async_std_resolver::config;
use async_std_resolver::resolver;
use axum::body::Body;
use axum::http::Request as AxumRequest;
use axum::http::Response as AxumResponse;
use hyper_util::rt::TokioIo;
use libc::SO_ORIGINAL_DST;
use libc::SOL_IP;
use libc::getsockopt;
use libc::sockaddr_in;
use libc::socklen_t;
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

/// Handles CONNECT method requests by establishing a TCP tunnel,
/// injecting any configured network faults, and applying plugin middleware.
#[tracing::instrument]
pub async fn handle_stream(
    stream: TcpStream,
    state: Arc<ProxyState>,
    passthrough: bool,
    event: Box<dyn ProxyTaskEvent>,
) -> Result<(), ProxyError> {
    let fd = stream.as_raw_fd();
    let connect_to = get_original_dst(fd).await.unwrap();
    tracing::debug!("Original destination: {:?}", connect_to);

    let plugins = state.plugins.clone();

    match TcpStream::connect(connect_to.clone()).await {
        Ok(raw_server_stream) => {
            let start = Instant::now();
            let _ = event.on_started("".to_string());
            let client_stream: Box<dyn Bidirectional + 'static> =
                Box::new(stream);

            let server_stream: Box<dyn Bidirectional + 'static> =
                Box::new(raw_server_stream);

            let mut modified_client_stream = client_stream;
            let mut modified_server_stream = server_stream;

            if !passthrough {
                let plugins_lock = plugins.read().await;
                match plugins_lock
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
                        return Ok(());
                    }
                }
                drop(plugins_lock);
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
                    tracing::debug!(
                        "Connection closed. Bytes from client: {}, bytes to server: {}",
                        bytes_from_client,
                        bytes_to_server
                    );
                }
                Err(e) => {
                    tracing::error!(
                        "Error in bidirectional copy (Host {}): {}",
                        connect_to,
                        e
                    );
                    let _ = event.on_error(e);
                    //let _ = event.on_completed(start.elapsed(),
                    // 0, 0);
                }
            };
        }
        Err(e) => {
            error!("Failed to connect to target {:?} - {}", connect_to, e);

            let _ = event.on_error(Box::new(e));
        }
    };

    Ok(())
}

pub async fn resolve_addresses(host: String) -> Vec<IpAddr> {
    let resolver = resolver(
        config::ResolverConfig::default(),
        config::ResolverOpts::default(),
    )
    .await;

    let response = resolver.lookup_ip(host.clone()).await.unwrap();
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

    // Connect the client reader to the server writer.
    // That is, whenever we receive data from the client, we forward it to the
    // server.
    let client_to_server = async {
        let count = tokio::io::copy(&mut read_inbound, &mut write_outbound)
            .await
            .inspect_err(|e| {
                error!(
                    error = e.to_string(),
                    "error copying read_inbound to write_outbound"
                )
            })?;

        let mut lock = c2s.lock().await;
        lock.size = count;

        write_outbound.shutdown().await.inspect_err(|e| {
            error!(error = e.to_string(), "error shutting down write_outbound!")
        })
    };

    // Connect the server reader to the client writer.
    // That is, whenever we receive data from the server, we forward it to the
    // client.
    let server_to_client = async {
        let count = tokio::io::copy(&mut read_outbound, &mut write_inbound)
            .await
            .inspect_err(|e| {
                error!(
                    error = e.to_string(),
                    "error copying read_outbound to write_inbound!"
                )
            })?;

        if let Err(err) = write_inbound.shutdown().await {
            match err.kind() {
                // The client can shut down the inbound connection sometimes. If
                // this is the case, shutting down this connection
                // will throw this error. In practice, it doesn't really matter.
                // There's no good way to check if a connection is
                // closed without trying to read from it and seeing what
                // happens. It's effectively the same as doing this.
                ErrorKind::NotConnected => {
                    tracing::debug!(
                        "unable to shutdown server stream as client stream already is shutdown"
                    );
                }

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

        let mut lock = s2c.lock().await;
        lock.size = count;

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

/// Retrieve the original destination using getsockopt(SO_ORIGINAL_DST)
async fn get_original_dst(fd: i32) -> Option<String> {
    let mut orig_dst = MaybeUninit::<sockaddr_in>::uninit();
    let mut orig_len = std::mem::size_of::<sockaddr_in>() as socklen_t;
    tracing::debug!("Socket fd {}", fd.clone());
    let ret = unsafe {
        getsockopt(
            fd,
            SOL_IP,
            SO_ORIGINAL_DST,
            orig_dst.as_mut_ptr() as *mut _,
            &mut orig_len as *mut socklen_t,
        )
    };

    if ret != 0 {
        tracing::error!(
            "getsockopt failed: {:?}",
            std::io::Error::last_os_error()
        );
        None
    } else {
        let sa = unsafe { orig_dst.assume_init() };
        // sockaddr_in fields are in network byte order.
        let ip = Ipv4Addr::from(u32::from_be(sa.sin_addr.s_addr));
        let port = u16::from_be(sa.sin_port);
        Some(format!("{}:{}", ip.to_string(), port))
    }
}
