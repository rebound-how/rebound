use std::sync::Arc;

use arc_swap::ArcSwap;
use tokio::sync::RwLock;
use tokio::sync::watch;

use crate::config::ProxyConfig;
use crate::fault::FaultInjector;
use crate::plugin::CompositePlugin;
use crate::plugin::metrics::MetricsInjector;
use crate::plugin::rpc::RpcPluginManager;

pub mod protocols;

/// Shared application state
#[derive(Debug, Clone)]
pub struct ProxyState {
    pub faults_plugin: Arc<ArcSwap<CompositePlugin>>,
    pub shared_config: Arc<ArcSwap<ProxyConfig>>,
    pub upstream_hosts: Arc<ArcSwap<Vec<String>>>,
    pub rpc_manager: Arc<RwLock<RpcPluginManager>>,
    pub stealth: bool,
}

impl ProxyState {
    pub fn new(stealth: bool) -> Self {
        Self {
            faults_plugin: Arc::new(ArcSwap::from_pointee(
                CompositePlugin::empty(),
            )),
            shared_config: Arc::new(ArcSwap::from_pointee(
                ProxyConfig::default(),
            )),
            upstream_hosts: Arc::new(ArcSwap::from_pointee(Vec::new())),
            rpc_manager: Arc::new(RwLock::new(RpcPluginManager::new())),
            stealth,
        }
    }

    /// Update the fault injectors
    pub async fn set_injectors(&self, new_faults: Vec<Box<dyn FaultInjector>>) {
        let grpc_plugins = self.rpc_manager.read().await;

        let mut injectors = Vec::new();
        injectors.extend(new_faults);
        injectors.push(Box::new(grpc_plugins.clone()));
        injectors.push(Box::new(MetricsInjector::new()));

        let mut new_plugins = CompositePlugin::empty();
        new_plugins.injectors = Arc::new(injectors);

        tracing::debug!(
            "Applying proxy fault injectors: {:?}",
            new_plugins.injectors
        );
        self.faults_plugin.store(Arc::new(new_plugins));
    }

    /// Update the shared configuration.
    pub async fn set_config(&self, new_config: ProxyConfig) {
        tracing::debug!("Applying proxy configuration: {:?}", new_config);
        self.shared_config.store(Arc::new(new_config));
    }

    /// Update the upstream hosts.
    pub async fn set_upstream_hosts(&self, new_hosts: Vec<String>) {
        tracing::debug!("Allowed hosts {:?}", new_hosts);
        self.upstream_hosts.store(Arc::new(new_hosts));
    }
}

pub async fn monitor_and_update_proxy_config(
    proxy_state: Arc<ProxyState>,
    mut config_rx: watch::Receiver<(ProxyConfig, Vec<Box<dyn FaultInjector>>)>,
) {
    loop {
        match config_rx.changed().await {
            Ok(_) => {
                let (new_config, faults) =
                    config_rx.borrow_and_update().clone();
                proxy_state.set_config(new_config).await;
                proxy_state.set_injectors(faults).await;
            }
            Err(e) => {
                tracing::debug!("Exited proxy config loop: {}", e);
                break;
            }
        };
    }
}
