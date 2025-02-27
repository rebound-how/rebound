use std::fmt;
use std::net::IpAddr;
use std::net::Ipv4Addr;
use std::net::SocketAddr;

use local_ip_address::list_afinet_netifas;
use nix::net::if_::if_nametoindex;

/// Structure to hold the final configuration.
#[derive(Debug)]
pub struct ProxyEbpfConfig {
    pub proxy_ip: Ipv4Addr,
    pub proxy_port: u16,
    pub proxy_ifindex: u32,
    pub ebpf_ifindex: u32,
    pub ebpf_ifname: String,
}

impl ProxyEbpfConfig {
    pub fn proxy_address(&self) -> String {
        format!("{}:{}", self.proxy_ip, self.proxy_port)
    }
}

impl fmt::Display for ProxyEbpfConfig {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "Proxy Configuration:\n\
             ---------------------\n\
             Proxy IP          : {}\n\
             Proxy Port        : {}\n\
             Proxy Ifindex     : {}\n\
             eBPF Ifindex      : {}\n\
             eBPF Interface Name: {}",
            self.proxy_ip,
            self.proxy_port,
            self.proxy_ifindex,
            self.ebpf_ifindex,
            self.ebpf_ifname
        )
    }
}

/// Determines the proxy address, port, and eBPF interface index based on CLI
/// arguments.
///
/// # Arguments
///
/// * `proxy_address` - Optional proxy address in the format "IP:PORT".
/// * `ebpf_interface` - Optional network interface name for eBPF program.
///
/// # Returns
///
/// * `Ok(ProxyEbpfConfig)` on success.
/// * `Err(String)` with an error message on failure.
pub fn determine_proxy_and_ebpf_config(
    proxy_address: Option<String>,
    ebpf_interface: Option<String>,
) -> Result<ProxyEbpfConfig, String> {
    let proxy_address = proxy_address.as_deref();
    let ebpf_interface = ebpf_interface.as_deref();

    // Retrieve all network interfaces and their addresses.
    let interfaces: Vec<(String, IpAddr)> = list_afinet_netifas()
        .map_err(|e| format!("Failed to get network interfaces: {}", e))?;
    let interfaces: Vec<(String, Ipv4Addr)> = interfaces
        .into_iter()
        .filter_map(|(name, addr)| {
            if let IpAddr::V4(ipv4) = addr { Some((name, ipv4)) } else { None }
        })
        .collect();

    // Initialize variables for proxy interface and eBPF interface.
    #[warn(unused_assignments)]
    let mut ebpf_ifindex: Option<u32> = None;

    // Function to find interface by IP.
    fn find_interface_by_ip(
        interfaces: &[(String, Ipv4Addr)],
        ip: Ipv4Addr,
    ) -> Option<&(String, Ipv4Addr)> {
        interfaces.iter().find(|iface| iface.1 == ip)
    }

    // Function to find the first non-loopback interface.
    fn find_first_non_loopback(
        interfaces: &[(String, Ipv4Addr)],
    ) -> Option<&(String, Ipv4Addr)> {
        interfaces.iter().find(|iface| !iface.1.is_loopback())
    }

    // Function to find interface by name.
    fn find_interface_by_name<'a>(
        interfaces: &'a [(String, Ipv4Addr)],
        name: &str,
    ) -> Option<&'a (String, Ipv4Addr)> {
        interfaces.iter().find(|iface| iface.0 == name)
    }

    // Helper function to get interface index from name.
    fn get_ifindex(interface_name: &str) -> Result<u32, String> {
        Ok(if_nametoindex(interface_name).map_err(|e| {
            format!(
                "Failed to get ifindex for interface '{}': {}",
                interface_name, e
            )
        })? as u32)
    }

    // Case 5: Both --ebpf-interface and --proxy-address are provided.
    if let (Some(proxy_addr_str), Some(ebpf_iface_name)) =
        (proxy_address, ebpf_interface)
    {
        // Parse the proxy address.
        let socket_addr: SocketAddr = proxy_addr_str.parse().map_err(|e| {
            format!("Invalid proxy address '{}': {}", proxy_addr_str, e)
        })?;
        let sock_proxy_ip = socket_addr.ip();
        let proxy_port = socket_addr.port();
        let proxy_idx;

        // Determine if proxy is loopback.
        let proxy_ip = match sock_proxy_ip {
            IpAddr::V4(ipv4) => ipv4,
            IpAddr::V6(_ipv6) => {
                return Err("IPV6 addresses are not supported".to_string());
            }
        };

        if proxy_ip.is_loopback() {
            // Proxy is on loopback; eBPF should be on a non-loopback interface.
            // Find eBPF interface by name.
            let (ebpf_iface_name, _ebpf_iface) =
                find_interface_by_name(&interfaces, ebpf_iface_name)
                    .ok_or_else(|| {
                        format!(
                            "Specified eBPF interface '{}' not found",
                            ebpf_iface_name
                        )
                    })?;

            // Get eBPF interface index.
            let ebpf_idx = get_ifindex(ebpf_iface_name)?;
            ebpf_ifindex = Some(ebpf_idx);

            // Ensure proxy is not on the same interface.
            // Since proxy is on loopback, no conflict.
            // Set proxy to loopback.
            let (proxy_iface_name, _proxy_iface) =
                find_interface_by_ip(&interfaces, proxy_ip).ok_or_else(
                    || {
                        format!(
                            "Proxy IP address '{}' not found on any interface",
                            proxy_ip
                        )
                    },
                )?;

            // Get proxy interface index.
            proxy_idx = get_ifindex(proxy_iface_name)?;
        } else {
            // Proxy is on a real NIC; ensure eBPF is not on the same NIC.
            // Find the interface that has the proxy IP.
            let (proxy_iface_name, _proxy_iface) =
                find_interface_by_ip(&interfaces, proxy_ip).ok_or_else(
                    || {
                        format!(
                            "Proxy IP address '{}' not found on any interface",
                            proxy_ip
                        )
                    },
                )?;

            // Get proxy interface index.
            proxy_idx = get_ifindex(proxy_iface_name)?;

            // Now, ensure eBPF interface is different from proxy interface.
            let _ebpf_iface =
                find_interface_by_name(&interfaces, ebpf_iface_name)
                    .ok_or_else(|| {
                        format!(
                            "Specified eBPF interface '{}' not found",
                            ebpf_iface_name
                        )
                    })?;

            // Check if eBPF interface is same as proxy interface.
            /*if ebpf_iface_name == proxy_iface_name {
                return Err(format!(
                    "Conflict: Both eBPF program and proxy are bound to the same interface '{}'",
                    ebpf_iface_name
                ));
            }*/

            // Get eBPF interface index.
            let ebpf_idx = get_ifindex(ebpf_iface_name)?;
            ebpf_ifindex = Some(ebpf_idx);
        }

        // Final validation: Ensure that proxy and eBPF are not on the same
        // interface.
        /*if let (Some(proxy_idx_val), Some(ebpf_idx_val)) = (proxy_ifindex, ebpf_ifindex) {
            if proxy_idx_val == ebpf_idx_val {
                return Err(format!(
                    "Proxy and eBPF program cannot be bound to the same network interface (ifindex {})",
                    proxy_idx_val
                ));
            }
        }*/

        return Ok(ProxyEbpfConfig {
            proxy_ip,
            proxy_port,
            proxy_ifindex: proxy_idx,
            ebpf_ifindex: ebpf_ifindex.ok_or_else(|| {
                "Failed to determine eBPF interface index".to_string()
            })?,
            ebpf_ifname: ebpf_iface_name.to_string(),
        });
    }

    // Scenario 2: --proxy-address 127.0.0.1:8080
    if let Some(proxy_addr_str) = proxy_address {
        // If ebpf_interface is not provided, proceed.
        if ebpf_interface.is_none() {
            // Parse the proxy address.
            let socket_addr: SocketAddr =
                proxy_addr_str.parse().map_err(|e| {
                    format!("Invalid proxy address '{}': {}", proxy_addr_str, e)
                })?;
            let sock_proxy_ip = socket_addr.ip();
            let proxy_port = socket_addr.port();

            // Determine if proxy is loopback.
            let proxy_ip = match sock_proxy_ip {
                IpAddr::V4(ipv4) => ipv4,
                IpAddr::V6(_ipv6) => {
                    return Err("IPV6 addresses are not supported".to_string());
                }
            };

            if proxy_ip.is_loopback() {
                // Proxy is on loopback; eBPF should be on a non-loopback
                // interface. Choose the first non-loopback
                // interface.
                let (non_loopback_iface_name, _non_loopback_iface) = find_first_non_loopback(&interfaces)
                    .ok_or_else(|| "No non-loopback network interfaces found for eBPF program".to_string())?;

                let ebpf_idx = get_ifindex(non_loopback_iface_name)?;
                ebpf_ifindex = Some(ebpf_idx);

                let (proxy_iface_name, _proxy_iface) = find_interface_by_ip(
                    &interfaces,
                    proxy_ip,
                )
                .ok_or_else(|| {
                    format!(
                        "Proxy IP address '{}' not found on any interface",
                        proxy_ip
                    )
                })?;

                // Get proxy interface index.
                let proxy_idx = get_ifindex(proxy_iface_name)?;

                return Ok(ProxyEbpfConfig {
                    proxy_ip,
                    proxy_port,
                    proxy_ifindex: proxy_idx,
                    ebpf_ifindex: ebpf_ifindex.ok_or_else(|| {
                        "Failed to determine eBPF interface index".to_string()
                    })?,
                    ebpf_ifname: non_loopback_iface_name.to_string(),
                });
            } else {
                // Proxy is on a real NIC; ensure eBPF is on a different NIC.
                // Find the interface that has the proxy IP.
                let (proxy_iface_name, _proxy_iface) = find_interface_by_ip(
                    &interfaces,
                    proxy_ip,
                )
                .ok_or_else(|| {
                    format!(
                        "Proxy IP address '{}' not found on any interface",
                        proxy_ip
                    )
                })?;

                let proxy_idx = get_ifindex(proxy_iface_name)?;

                // Choose another non-loopback interface for eBPF.
                let (ebpf_iface_name, _ebpf_iface) = interfaces.iter().find(|iface| iface.0 != *proxy_iface_name && !iface.1.is_loopback())
                    .ok_or_else(|| "No alternative non-loopback network interface found for eBPF program".to_string())?;

                let ebpf_idx = get_ifindex(ebpf_iface_name)?;
                ebpf_ifindex = Some(ebpf_idx);

                // Ensure eBPF interface is different from proxy interface.
                if proxy_iface_name == ebpf_iface_name {
                    return Err(format!(
                        "Proxy and eBPF program cannot be bound to the same network interface '{}'",
                        ebpf_iface_name
                    ));
                }

                return Ok(ProxyEbpfConfig {
                    proxy_ip,
                    proxy_port,
                    proxy_ifindex: proxy_idx,
                    ebpf_ifindex: ebpf_ifindex.ok_or_else(|| {
                        "Failed to determine eBPF interface index".to_string()
                    })?,
                    ebpf_ifname: ebpf_iface_name.to_string(),
                });
            }
        }
    }

    // Scenario 4: --ebpf-interface eth0
    if let Some(ebpf_iface_name) = ebpf_interface {
        // If proxy_address is not provided, proceed.
        if proxy_address.is_none() {
            // Choose proxy to bind to loopback.
            let proxy_ip = Ipv4Addr::new(127, 0, 0, 1);
            let proxy_port = 8080;

            // Find the specified eBPF interface.
            let _ebpf_iface =
                find_interface_by_name(&interfaces, ebpf_iface_name)
                    .ok_or_else(|| {
                        format!(
                            "Specified eBPF interface '{}' not found",
                            ebpf_iface_name
                        )
                    })?;

            let ebpf_idx = get_ifindex(ebpf_iface_name)?;
            ebpf_ifindex = Some(ebpf_idx);

            let (proxy_iface_name, _proxy_iface) =
                find_interface_by_ip(&interfaces, proxy_ip).ok_or_else(
                    || {
                        format!(
                            "Proxy IP address '{}' not found on any interface",
                            proxy_ip
                        )
                    },
                )?;

            // Get proxy interface index.
            let proxy_idx = get_ifindex(proxy_iface_name)?;

            return Ok(ProxyEbpfConfig {
                proxy_ip,
                proxy_port,
                proxy_ifindex: proxy_idx,
                ebpf_ifindex: ebpf_ifindex.ok_or_else(|| {
                    "Failed to determine eBPF interface index".to_string()
                })?,
                ebpf_ifname: ebpf_iface_name.to_string(),
            });
        }
    }

    // Scenario 3: --proxy-address 192.168.1.34:8080
    if let Some(proxy_addr_str) = proxy_address {
        if ebpf_interface.is_none() {
            // Parse the proxy address.
            let socket_addr: SocketAddr =
                proxy_addr_str.parse().map_err(|e| {
                    format!("Invalid proxy address '{}': {}", proxy_addr_str, e)
                })?;
            let sock_proxy_ip = socket_addr.ip();
            let proxy_port = socket_addr.port();

            // Determine if proxy is loopback.
            let proxy_ip = match sock_proxy_ip {
                IpAddr::V4(ipv4) => ipv4,
                IpAddr::V6(_) => {
                    return Err("IPV6 addresses are not supported".to_string());
                }
            };

            if proxy_ip.is_loopback() {
                // Proxy is on loopback; eBPF should be on a non-loopback
                // interface.
                let (non_loopback_iface_name, _non_loopback_iface) = find_first_non_loopback(&interfaces)
                    .ok_or_else(|| "No non-loopback network interfaces found for eBPF program".to_string())?;

                let ebpf_idx = get_ifindex(non_loopback_iface_name)?;
                ebpf_ifindex = Some(ebpf_idx);

                // Proxy is on loopback; no proxy_ifindex needed.
                let (proxy_iface_name, _proxy_iface) = find_interface_by_ip(
                    &interfaces,
                    proxy_ip,
                )
                .ok_or_else(|| {
                    format!(
                        "Proxy IP address '{}' not found on any interface",
                        proxy_ip
                    )
                })?;

                // Get proxy interface index.
                let proxy_idx = get_ifindex(proxy_iface_name)?;

                return Ok(ProxyEbpfConfig {
                    proxy_ip,
                    proxy_port,
                    proxy_ifindex: proxy_idx,
                    ebpf_ifindex: ebpf_ifindex.ok_or_else(|| {
                        "Failed to determine eBPF interface index".to_string()
                    })?,
                    ebpf_ifname: non_loopback_iface_name.to_string(),
                });
            } else {
                // Proxy is on a real NIC; ensure eBPF is on a different NIC.
                // Find the interface that has the proxy IP.
                let (proxy_iface_name, _proxy_iface) = find_interface_by_ip(
                    &interfaces,
                    proxy_ip,
                )
                .ok_or_else(|| {
                    format!(
                        "Proxy IP address '{}' not found on any interface",
                        proxy_ip
                    )
                })?;

                let proxy_idx = get_ifindex(proxy_iface_name)?;

                // Choose another non-loopback interface for eBPF.
                let (ebpf_iface_name, _ebpf_iface) = interfaces.iter().find(|iface| iface.0 != *proxy_iface_name && !iface.1.is_loopback())
                    .ok_or_else(|| "No alternative non-loopback network interface found for eBPF program".to_string())?;

                let ebpf_idx = get_ifindex(ebpf_iface_name)?;
                ebpf_ifindex = Some(ebpf_idx);

                // Ensure eBPF interface is different from proxy interface.
                if proxy_iface_name == ebpf_iface_name {
                    return Err(format!(
                        "Proxy and eBPF program cannot be bound to the same network interface '{}'",
                        ebpf_iface_name
                    ));
                }

                return Ok(ProxyEbpfConfig {
                    proxy_ip,
                    proxy_port,
                    proxy_ifindex: proxy_idx,
                    ebpf_ifindex: ebpf_ifindex.ok_or_else(|| {
                        "Failed to determine eBPF interface index".to_string()
                    })?,
                    ebpf_ifname: ebpf_iface_name.to_string(),
                });
            }
        }
    }

    // Scenario 1: No arguments provided.
    if proxy_address.is_none() && ebpf_interface.is_none() {
        // Default proxy address: 127.0.0.1:8080
        let proxy_ip = Ipv4Addr::new(127, 0, 0, 1);
        let proxy_port = 8080;

        // Choose the first non-loopback interface for eBPF.
        let (non_loopback_iface_name, _non_loopback_iface) =
            find_first_non_loopback(&interfaces).ok_or_else(|| {
                "No non-loopback network interfaces found for eBPF program"
                    .to_string()
            })?;

        let ebpf_idx = get_ifindex(non_loopback_iface_name)?;
        ebpf_ifindex = Some(ebpf_idx);

        // Proxy is on loopback; no proxy_ifindex needed.
        let (proxy_iface_name, _proxy_iface) =
            find_interface_by_ip(&interfaces, proxy_ip).ok_or_else(|| {
                format!(
                    "Proxy IP address '{}' not found on any interface",
                    proxy_ip
                )
            })?;

        // Get proxy interface index.
        let proxy_idx = get_ifindex(proxy_iface_name)?;

        return Ok(ProxyEbpfConfig {
            proxy_ip,
            proxy_port,
            proxy_ifindex: proxy_idx,
            ebpf_ifindex: ebpf_ifindex.ok_or_else(|| {
                "Failed to determine eBPF interface index".to_string()
            })?,
            ebpf_ifname: non_loopback_iface_name.to_string(),
        });
    }

    // Scenario 5 and other unspecified cases.
    // If none of the above scenarios matched, return an error.
    Err("Invalid combination of arguments".to_string())
}
