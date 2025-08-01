use std::net::IpAddr;
use std::net::SocketAddr;

use anyhow::Result;

use crate::errors::ProxyError;
use crate::types::ProtocolType;
use crate::types::ProxyAddrConfig;
use crate::types::ProxyMap;
use crate::types::RemoteAddrConfig;

#[derive(Debug, Clone)]
pub struct HostPort {
    pub host: String,
    pub port: u16,
}

impl ProxyMap {
    /// Parse a mapping string like:
    /// - `http://localhost:9090=example.com:8080`
    /// - `tcp://:9090=example.com:5432`
    /// - `http:9090=example.com:80`
    /// - `:9090=example.com:80`  (defaults to tcp)
    pub fn parse(s: &str) -> Result<Self, String> {
        let mut parts = s.splitn(2, '=');
        let left = parts
            .next()
            .ok_or_else(|| format!("Missing '=' in proxy spec: {}", s))?;
        let right = parts
            .next()
            .ok_or_else(|| format!("Missing target after '=': {}", s))?;

        // Parse both sides with same logic, left defines protocol
        let (proto, listen_addr) = Self::parse_side(left, None)?;
        let (_, target_addr) = Self::parse_side(right, Some(proto))?;

        Ok(ProxyMap {
            proto: Some(proto),
            proxy: ProxyAddrConfig {
                proxy_ip: listen_addr
                    .host
                    .parse()
                    .map_err(|e| format!("failed to parse proxy addr {}", e))?,
                proxy_port: listen_addr.port,
            },
            remote: RemoteAddrConfig {
                remote_host: target_addr.host,
                remote_port: target_addr.port,
            },
        })
    }

    pub fn parse_many(inputs: Vec<String>) -> Result<Vec<Self>, String> {
        inputs.into_iter().map(|s| ProxyMap::parse(&s)).collect()
    }

    /// Parse one side of mapping.
    /// If `default_proto` is None, detect protocol from input; otherwise
    /// inherit.
    pub fn parse_side(
        input: &str,
        default_proto: Option<ProtocolType>,
    ) -> Result<(ProtocolType, HostPort), String> {
        // Determine protocol and strip prefix
        let (proto, rest) = if let Some(idx) = input.find("://") {
            let scheme = &input[..idx];
            let after = &input[idx + 3..];
            (ProtocolType::from_str(scheme), after)
        } else if let Some(idx) = input.find(':') {
            let prefix = &input[..idx];
            let suffix = &input[idx + 1..];
            if default_proto.is_none()
                && ProtocolType::is_known(prefix)
                && !suffix.contains('.')
            {
                // prefix is protocol name, and suffix not a hostname with dot
                (ProtocolType::from_str(prefix), suffix)
            } else {
                (default_proto.unwrap_or(ProtocolType::Tcp), input)
            }
        } else {
            (default_proto.unwrap_or(ProtocolType::Tcp), input)
        };

        // Split host and port
        let (host, port_str) = if let Some(idx) = rest.rfind(':') {
            let h = &rest[..idx];
            let p = &rest[idx + 1..];
            (if h.is_empty() { "0.0.0.0" } else { h }, p)
        } else {
            // no colon: entire rest is port
            ("0.0.0.0", rest)
        };
        let port: u16 = port_str
            .parse()
            .map_err(|e| format!("Invalid port '{}': {}", port_str, e))?;

        Ok((proto, HostPort { host: host.to_string(), port }))
    }

    fn get_tcp_proxy_address(socket_addr: SocketAddr) -> ProxyAddrConfig {
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

    pub fn filter_tcp(maps: Vec<Self>) -> Vec<Self> {
        maps.into_iter()
            .filter(|m| m.proto == Some(ProtocolType::Tcp))
            .collect()
    }

    pub fn filter_http(maps: Vec<Self>) -> Vec<Self> {
        maps.into_iter()
            .filter(|m| {
                m.proto == Some(ProtocolType::Http)
                    || m.proto == Some(ProtocolType::Https)
            })
            .collect()
    }
}

/// Protocol types supported by proxy
impl ProtocolType {
    /// Create ProtocolType from scheme string
    pub fn from_str(s: &str) -> ProtocolType {
        match s.to_lowercase().as_str() {
            "tcp" => ProtocolType::Tcp,
            "http" => ProtocolType::Http,
            "https" => ProtocolType::Https,
            "psql" => ProtocolType::Psql,
            "psqls" => ProtocolType::Psqls,
            _ => ProtocolType::None,
        }
    }

    /// Check if a string matches a known protocol
    pub fn is_known(s: &str) -> bool {
        matches!(
            s.to_lowercase().as_str(),
            "tcp" | "http" | "https" | "psql" | "psqls"
        )
    }
}
