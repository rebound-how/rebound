use std::sync::Arc;

use url::Url;

use crate::cli::ProxyAwareCommandCommon;
use crate::errors::ProxyError;
use crate::plugin::rpc::load_remote_plugins_as_injectors;
use crate::proxy::ProxyState;

pub async fn initialize_proxy_state(
    cli: &ProxyAwareCommandCommon,
    is_stealth: bool,
) -> Result<Arc<ProxyState>, ProxyError> {
    // Initialize shared state with empty configuration
    //let state = Arc::new(ProxyState::new(is_stealth));
    let state = ProxyState::new(is_stealth);

    let _ = load_remote_plugins_as_injectors(
        state.rpc_manager.clone(),
        cli.grpc_plugins.clone(),
    )
    .await;

    let upstream_hosts = cli.upstream_hosts.clone();
    let upstreams: Vec<String> =
        upstream_hosts.iter().map(|h| upstream_to_addr(h).unwrap()).collect();

    state.set_upstream_hosts(upstreams).await;

    Ok(Arc::new(state))
}

fn upstream_to_addr(
    host: &String,
) -> Result<String, Box<dyn std::error::Error>> {
    if host == &String::from("*") {
        return Ok(host.clone());
    }

    let url_str = if host.contains("://") {
        host.to_string()
    } else {
        format!("scheme://{}", host)
    };

    let url = Url::parse(&url_str)?;
    let host = url.host_str().ok_or("Missing host")?.to_string();
    let port = url.port_or_known_default().unwrap();

    Ok(format!("{}:{}", host, port))
}
