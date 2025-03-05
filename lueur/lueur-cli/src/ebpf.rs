#[cfg(all(
    target_os = "linux",
    any(feature = "stealth", feature = "stealth-auto-build")
))]
use std::net::IpAddr;
use std::net::Ipv4Addr;
use std::process;

use aya::Pod;
use aya::maps::HashMap;
use aya::programs::CgroupAttachMode;
use aya::programs::CgroupSockAddr;
use aya::programs::CgroupSockopt;
use aya::programs::SockOps;
use aya::programs::tc;
use local_ip_address::list_afinet_netifas;
use nix::net::if_::if_nametoindex;
use rand::Rng;

use crate::types::EbpfProxyAddrConfig;
use crate::types::ProxyAddrConfig;

#[repr(C)]
#[derive(Clone, Copy)]
pub struct EbpfConfig {
    pub proxy_ip: u32,      // IPv4 address in network byte order
    pub proxy_ifindex: u32, // Network interface index for redirection
    pub proxy_port: u16,    // Proxy port in network byte order
}

#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct EbpfProxyConfig {
    pub target_proc_name: [u8; 16], /* Only intercept traffic from this
                                     * process (if nonzero) */
    pub proxy_pid: u32, // Do not intercept traffic from the proxy itself

    // IPv4 proxy fields:
    pub proxy_ip4: u32, // Proxy IP in network byte order
    pub proxy_port4: u16, /* Proxy port (network byte order) */

                        /* IPv6 proxy fields:
                         *pub proxy_ip6: [u8; 16],
                         *pub proxy_port6: u16, */
}

unsafe impl Pod for EbpfConfig {}
unsafe impl Pod for EbpfProxyConfig {}

pub fn get_ebpf_proxy(
    proxy_nic_config: &ProxyAddrConfig,
) -> anyhow::Result<EbpfProxyAddrConfig> {
    let proxy_ip4: u32 = proxy_nic_config.proxy_ip.into();
    let proxy_ip6 = ipv4_to_mapped_ipv6_bytes(proxy_ip4);

    let interfaces = get_all_interfaces()?;
    let proxy_iface =
        find_interface_by_ip(&interfaces, proxy_ip4.into()).unwrap();
    let iface_name = proxy_iface.0.clone();

    let ebpf_proxy_port: u16 = rand::thread_rng().gen_range(1024..=65535);

    Ok(EbpfProxyAddrConfig {
        ip: proxy_iface.1.clone(),
        port: ebpf_proxy_port,
        ifname: iface_name,
    })
}

pub fn install_and_run(
    ebpf: &mut aya::Ebpf,
    ebpf_proxy_config: &EbpfProxyAddrConfig,
    ebpf_process: String,
) -> anyhow::Result<()> {
    let proxy_ip4 = ebpf_proxy_config.ip;
    let ebpf_proxy_port = ebpf_proxy_config.port;
    let iface = ebpf_proxy_config.ifname.as_str();

    tracing::debug!("Using interface {} {}", proxy_ip4, iface);

    for (name, map) in ebpf.maps() {
        tracing::info!("found map `{}`", name,);
    }

    // Initialize the shared map for proxy configuration.
    let ebpf_map: &mut aya::maps::Map = ebpf
        .map_mut("PROXY_CONFIG")
        .expect("Failed to create PROXY_CONFIG ebpf map");
    let mut proxy_config_map: HashMap<_, u32, EbpfProxyConfig> =
        HashMap::try_from(ebpf_map).unwrap();

    let mut config = EbpfProxyConfig {
        target_proc_name: [0; 16],
        proxy_pid: process::id(),
        proxy_ip4: proxy_ip4.into(),
        proxy_port4: u16::to_be(ebpf_proxy_port),
        //proxy_ip6: proxy_ip6,
        //proxy_port6: u16::to_be(proxy_nic_config.proxy_port),
    };

    let proc_name = ebpf_process.as_bytes();
    for (i, b) in proc_name.iter().enumerate() {
        config.target_proc_name[i] = *b;
    }

    proxy_config_map.insert(0, config, 0)?;

    tracing::info!(
        "Shared map PROXY_CONFIG initialized {}:{} [PID: {}]",
        u32::from_be(config.proxy_ip4),
        u16::from_be(config.proxy_port4),
        config.proxy_pid
    );

    let _ = tc::qdisc_add_clsact(&iface);

    // Attach the cgroup_sock program to a cgroup.
    // This program will tag connections for the target process.
    let cgroup_path = "/sys/fs/cgroup/"; // Adjust as needed.
    let cgroup = std::fs::File::open(&cgroup_path).unwrap();

    let _ = tc::qdisc_add_clsact(&iface);

    let cgroup_prog_v4: &mut CgroupSockAddr =
        ebpf.program_mut("cg_connect4").unwrap().try_into()?;
    match cgroup_prog_v4.load() {
        Ok(_) => tracing::debug!("cg_connect4 program attached"),
        Err(e) => tracing::error!("cg_connect4 program failed to load {:?}", e),
    };
    cgroup_prog_v4.attach(&cgroup, CgroupAttachMode::Single).unwrap();

    // Attach the sock_ops program.
    let sock_ops: &mut SockOps =
        ebpf.program_mut("cg_sock_ops").unwrap().try_into()?;
    match sock_ops.load() {
        Ok(_) => tracing::debug!("cg_sock_ops program attached"),
        Err(e) => tracing::error!("cg_sock_ops program failed to load {:?}", e),
    };
    sock_ops.attach(&cgroup, CgroupAttachMode::Single).unwrap();

    let opt_prog: &mut CgroupSockopt =
        ebpf.program_mut("cg_sock_opt").unwrap().try_into()?;
    match opt_prog.load() {
        Ok(_) => tracing::debug!("cg_sock_opt program attached"),
        Err(e) => tracing::error!("cg_sock_opt program failed to load {:?}", e),
    };
    opt_prog.attach(&cgroup, CgroupAttachMode::Single).unwrap();

    /*
        let _ = tc::qdisc_add_clsact(&iface);
        let cgroup_prog: &mut CgroupSockAddr = ebpf.program_mut("tag_connection_v4").unwrap().try_into()?;

        match cgroup_prog.load() {
            Ok(_) => tracing::debug!("tag_connection_v4 program attached"),
            Err(e) => tracing::error!("tag_connection_v4 program failed to load {:?}", e),
        };

        cgroup_prog.attach(
            &cgroup,
            CgroupAttachMode::Single
        ).unwrap();

        let cgroup_prog: &mut CgroupSockAddr = ebpf.program_mut("tag_connection_v6").unwrap().try_into()?;

        match cgroup_prog.load() {
            Ok(_) => tracing::debug!("tag_connection_v6 program attached"),
            Err(e) => tracing::error!("tag_connection_v6 program failed to load {:?}", e),
        };

        cgroup_prog.attach(
            &cgroup,
            CgroupAttachMode::Single
        ).unwrap();


        let sock_ops: &mut SockOps = ebpf.program_mut("handle_sock_ops")
        .unwrap()
        .try_into()?;
        match sock_ops.load() {
            Ok(_) => tracing::debug!("handle_sock_ops program attached"),
            Err(e) => tracing::error!("handle_sock_ops program failed to load {:?}", e),
        };
        sock_ops.attach(&cgroup, CgroupAttachMode::Single).unwrap();


        // Attach TC classifier for egress.
        // Replace "eth0" with the appropriate network interface.
        let tc_egress: &mut SchedClassifier = ebpf.program_mut("redirect_to_proxy").unwrap().try_into()?;
        match tc_egress.load() {
            Ok(_) => tracing::debug!("redirect_to_proxy egress program loaded"),
            Err(e) => tracing::error!("redirect_to_proxy egress program failed to load{:?}", e),
        };

        match tc_egress.attach(iface, TcAttachType::Egress) {
            Ok(_) => tracing::debug!("redirect_to_proxy egress program attached"),
            Err(e) => {
                tracing::error!("redirect_to_proxy egress program failed to be attached {:?}", e)
            }
        };

        // Attach TC classifier for ingress.
        let tc_ingress: &mut SchedClassifier = ebpf.program_mut("restore_destination").unwrap().try_into()?;
        match tc_ingress.load() {
            Ok(_) => tracing::debug!("restore_destination egress program loaded"),
            Err(e) => tracing::error!("restore_destination egress program failed to load{:?}", e),
        };

        match tc_ingress.attach(iface, TcAttachType::Ingress) {
            Ok(_) => tracing::debug!("restore_destination egress program attached"),
            Err(e) => {
                tracing::error!("restore_destination egress program failed to be attached {:?}", e)
            }
        };
    */

    tracing::debug!("ebpf programs installed");

    Ok(())
}

///
/// -------------------- Private functions -----------------------------------

// Helper function to get interface index from name.
fn get_ifindex(interface_name: &str) -> Result<u32, String> {
    Ok(if_nametoindex(interface_name).map_err(|e| {
        format!(
            "Failed to get ifindex for interface '{}': {}",
            interface_name, e
        )
    })? as u32)
}

// Function to find interface by IP.
fn find_interface_by_ip(
    interfaces: &[(String, Ipv4Addr)],
    ip: Ipv4Addr,
) -> Option<&(String, Ipv4Addr)> {
    interfaces.iter().find(|iface| iface.1 == ip)
}

fn get_all_interfaces() -> anyhow::Result<Vec<(String, Ipv4Addr)>> {
    let interfaces: Vec<(String, IpAddr)> = list_afinet_netifas()
        .map_err(|e| format!("Failed to get network interfaces: {}", e))
        .unwrap();

    let interfaces: Vec<(String, Ipv4Addr)> = interfaces
        .into_iter()
        .filter_map(|(name, addr)| {
            if let IpAddr::V4(ipv4) = addr { Some((name, ipv4)) } else { None }
        })
        .collect();

    Ok(interfaces)
}

/// Converts a host‐order `u32` IPv4 address into an IPv4‐mapped IPv6 `[u8;
/// 16]`.
///
/// For example, `0xC0A80001` (192.168.0.1) becomes `::ffff:192.168.0.1`
/// i.e. `[0,0,0,0,0,0,0,0,0,0,0xff,0xff,192,168,0,1]`.
#[inline]
pub fn ipv4_to_mapped_ipv6_bytes(ip4_host: u32) -> [u8; 16] {
    // Convert the host-order IPv4 to big-endian bytes
    let ip4_be = ip4_host.to_be();
    let ip4_bytes = ip4_be.to_be_bytes();

    // Construct the 16-byte array for ::ffff:x.x.x.x
    let mut v6 = [0u8; 16];
    // The mapped IPv4 prefix is 0000:0000:0000:0000:0000:FFFF
    v6[10] = 0xff;
    v6[11] = 0xff;
    // Copy the 4 IPv4 bytes into the last 4 bytes of the IPv6 address
    v6[12] = ip4_bytes[0];
    v6[13] = ip4_bytes[1];
    v6[14] = ip4_bytes[2];
    v6[15] = ip4_bytes[3];

    v6
}
