#![no_std]
#![no_main]
#![allow(static_mut_refs)]

use core::mem;

use aya_ebpf::EbpfContext;
use aya_ebpf::bindings::BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB;
use aya_ebpf::bindings::TC_ACT_RECLASSIFY;
use aya_ebpf::bindings::bpf_sock_addr;
use aya_ebpf::bindings::bpf_sockopt;
use aya_ebpf::bindings::{self};
use aya_ebpf::macros::cgroup_sock_addr;
use aya_ebpf::macros::cgroup_sockopt;
use aya_ebpf::macros::map;
use aya_ebpf::macros::sock_ops;
use aya_ebpf::maps::HashMap;
use aya_ebpf::programs::SockAddrContext;
use aya_ebpf::programs::SockOpsContext;
use aya_ebpf::programs::SockoptContext;
use aya_log_ebpf::debug;
use network_types::ip::IpProto;

// ---------------------------------------------------------------------
// Data Structures and Maps
// ---------------------------------------------------------------------

/// Proxy configuration: Only IPv4 is supported.
/// All IP addresses and ports are stored in network byte order.
#[repr(C)]
#[derive(Copy, Clone)]
pub struct ProxyConfig {
    /// Target process name (null-terminated in 16 bytes).
    pub target_proc_name: [u8; 16],
    /// If a connection originates from this PID (the proxy), skip redirection.
    pub proxy_pid: u32,
    /// IPv4 proxy address (network byte order)
    pub proxy_ip4: u32,
    /// IPv4 proxy port (network byte order)
    pub proxy_port4: u16,
}

#[map(name = "PROXY_CONFIG")]
static mut PROXY_CONFIG: HashMap<u32, ProxyConfig> =
    HashMap::<u32, ProxyConfig>::with_max_entries(1, 0);

/// Structure to hold the original destination (for IPv4).
#[repr(C)]
#[derive(Copy, Clone)]
pub struct Socket {
    pub dst_addr: u32, // original destination IP (network byte order)
    pub dst_port: u16, // original destination port (network byte order)
}

/// Map to store the original destination for each connection,
/// keyed by a unique socket cookie (a 64-bit value).
#[map(name = "MAP_SOCKS")]
static mut MAP_SOCKS: HashMap<u64, Socket> =
    HashMap::<u64, Socket>::with_max_entries(20000, 0);

/// Map to store a mapping from the client's source port to the socket cookie.
/// This helps the getsockopt program find the correct connection.
#[map(name = "MAP_PORTS")]
static mut MAP_PORTS: HashMap<u16, u64> =
    HashMap::<u16, u64>::with_max_entries(20000, 0);

/// Structure representing the source socker information once the connection
/// has been established
/// aya doesn't seem to provide these structures
#[repr(C)]
pub struct InAddr {
    pub s_addr: u32,
}

#[repr(C)]
pub struct SockaddrIn {
    pub sin_family: u16,
    pub sin_port: u16,
    pub sin_addr: InAddr,
    pub sin_zero: [u8; 8],
}

const SOCKADDR_IN_SIZE: usize = 16;

// ---------------------------------------------------------------------
// Helper Functions
// ---------------------------------------------------------------------

/// Returns `true` if the given `comm_arr` (up to its null terminator) starts
/// with the bytes in `prefix`. Otherwise returns `false`.
///
/// This ignores any trailing zeros beyond the null terminator, but if the
/// prefix is longer than the comm’s actual length (as determined by null or the
/// array size), it returns false.
#[inline(always)]
fn starts_with_comm(comm_arr: &[u8; 16], prefix_arr: &[u8; 16]) -> bool {
    // 1) Find end of comm (first null or full length)
    let comm_end =
        comm_arr.iter().position(|&b| b == 0).unwrap_or(comm_arr.len());

    // 2) Find end of prefix (first null or full length)
    let prefix_end =
        prefix_arr.iter().position(|&b| b == 0).unwrap_or(prefix_arr.len());

    // 3) If the prefix (non-null portion) is longer than the comm, can't match
    if prefix_end > comm_end {
        return false;
    }

    // 4) Check if comm's first `prefix_end` bytes match the prefix's first
    //    `prefix_end` bytes
    comm_arr[0..prefix_end] == prefix_arr[0..prefix_end]
}

// ---------------------------------------------------------------------
// cgroup_sock_addr Program for IPv4 (Redirect on connect)
// ---------------------------------------------------------------------

/// This program runs when a process calls connect(2) on an IPv4 socket.
/// It filters by IPv4/TCP and by process name, then stores the original
/// destination (from sock->user_ip4 and user_port) in MAP_SOCKS and rewrites
/// the socket's destination to the proxy address/port. The kernel will preserve
/// the original destination so that the proxy can later retrieve it via
/// getsockopt(SO_ORIGINAL_DST).
#[cgroup_sock_addr(connect4)]
pub fn cg_connect4(ctx: SockAddrContext) -> i32 {
    let sock = unsafe { &*ctx.sock_addr };
    // Process only IPv4 TCP connections.
    if sock.user_family != 2 || sock.protocol != IpProto::Tcp as u32 {
        return TC_ACT_RECLASSIFY;
    }
    let config = match unsafe { PROXY_CONFIG.get(&0) } {
        Some(c) => c,
        None => return TC_ACT_RECLASSIFY,
    };

    let comm = match ctx.command() {
        Ok(c) => c,
        Err(_) => return TC_ACT_RECLASSIFY,
    };

    if !starts_with_comm(&comm, &config.target_proc_name) {
        return 1;
    }

    let pid = ctx.pid() as u32;
    if pid == config.proxy_pid {
        return TC_ACT_RECLASSIFY;
    }

    // Capture the original destination (from the connect syscall).
    let orig_ip = sock.user_ip4;
    let orig_port = sock.user_port as u16;

    // Obtain a unique socket cookie.
    // Note: bpf_get_socket_cookie is provided by Aya as a helper.
    let cookie =
        unsafe { aya_ebpf::helpers::bpf_get_socket_cookie(ctx.as_ptr()) };

    // Store the original destination in MAP_SOCKS, keyed by the cookie.
    let orig = Socket { dst_addr: orig_ip, dst_port: orig_port };
    unsafe {
        let _ = MAP_SOCKS.insert(&cookie, &orig, 0);
    }

    // Rewrite the socket's destination so that the connection is redirected to
    // the proxy.
    let sock_mut = ctx.sock_addr as *mut bpf_sock_addr;
    unsafe {
        (*sock_mut).user_ip4 = config.proxy_ip4.to_be();
        (*sock_mut).user_port = u32::from(config.proxy_port4);
    }

    TC_ACT_RECLASSIFY
}

// ---------------------------------------------------------------------
// sock_ops Program: Map client's source port to socket cookie
// ---------------------------------------------------------------------

/// This program fires on ACTIVE_ESTABLISHED events
/// (BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB). It retrieves the unique socket cookie
/// and the client's ephemeral local port, then updates MAP_PORTS to map that
/// port to the cookie.
#[sock_ops]
pub fn cg_sock_ops(ctx: SockOpsContext) -> u32 {
    // Only handle ACTIVE_ESTABLISHED events. (op code 3 is typical.)
    if ctx.op() != BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB {
        return 0;
    }
    let cookie =
        unsafe { aya_ebpf::helpers::bpf_get_socket_cookie(ctx.as_ptr()) };
    // Retrieve the local (client) port.
    let local_port = ctx.local_port() as u16;
    unsafe {
        let _ = MAP_PORTS.insert(&local_port, &cookie, 0);
    }
    // TC_ACT_OK
    0
}

// ---------------------------------------------------------------------
// cgroup_sockopt Program: Respond to SO_ORIGINAL_DST
// ---------------------------------------------------------------------

/// This program is triggered when the proxy calls getsockopt(SO_ORIGINAL_DST).
/// It uses the client's source port (from the socket) to retrieve the
/// corresponding cookie from MAP_PORTS, then uses that cookie to get the
/// original destination from MAP_SOCKS. Finally, it writes the original
/// destination (a sockaddr_in) into the optval.
#[cgroup_sockopt(getsockopt)]
pub fn cg_sock_opt(ctx: SockoptContext) -> i32 {
    let sockopt = unsafe { &mut *(ctx.sockopt as *mut bpf_sockopt) };

    // this should be SO_ORIGINAL_DST
    if sockopt.optname != 80 {
        return TC_ACT_RECLASSIFY;
    }

    let sk = unsafe { &*sockopt.__bindgen_anon_1.sk };

    // must be an IP family
    if sk.family != 2 {
        return TC_ACT_RECLASSIFY;
    }

    // must be TCP
    if sk.protocol != 6 {
        return TC_ACT_RECLASSIFY;
    }

    // Get the client's source port.
    let src_port = u16::from_be(sk.dst_port as u16);

    // Look up the cookie using the client's source port.
    let cookie = match unsafe { MAP_PORTS.get(&src_port) } {
        Some(c) => c,
        None => return TC_ACT_RECLASSIFY,
    };

    // Look up the original destination using the cookie.
    let orig = match unsafe { MAP_SOCKS.get(&cookie) } {
        Some(o) => o,
        None => return TC_ACT_RECLASSIFY,
    };

    // optval is assumed to point to a SockaddrIn.
    let optval = unsafe { sockopt.__bindgen_anon_2.optval };
    let optval_end = unsafe { sockopt.__bindgen_anon_3.optval_end };
    let sa: *mut SockaddrIn = optval as *mut SockaddrIn;
    if sa.is_null() {
        return TC_ACT_RECLASSIFY;
    }

    if (optval as usize + SOCKADDR_IN_SIZE) > optval_end as usize {
        return TC_ACT_RECLASSIFY;
    }

    // we overwrite the response of getsockopt(SO_ORIGINAL_DST)
    // after the syscall has returned
    // ordering matters here, if you set optlen after the changes in the
    // socket addr, the verifier will bail on you
    sockopt.optlen = mem::size_of_val(&sa) as i32;
    unsafe {
        (*sa).sin_family = sk.family as u16;
        (*sa).sin_addr.s_addr = orig.dst_addr;
        (*sa).sin_port = orig.dst_port;
    }
    sockopt.retval = 0;

    TC_ACT_RECLASSIFY
}

//
// ==================== Panic Handler and License ====================
//
#[cfg(not(test))]
#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}
