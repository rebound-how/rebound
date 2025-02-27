#![no_std]
#![no_main]

use core::mem;
use core::ptr::addr_of_mut;

use aya_ebpf::bindings::TC_ACT_OK;
use aya_ebpf::bindings::TC_ACT_PIPE;
use aya_ebpf::bindings::TC_ACT_SHOT;
use aya_ebpf::helpers::bpf_map_delete_elem;
use aya_ebpf::helpers::bpf_map_lookup_elem;
use aya_ebpf::helpers::bpf_map_update_elem;
use aya_ebpf::helpers::bpf_redirect;
use aya_ebpf::macros::classifier;
use aya_ebpf::macros::map;
use aya_ebpf::maps::Array;
use aya_ebpf::maps::HashMap;
use aya_ebpf::programs::TcContext;
use aya_log_ebpf::debug;
use aya_log_ebpf::error;
use aya_log_ebpf::info;
use aya_log_ebpf::warn;
use memoffset::offset_of;
use network_types::eth::EthHdr;
use network_types::eth::EtherType;
use network_types::ip::IpProto;
use network_types::ip::Ipv4Hdr;
use network_types::tcp::TcpHdr;

#[repr(C)]
pub struct Config {
    pub proxy_port: u16,
}

#[map(name = "UPSTREAM_PORTS_MAP")]
static mut UPSTREAM_PORTS_MAP: HashMap<u16, u8> =
    HashMap::with_max_entries(1024, 0);

/// Holds proxy configuration details: IP address, port, and interface index.
#[repr(C)]
#[derive(Clone, Copy)]
pub struct ProxyConfig {
    pub proxy_ip: u32,      // IPv4 address in network byte order
    pub proxy_ifindex: u32, // Network interface index for redirection
    pub proxy_port: u16,    // Proxy port in network byte order
}

#[repr(C)]
#[derive(Clone, Copy)]
pub struct FlowId {
    src_addr: u32,
    dst_addr: u32,
    src_port: u16,
}

/// eBPF Map Definitions
#[map(name = "PROXY_CONFIG_MAP")]
static mut PROXY_CONFIG_MAP: Array<ProxyConfig> =
    Array::<ProxyConfig>::with_max_entries(1, 0);

#[map(name = "FLOW_MAP")]
static mut FLOW_MAP: HashMap<FlowId, u16> = HashMap::with_max_entries(1024, 0);

#[classifier]
pub fn lueur_route_ingress(ctx: TcContext) -> i32 {
    let r = match try_ingress(ctx) {
        Ok(ret) => ret,
        Err(_) => TC_ACT_SHOT,
    };

    unsafe { bpf_redirect(2, 0) };

    r
}

#[classifier]
pub fn lueur_route_egress(ctx: TcContext) -> i32 {
    let r = match try_egress(ctx) {
        Ok(ret) => ret,
        Err(_) => TC_ACT_SHOT,
    };

    unsafe { bpf_redirect(1, 0) };

    r
}

#[inline(always)] // (1)
fn ptr_at_mut<T>(ctx: &TcContext, offset: usize) -> Result<*mut T, ()> {
    let start = ctx.data();
    let end = ctx.data_end();
    let len = mem::size_of::<T>();

    if start + offset + len > end {
        return Err(());
    }

    Ok((start + offset) as *mut T)
}

/// Retrieves the proxy configuration from `PROXY_CONFIG_MAP`.
fn lookup_proxy_config(ctx: &TcContext) -> Result<ProxyConfig, ()> {
    let proxy_config_ptr = unsafe {
        bpf_map_lookup_elem(
            addr_of_mut!(PROXY_CONFIG_MAP) as *mut _,
            &0u32 as *const _ as *const _,
        )
    };

    if proxy_config_ptr.is_null() {
        warn!(ctx, "Failed to lookup PROXY_CONFIG_MAP");
        return Err(());
    }

    // Copy out the configuration by value
    let config = unsafe { *(proxy_config_ptr as *const ProxyConfig) };
    Ok(config)
}

/// Checks if a given port is being tracked in `UPSTREAM_PORTS_MAP`.
fn is_tracked_upstream_port(_ctx: &TcContext, port: u16) -> bool {
    let port_ptr = unsafe {
        bpf_map_lookup_elem(
            addr_of_mut!(UPSTREAM_PORTS_MAP) as *mut _,
            &port as *const _ as *const _,
        )
    };

    !port_ptr.is_null()
}

/// Inserts or updates a flow in `FLOW_MAP`.
fn update_flow_map(
    ctx: &TcContext,
    flow_id: FlowId,
    port: u16,
) -> Result<(), ()> {
    if unsafe {
        bpf_map_update_elem(
            addr_of_mut!(FLOW_MAP) as *mut _,
            &flow_id as *const _ as *const _,
            &port as *const _ as *const _,
            0,
        )
    } != 0
    {
        debug!(ctx, "Failed to insert into FLOW_MAP");
        return Err(());
    }

    Ok(())
}

/// Modifies an IP address (source or destination) and updates the IP checksum
/// accordingly.
fn modify_ip_address(
    ctx: &mut TcContext,
    ip_check_offset: usize,
    ip_addr_offset: usize,
    old_ip: u32,
    new_ip: u32,
) -> Result<(), ()> {
    // Write the new IP address using ctx.store()
    ctx.store(ip_addr_offset, &new_ip, 0);

    // Replace Layer 3 (IP) checksum
    if let Err(err) = ctx.l3_csum_replace(
        ip_check_offset,
        u64::from(old_ip),
        u64::from(new_ip),
        mem::size_of::<u32>() as u64,
    ) {
        error!(ctx, "Layer 3 checksum replacement error: {}", err);
        return Err(());
    }

    Ok(())
}

/// Modifies a TCP port (source or destination) and updates the TCP checksum
/// accordingly.
fn modify_tcp_port(
    ctx: &mut TcContext,
    check_offset: usize,
    port_offset: usize,
    old_port: u16,
    new_port: u16,
) -> Result<(), ()> {
    if let Err(err) = ctx.store(port_offset, &new_port, 0 as u64) {
        error!(ctx, "err store {}", err);
        return Err(());
    }

    let size = mem::size_of::<u16>() as u64;
    if let Err(err) = ctx.l4_csum_replace(
        check_offset,
        u64::from(old_port),
        u64::from(new_port),
        size,
    ) {
        error!(ctx, "Checksum replacement error: {}", err);
        return Err(());
    }

    Ok(())
}

fn try_ingress(mut ctx: TcContext) -> Result<i32, ()> {
    let ethhdr: EthHdr = ctx.load(0).map_err(|_| ())?;
    match ethhdr.ether_type {
        EtherType::Ipv4 => {}
        _ => return Ok(TC_ACT_PIPE),
    }

    let iphdr: *mut Ipv4Hdr = ptr_at_mut(&ctx, EthHdr::LEN)?;
    match unsafe { (*iphdr).proto } {
        IpProto::Tcp => {}
        _ => return Ok(TC_ACT_PIPE),
    }

    let tcphdr: *mut TcpHdr = ptr_at_mut(&ctx, EthHdr::LEN + Ipv4Hdr::LEN)?;

    let src_addr = unsafe { (*iphdr).src_addr };
    let dst_addr = unsafe { (*iphdr).dst_addr };
    let src_port = unsafe { (*tcphdr).source };
    let dst_port = unsafe { (*tcphdr).dest };

    let is_fin = unsafe { (*tcphdr).fin() != 0 };
    let is_rst = unsafe { (*tcphdr).rst() != 0 };
    //let is_ack: bool = unsafe { (*tcphdr).ack() != 0 };

    let flow_id = FlowId { src_addr, dst_addr, src_port };

    if is_rst {
        return Ok(TC_ACT_OK);
    }

    if is_fin {
        if unsafe {
            bpf_map_delete_elem(
                addr_of_mut!(FLOW_MAP) as *mut _,
                &flow_id as *const _ as *const _,
            )
        } != 0
        {
            error!(&ctx, "INGRESS: Failed to remove flow from FLOW_MAP");
        } else {
            debug!(&ctx, "INGRESS: Flow entry removed on connection close");
        }

        return Ok(TC_ACT_OK);
    }

    let source_addr = u32::from_be(src_addr);
    let dest_addr = u32::from_be(dst_addr);
    let source_port = u16::from_be(src_port);
    let dest_port = u16::from_be(dst_port);

    let proxy_config = lookup_proxy_config(&ctx)?;
    let proxy_port = proxy_config.proxy_port;

    let lo_addr: u32 = 2130706433;
    if source_addr != lo_addr {
        return Ok(TC_ACT_PIPE);
    }

    if is_tracked_upstream_port(&ctx, dst_port) {
        info!(
            &ctx,
            "INGRESS source {} port {}, dest {}, port {}, proxy {}:{}",
            source_addr,
            source_port,
            dest_addr,
            dest_port,
            u32::from_be(proxy_config.proxy_ip),
            u16::from_be(proxy_port)
        );

        if update_flow_map(&ctx, flow_id, dst_port).is_err() {
            return Ok(TC_ACT_SHOT);
        }

        let offset = EthHdr::LEN + Ipv4Hdr::LEN;
        let check_offset = offset + offset_of!(TcpHdr, check);
        let dest_offset = offset + offset_of!(TcpHdr, dest);

        if modify_tcp_port(
            &mut ctx,
            check_offset,
            dest_offset,
            dst_port,
            proxy_port,
        )
        .is_err()
        {
            return Ok(TC_ACT_SHOT);
        }
        info!(
            &ctx,
            "INGRESS PORT MODIFIED from {} to {}",
            u16::from_be(dst_port),
            u16::from_be(proxy_port)
        );
    }

    Ok(TC_ACT_OK)
}

pub fn try_egress(mut ctx: TcContext) -> Result<i32, ()> {
    let ethhdr: EthHdr = ctx.load(0).map_err(|_| ())?;
    match ethhdr.ether_type {
        EtherType::Ipv4 => {}
        _ => return Ok(TC_ACT_PIPE),
    }

    let iphdr: *mut Ipv4Hdr = ptr_at_mut(&ctx, EthHdr::LEN)?;
    match unsafe { (*iphdr).proto } {
        IpProto::Tcp => {}
        _ => return Ok(TC_ACT_PIPE),
    }

    let tcphdr: *mut TcpHdr = ptr_at_mut(&ctx, EthHdr::LEN + Ipv4Hdr::LEN)?;

    let src_addr = unsafe { (*iphdr).src_addr };
    let dst_addr = unsafe { (*iphdr).dst_addr };
    let src_port = unsafe { (*tcphdr).source };
    let dst_port = unsafe { (*tcphdr).dest };

    let is_fin = unsafe { (*tcphdr).fin() != 0 };
    let is_rst = unsafe { (*tcphdr).rst() != 0 };
    //let is_ack = unsafe { (*tcphdr).ack() != 0 };

    let flow_id = FlowId { src_addr, dst_addr, src_port: dst_port };

    if is_rst {
        return Ok(TC_ACT_OK);
    }

    if is_fin {
        if unsafe {
            bpf_map_delete_elem(
                addr_of_mut!(FLOW_MAP) as *mut _,
                &flow_id as *const _ as *const _,
            )
        } != 0
        {
            error!(&ctx, "EGRESS: Failed to remove flow from FLOW_MAP");
        } else {
            debug!(&ctx, "EGRESS: Flow entry removed on connection close");
        }

        return Ok(TC_ACT_OK);
    }

    let source_addr = u32::from_be(src_addr);
    //let dest_addr = u32::from_be(dst_addr);
    //let source_port = u16::from_be(src_port);
    //let dest_port = u16::from_be(dst_port);

    let proxy_config = lookup_proxy_config(&ctx)?;
    let proxy_port = proxy_config.proxy_port;

    let lo_addr: u32 = 2130706433;
    if source_addr != lo_addr {
        return Ok(TC_ACT_PIPE);
    }

    if src_port == proxy_port {
        // info!(&ctx, "EGRESS source {} port {}, dest {}, port {}",
        // source_addr, source_port, dest_addr, dest_port);

        // Retrieve original destination port
        let orig_port_ptr = unsafe {
            bpf_map_lookup_elem(
                addr_of_mut!(FLOW_MAP) as *mut _,
                &flow_id as *const _ as *const _,
            )
        };

        if orig_port_ptr.is_null() {
            debug!(&ctx, "EGRESS: No matching flow in FLOW_MAP");
            return Ok(TC_ACT_OK);
        }

        let original_dest_port = unsafe { *(orig_port_ptr as *const u16) };
        let offset = EthHdr::LEN + Ipv4Hdr::LEN;
        let check_offset = offset + offset_of!(TcpHdr, check);
        let source_offset = offset + offset_of!(TcpHdr, source);

        if modify_tcp_port(
            &mut ctx,
            check_offset,
            source_offset,
            proxy_port,
            original_dest_port,
        )
        .is_err()
        {
            return Ok(TC_ACT_SHOT);
        }
        //info!(&ctx, "EGRESS PORT REVERTED from {} to {}",
        // u16::from_be(proxy_port), u16::from_be(original_dest_port));
    }

    Ok(TC_ACT_OK)
}

#[cfg(not(test))]
#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}
