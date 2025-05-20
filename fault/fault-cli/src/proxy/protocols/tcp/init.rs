use std::net::IpAddr;
use std::net::SocketAddr;
use std::sync::Arc;

use anyhow::Result;
use async_std_resolver::resolver_from_system_conf;
use futures::future::join_all;
use rand;
use rand::seq::IndexedRandom;
use tokio::sync::mpsc;
use tokio::task;

use crate::errors::ProxyError;
use crate::event::TaskManager;
use crate::proxy::ProxyState;
use crate::proxy::protocols::tcp;
use crate::types::ProtocolType;
use crate::types::ProxyAddrConfig;
use crate::types::ProxyMap;
use crate::types::RemoteAddrConfig;

pub async fn initialize_tcp_proxies(
    proxied_protos: Vec<ProxyMap>,
    state: Arc<ProxyState>,
    shutdown_rx: kanal::AsyncReceiver<()>,
    task_manager: Arc<TaskManager>,
) -> Result<Vec<task::JoinHandle<std::result::Result<(), ProxyError>>>> {
    let count = proxied_protos.len();

    if count == 0 {
        return Ok(Vec::new());
    }

    // Create a oneshot channel for readiness signaling
    let (readiness_tx, mut readiness_rx) = mpsc::channel::<()>(count);

    let mut handles = Vec::new();

    for proto in proxied_protos {
        let handle = tokio::spawn(tcp::run_tcp_proxy(
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

impl ProxyMap {
    pub async fn parse(input: &str) -> Result<Self, String> {
        let mut parts = input.splitn(2, '=');
        let left = parts.next().ok_or_else(|| {
            format!("Invalid proxy protocol input (no '='): {}", input)
        })?;
        let right = parts.next().ok_or_else(|| {
            format!("Invalid proxy protocol input (no '='): {}", input)
        })?;

        let proxy = parse_left(left)?;
        let (proto, remote_host, remote_port) = parse_right(right)?;

        Ok(Self {
            proxy: get_tcp_proxy_address(proxy),
            remote: RemoteAddrConfig { remote_host, remote_port },
            proto,
        })
    }
}

pub async fn parse_proxy_protocols(
    protocols: Vec<String>,
) -> Result<Vec<ProxyMap>> {
    let result = join_all(
        protocols
            .iter()
            .map(async |p| ProxyMap::parse(p.as_str()).await.unwrap()),
    )
    .await;
    Ok(result)
}

fn get_tcp_proxy_address(addr: String) -> ProxyAddrConfig {
    let socket_addr: SocketAddr = addr
        .parse()
        .map_err(|e| format!("Invalid TCP proxy address '{}': {}", addr, e))
        .unwrap();
    let sock_proxy_ip = socket_addr.ip();
    let proxy_port = socket_addr.port();

    let proxy_ip = match sock_proxy_ip {
        IpAddr::V4(ipv4) => ipv4,
        IpAddr::V6(_ipv6) => {
            panic!("IPV6 addresses are not supported for proxy");
        }
    };

    ProxyAddrConfig { proxy_ip, proxy_port }
}

/// Parses the left side ("HOST:PORT" with HOST optional).
/// If only PORT is provided, defaults HOST to "0.0.0.0".
fn parse_left(left: &str) -> Result<String, String> {
    // Is it "HOST:PORT" or just "PORT"?
    if left.contains(':') {
        // We expect something like "localhost:9098"
        let mut iter = left.splitn(2, ':');
        let host = iter.next().unwrap();
        let port = iter.next().ok_or_else(|| {
            format!("Invalid proxy side (missing port): {}", left)
        })?;
        Ok(format!("{}:{}", host, port))
    } else {
        let port = left;
        Ok(format!("0.0.0.0:{}", port))
    }
}

/// Splits a "host:port" string into (host, port).
fn parse_host_port(
    input: &str,
    proto_type: Option<ProtocolType>,
) -> Result<(String, u16), String> {
    let mut parts = input.splitn(2, ':');
    let host =
        parts.next().ok_or_else(|| format!("Invalid host in '{}'", input))?;
    let port = parts.next().ok_or(match proto_type {
        Some(p) => match p {
            ProtocolType::Http => "80",
            ProtocolType::Https => "443",
            ProtocolType::Psql | ProtocolType::Psqls => "5432",
            ProtocolType::Tls => "",
            ProtocolType::None => "",
        },
        None => "",
    })?;

    let prt_num = port.parse::<u16>().expect("Remote port is invalid");

    Ok((host.to_string(), prt_num))
}

/// Parses the right side ("TYPE://HOST:PORT" with TYPE optional).
/// Returns (Option<ProtocolType>, "HOST:PORT").
pub fn parse_right(
    right: &str,
) -> Result<(Option<ProtocolType>, String, u16), String> {
    if let Some(idx) = right.find("://") {
        // We have a protocol
        let proto_str = &right[..idx];
        let addr = &right[idx + 3..]; // skip "://"

        // Parse the protocol enum, or ignore if unknown
        let proto = match proto_str {
            "psql" => Some(ProtocolType::Psql),
            "psqls" => Some(ProtocolType::Psqls),
            "http" => Some(ProtocolType::Http),
            "https" => Some(ProtocolType::Https),
            "tls" => Some(ProtocolType::Tls),
            _ => None,
        };

        if addr.contains(':') {
            let mut iter = addr.splitn(2, ':');
            let port = iter.next().ok_or_else(|| match proto.clone() {
                Some(p) => match p {
                    ProtocolType::Http => "80",
                    ProtocolType::Https => "443",
                    ProtocolType::Psql | ProtocolType::Psqls => "5432",
                    ProtocolType::Tls => "",
                    ProtocolType::None => "",
                },
                None => "",
            })?;

            if port.is_empty() {
                return Err(format!(
                    "Invalid remote side (missing host:port after protocol): {}",
                    right
                ));
            }
        }

        let (host, port) = parse_host_port(addr, proto.clone())?;
        Ok((proto, host, port))
    } else {
        // No "://", so no protocol
        // Expect right side to be "HOST:PORT"
        if !right.contains(':') {
            return Err(format!(
                "Invalid remote side (missing host:port): {}",
                right
            ));
        }
        let (host, port) = parse_host_port(right, None)?;
        Ok((None, host, port))
    }
}

pub async fn resolve_remote_host(host: String) -> Result<IpAddr, String> {
    let dns_resolver;

    dns_resolver = resolver_from_system_conf().await.unwrap();
    let response = dns_resolver.lookup_ip(host.clone()).await.unwrap();
    let candidates = response.into_iter().collect::<Vec<_>>();

    tracing::debug!("Domain {} Found addresses {:?}", host, candidates);

    let mut rng = rand::rng();

    Ok(candidates.choose(&mut rng).cloned().unwrap())
}
