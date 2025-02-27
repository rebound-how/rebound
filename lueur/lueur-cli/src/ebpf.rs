use aya::Pod;
use aya::maps::Array;
use aya::maps::HashMap;
use aya::programs::SchedClassifier;
use aya::programs::TcAttachType;
use aya::programs::tc;
use reqwest::Url;

use crate::nic::ProxyEbpfConfig;

#[repr(C)]
#[derive(Clone, Copy)]
pub struct EbpfConfig {
    pub proxy_ip: u32,      // IPv4 address in network byte order
    pub proxy_ifindex: u32, // Network interface index for redirection
    pub proxy_port: u16,    // Proxy port in network byte order
}

unsafe impl Pod for EbpfConfig {}

pub fn install_and_run(
    ebpf: &mut aya::Ebpf,
    proxy_nic_config: &ProxyEbpfConfig,
    upstream_ports: Vec<String>,
) -> anyhow::Result<()> {
    // Bump the memlock rlimit. This is needed for older kernels that don't use
    // the new memcg based accounting, see https://lwn.net/Articles/837122/
    let rlim = libc::rlimit {
        rlim_cur: libc::RLIM_INFINITY,
        rlim_max: libc::RLIM_INFINITY,
    };
    let ret = unsafe { libc::setrlimit(libc::RLIMIT_MEMLOCK, &rlim) };
    if ret != 0 {
        tracing::debug!(
            "remove limit on locked memory failed, ret is: {}",
            ret
        );
    }

    let iface_name = &proxy_nic_config.ebpf_ifname;
    let iface = iface_name.as_str();

    tracing::info!("Ebpf programs bound to interface {}", iface_name);

    match tc::qdisc_add_clsact(iface_name) {
        Ok(_) => tracing::info!("qdisc attached to {}", iface_name),
        Err(e) => tracing::debug!("Attach {} to qdisc: {:?}", iface_name, e),
    };

    let ingress_program: &mut SchedClassifier =
        ebpf.program_mut("lueur_route_ingress").unwrap().try_into()?;

    match ingress_program.load() {
        Ok(_) => tracing::debug!("Ingress program attached"),
        Err(e) => tracing::error!("Ingress program failed to load {:?}", e),
    };

    match ingress_program.attach(iface, TcAttachType::Ingress) {
        Ok(_) => tracing::debug!("Ingress program loaded"),
        Err(e) => {
            tracing::error!("Ingress program failed to be attached {:?}", e)
        }
    };

    let egress_program: &mut SchedClassifier =
        ebpf.program_mut("lueur_route_egress").unwrap().try_into()?;

    match egress_program.load() {
        Ok(_) => tracing::debug!("Egress program loaded"),
        Err(e) => tracing::error!("Egress program failed to load{:?}", e),
    };

    match egress_program.attach(iface, TcAttachType::Egress) {
        Ok(_) => tracing::debug!("Egress program attached"),
        Err(e) => {
            tracing::error!("Egress program failed to be attached {:?}", e)
        }
    };

    tracing::debug!("Setting proxy port map...");
    let mut config_map = Array::<_, EbpfConfig>::try_from(
        ebpf.map_mut("PROXY_CONFIG_MAP").unwrap(),
    )?;

    tracing::info!("{}", proxy_nic_config);

    let proxy_ip: u32 = proxy_nic_config.proxy_ip.into();
    let config = EbpfConfig {
        proxy_ip: u32::to_be(proxy_ip),
        proxy_port: u16::to_be(proxy_nic_config.proxy_port),
        proxy_ifindex: u32::to_be(proxy_nic_config.proxy_ifindex),
    };
    config_map.set(0, config, 0)?;
    tracing::debug!("Proxy port map set");

    tracing::debug!("Filling upstream ports map...");
    let mut target_ports_map = HashMap::<_, u16, u8>::try_from(
        ebpf.map_mut("UPSTREAM_PORTS_MAP").unwrap(),
    )?;

    for host in upstream_ports {
        let (host, port) = parse_host_and_port(host.as_str()).unwrap();
        tracing::debug!(
            "Upstream port handled in stealth mode: {} => {}",
            host,
            port
        );
        let key = u16::to_be(port);
        target_ports_map.insert(key, 0u8, 0)?;
    }

    tracing::debug!("Upstream ports map filled");

    tracing::debug!("ebpf programs installed");

    Ok(())
}

fn parse_host_and_port(
    host: &str,
) -> Result<(String, u16), Box<dyn std::error::Error>> {
    let url_str = if host.contains("://") {
        host.to_string()
    } else {
        format!("scheme://{}", host)
    };

    let url = Url::parse(&url_str)?;

    let host = url.host_str().ok_or("Missing host")?.to_string();

    let port = url.port_or_known_default().unwrap();

    Ok((host, port))
}
