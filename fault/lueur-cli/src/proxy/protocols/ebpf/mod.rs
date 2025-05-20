use std::io::ErrorKind;
use std::mem::MaybeUninit;
use std::net::IpAddr;
use std::net::Ipv4Addr;
use std::net::SocketAddr;
use std::os::fd::AsRawFd;
use std::sync::Arc;

use ::oneshot::Sender;
use anyhow::Result;
use libc::SO_ORIGINAL_DST;
use libc::SOL_IP;
use libc::getsockopt;
use libc::sockaddr_in;
use libc::socklen_t;
use tokio::net::TcpStream;
use tokio::sync::broadcast;
use tokio::time::Instant;

use crate::errors::ProxyError;
use crate::event::TaskManager;
use crate::proxy::ProxyState;
use crate::proxy::protocols::tcp::stream::handle_stream;

pub mod init;

#[cfg(all(
    target_os = "linux",
    any(feature = "stealth", feature = "stealth-auto-build")
))]
pub async fn run_ebpf_proxy(
    ebpf_proxy_address: String,
    state: Arc<ProxyState>,
    shutdown_rx: kanal::AsyncReceiver<()>,
    readiness_tx: Sender<()>,
    task_manager: Arc<TaskManager>,
) -> Result<(), ProxyError> {
    let addr: SocketAddr = ebpf_proxy_address.parse().map_err(|e| {
        ProxyError::Internal(format!(
            "Failed to parse eBpf proxy address {}: {}",
            ebpf_proxy_address, e
        ))
    })?;

    let state_cloned = state.clone();

    let proxy_listener =
        tokio::net::TcpListener::bind(addr).await.map_err(|e| {
            ProxyError::IoError(std::io::Error::new(
                e.kind(),
                format!("Failed to bind ebpf proxy to address {}: {}", addr, e),
            ))
        })?;

    let _ = readiness_tx.send(()).map_err(|e| {
        ProxyError::Internal(format!("Failed to send readiness signal: {}", e))
    });

    tracing::debug!("Listening for incoming request via eBPF redirection");

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

                        let start = Instant::now();

                        let event = task_manager
                            .new_fault_event("".to_string())
                            .await
                            .unwrap();

                        let _ = event.on_started(addr.to_string(), addr.to_string());

                        // we already have an IP, so let's not pretend we
                        // did anything
                        let _ = event.on_resolved(addr.ip().to_string(), 0.0);

                        let state = state_cloned.clone();

                        tokio::spawn(async move {
                            let state = state.clone();
                            let addr = addr;

                            match get_connect_addr(&stream).await {
                                Ok(candidate) =>  match candidate {
                                    Some(connect_to) => {
                                        match handle_stream(
                                            stream,
                                            connect_to,
                                            &state,
                                            false,
                                            event.clone(),
                                            None
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
                                            }
                                            Err(e) => {
                                                tracing::error!("Error handling stream from {}: {:?}", addr, e);
                                                let _ = event.on_error(Box::new(e));
                                            }
                                        };

                                        Ok(())
                                    }
                                    None => {
                                        Err(
                                            ProxyError::Internal(
                                                "failed to locate a target address to on the socket".to_string()
                                            )
                                        )
                                    }
                                }
                                Err(e) => Err(e)
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

    tracing::debug!("ebpf proxy is now finished, bye bye");

    Ok(())
}

#[cfg(all(
    target_os = "linux",
    any(feature = "stealth", feature = "stealth-auto-build")
))]
async fn get_connect_addr(
    stream: &TcpStream,
) -> Result<Option<SocketAddr>, ProxyError> {
    let fd = stream.as_raw_fd();
    get_original_dst(fd).await
}

#[cfg(all(
    target_os = "linux",
    any(feature = "stealth", feature = "stealth-auto-build")
))]
/// Retrieve the original destination using getsockopt(SO_ORIGINAL_DST)
async fn get_original_dst(fd: i32) -> Result<Option<SocketAddr>, ProxyError> {
    let mut orig_dst = MaybeUninit::<sockaddr_in>::uninit();
    let mut orig_len = std::mem::size_of::<sockaddr_in>() as socklen_t;
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
        Err(ProxyError::IoError(std::io::Error::last_os_error()))
    } else {
        let sa = unsafe { orig_dst.assume_init() };
        // sockaddr_in fields are in network byte order.
        let ip = Ipv4Addr::from(u32::from_be(sa.sin_addr.s_addr));
        let port = u16::from_be(sa.sin_port);
        Ok(Some(SocketAddr::new(IpAddr::V4(ip), port)))
    }
}

fn is_unexpected_eof(err: &ProxyError) -> bool {
    match err {
        ProxyError::IoError(ioerr) => ioerr.kind() == ErrorKind::UnexpectedEof,
        _ => false,
    }
}
