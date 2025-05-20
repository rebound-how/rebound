#[cfg(all(
    target_os = "linux",
    any(feature = "stealth", feature = "stealth-auto-build")
))]
use std::env;
use std::net::IpAddr;
use std::net::Ipv4Addr;
use std::path::PathBuf;
use std::process;

use aya::Ebpf;
use aya::Pod;
use aya::maps::HashMap;
use aya::programs::CgroupAttachMode;
use aya::programs::CgroupSockAddr;
use aya::programs::CgroupSockopt;
use aya::programs::SockOps;
use aya::programs::tc;
use local_ip_address::list_afinet_netifas;
use rand::Rng;

use crate::cli::StealthCommandCommon;
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
    ebpf_proxy_iface: Option<String>,
    ebpf_proxy_ip: Option<String>,
    ebpf_proxy_port: Option<u16>,
) -> anyhow::Result<Option<EbpfProxyAddrConfig>> {
    let interfaces = get_all_interfaces()?;
    if interfaces.is_empty() {
        tracing::warn!(
            "Could not find any suitable interfaces to bind our ebpf program to"
        );
        return Ok(None);
    }

    let iface_name;
    let iface_ip: Ipv4Addr;

    if let Some(iface) = ebpf_proxy_iface {
        let proxy_iface = match find_ip_by_interface(&interfaces, iface) {
            Some(it) => it,
            None => return Ok(None),
        };
        iface_ip = proxy_iface.1;
        iface_name = proxy_iface.0.clone();
    } else if let Some(ebpf_ip) = ebpf_proxy_ip {
        let proxy_iface =
            match find_interface_by_ip(&interfaces, ebpf_ip.parse()?) {
                Some(it) => it,
                None => return Ok(None),
            };
        iface_ip = proxy_iface.1;
        iface_name = proxy_iface.0.clone();
    } else {
        let proxy_ip4: u32 = proxy_nic_config.proxy_ip.into();

        if Ipv4Addr::from(proxy_ip4) == Ipv4Addr::new(0, 0, 0, 0) {
            let proxy_iface = find_non_loopback_interface(&interfaces).unwrap();
            iface_ip = proxy_iface.1; // Ipv4Addr::new(0, 0, 0, 0);
            iface_name = proxy_iface.0.clone();
        } else {
            let proxy_iface =
                match find_interface_by_ip(&interfaces, proxy_ip4.into()) {
                    Some(it) => it,
                    None => return Ok(None),
                };
            iface_ip = proxy_iface.1;
            iface_name = proxy_iface.0.clone();
        }
    }

    let port: u16 = match ebpf_proxy_port {
        Some(p) => p,
        None => rand::rng().random_range(1024..=65535),
    };

    tracing::debug!("eBPF proxy detected address {}:{}", iface_ip, port);

    Ok(Some(EbpfProxyAddrConfig { ip: iface_ip, port, ifname: iface_name }))
}

pub fn install_and_run(
    ebpf: &mut aya::Ebpf,
    ebpf_proxy_config: &EbpfProxyAddrConfig,
    ebpf_process: String,
) -> anyhow::Result<()> {
    let proxy_ip4 = ebpf_proxy_config.ip;
    let iface = ebpf_proxy_config.ifname.as_str();

    tracing::debug!("Using interface {} {}", proxy_ip4, iface);

    for (name, ..) in ebpf.maps() {
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
        proxy_ip4: ebpf_proxy_config.ip.into(),
        proxy_port4: u16::to_be(ebpf_proxy_config.port),
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

    let _ = tc::qdisc_add_clsact(iface);

    // Attach the cgroup_sock program to a cgroup.
    // This program will tag connections for the target process.
    let cgroup_path = "/sys/fs/cgroup/"; // Adjust as needed.
    let cgroup = std::fs::File::open(cgroup_path).unwrap();

    let _ = tc::qdisc_add_clsact(iface);

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

    tracing::debug!("ebpf programs installed");

    Ok(())
}

//
// -------------------- Private functions -----------------------------------
//

// Function to find interface by IP.
fn find_interface_by_ip(
    interfaces: &[(String, Ipv4Addr)],
    ip: Ipv4Addr,
) -> Option<&(String, Ipv4Addr)> {
    interfaces.iter().find(|iface| iface.1 == ip)
}

// Function to find non loopback interface
fn find_non_loopback_interface(
    interfaces: &[(String, Ipv4Addr)],
) -> Option<&(String, Ipv4Addr)> {
    interfaces.iter().find(|iface| !iface.1.is_loopback())
}

// Function to find the IP attached to an IP
fn find_ip_by_interface(
    interfaces: &[(String, Ipv4Addr)],
    iface_name: String,
) -> Option<&(String, Ipv4Addr)> {
    interfaces.iter().find(|iface| iface.0 == iface_name)
}

fn get_all_interfaces() -> anyhow::Result<Vec<(String, Ipv4Addr)>> {
    let interfaces: Vec<(String, IpAddr)> = list_afinet_netifas()
        .map_err(|e| tracing::error!("Failed to get network interfaces: {}", e))
        .unwrap();

    let interfaces: Vec<(String, Ipv4Addr)> = interfaces
        .into_iter()
        .filter_map(|(name, addr)| {
            if let IpAddr::V4(ipv4) = addr { Some((name, ipv4)) } else { None }
        })
        .collect();

    Ok(interfaces)
}

#[cfg(all(target_os = "linux", feature = "stealth-auto-build"))]
pub fn initialize_stealth(
    cli: &ProxyAwareCommandCommon,
    ebpf_proxy_config: &EbpfProxyAddrConfig,
) -> Option<Ebpf> {
    let upstream_hosts = cli.upstream_hosts.clone();

    #[allow(unused_variables)]
    let ebpf_guard = match cli.ebpf {
        true => {
            let mut bpf = aya::Ebpf::load(aya::include_bytes_aligned!(
                concat!(env!("OUT_DIR"), "/fault-ebpf")
            ))
            .unwrap();

            if let Err(e) = aya_log::EbpfLogger::init(&mut bpf) {
                tracing::warn!("failed to initialize eBPF logger: {}", e);
            }

            let _ = ebpf::install_and_run(&mut bpf, &ebpf_proxy_config);

            tracing::info!("Ebpf has been loaded");

            Some(bpf)
        }
        false => None,
    };

    ebpf_guard
}

#[cfg(all(target_os = "linux", feature = "stealth"))]
pub fn initialize_stealth(
    stealth_options: &StealthCommandCommon,
    ebpf_proxy_config: &EbpfProxyAddrConfig,
) -> Option<Ebpf> {
    let proc_name = stealth_options.ebpf_process_name.clone().unwrap();

    #[allow(unused_variables)]
    let ebpf_guard = match stealth_options.ebpf {
        true => {
            let cargo_bin_dir = get_programs_bin_dir(stealth_options);
            if cargo_bin_dir.is_none() {
                tracing::warn!(
                    "No cargo bin directory could be detected, please set CARGO_HOME"
                );
                return None;
            }
            tracing::info!(
                "Loading ebpf programs from bin directory {:?}",
                cargo_bin_dir
            );

            let bin_dir = cargo_bin_dir.unwrap();
            let programs_path = bin_dir.join("fault-ebpf");
            if !programs_path.exists() {
                tracing::error!(
                    "Missing the fault ebpf programs. Please install them."
                );
                return None;
            }

            tracing::info!("Loading ebpf programs from {:?}", programs_path);

            let mut bpf = aya::Ebpf::load_file(programs_path).unwrap();

            if let Err(e) = aya_log::EbpfLogger::init(&mut bpf) {
                tracing::warn!("failed to initialize eBPF logger: {}", e);
            }

            let _ = install_and_run(&mut bpf, ebpf_proxy_config, proc_name);

            tracing::info!("Ebpf has been loaded");

            Some(bpf)
        }
        false => None,
    };

    ebpf_guard
}

#[cfg(all(target_os = "linux", feature = "stealth"))]
fn get_programs_bin_dir(cli: &StealthCommandCommon) -> Option<PathBuf> {
    if let Some(programs_dir) = &cli.ebpf_programs_dir {
        let path = PathBuf::from(programs_dir);
        if path.exists() {
            return Some(path);
        }
    }

    if let Ok(cargo_home) = env::var("CARGO_HOME") {
        let mut path = PathBuf::from(cargo_home);
        path.push("bin");

        if path.exists() {
            return Some(path);
        }
    }

    // Fallback for Unix-like systems: use HOME/.cargo/bin
    #[cfg(unix)]
    {
        match env::home_dir() {
            Some(mut path) => {
                path.push(".cargo/bin");
                Some(path)
            }
            None => None,
        }
    }
}
