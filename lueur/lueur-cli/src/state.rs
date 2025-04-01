use std::sync::Arc;

use url::Url;

use crate::cli::ProxyAwareCommandCommon;
use crate::proxy::ProxyState;

#[derive(Debug, Clone)]
pub struct AppState {
    pub proxy_state: Arc<ProxyState>,
}

pub async fn initialize_application_state(
    cli: &ProxyAwareCommandCommon,
    is_stealth: bool,
) -> AppState {
    // Initialize shared state with empty configuration
    let state = Arc::new(ProxyState::new(is_stealth));

    //let rpc_plugin = load_remote_plugins(cli.grpc_plugins.clone()).await;
    //state.update_plugins(vec![rpc_plugin]).await;

    let upstream_hosts = cli.upstream_hosts.clone();
    let upstreams: Vec<String> =
        upstream_hosts.iter().map(|h| upstream_to_addr(h).unwrap()).collect();

    state.update_upstream_hosts(upstreams).await;

    AppState { proxy_state: state }
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
