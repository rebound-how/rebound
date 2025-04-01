use std::sync::Arc;

use tokio::sync::RwLock;

use crate::config::FaultConfig;
use crate::config::FaultKind;
use crate::config::ProxyConfig;
use crate::fault::FaultInjector;
use crate::plugin::CompositePlugin;
use crate::plugin::load_injector;
use crate::types::FaultConfiguration;

pub mod protocols;

/// Shared application state
#[derive(Debug, Clone)]
pub struct ProxyState {
    pub plugins: Arc<RwLock<CompositePlugin>>,
    pub shared_config: Arc<RwLock<ProxyConfig>>,
    pub upstream_hosts: Arc<RwLock<Vec<String>>>,
    pub stealth: bool,
}

impl ProxyState {
    pub fn new(stealth: bool) -> Self {
        Self {
            plugins: Arc::new(RwLock::new(CompositePlugin::empty())),
            shared_config: Arc::new(RwLock::new(ProxyConfig::default())),
            upstream_hosts: Arc::new(RwLock::new(Vec::new())),
            stealth,
        }
    }

    /// Update the faults
    pub async fn set_faults(&self, new_faults: Vec<Box<dyn FaultInjector>>) {
        let mut plugins = self.plugins.write().await;
        plugins.set_injectors(new_faults);
    }

    /// Update the shared configuration.
    pub async fn update_config(&self, new_config: ProxyConfig) {
        tracing::debug!("Applying proxy configuration: {:?}", new_config);
        let mut config = self.shared_config.write().await;
        *config = new_config;
    }

    /// Update the upstream hosts.
    pub async fn update_upstream_hosts(&self, new_hosts: Vec<String>) {
        tracing::debug!("Allowed hosts {:?}", new_hosts);
        let mut hosts = self.upstream_hosts.write().await;
        *hosts = new_hosts;
    }

    pub async fn set_fault(&self, fault: FaultConfiguration) {
        tracing::debug!("Setting fault on config: {:?}", fault);
        let mut config = self.shared_config.write().await;

        let fault_config = fault.build().unwrap();
        let kind = fault_config.kind();

        if let Some(existing) = config.find_mut_by_kind(kind) {
            *existing = fault_config;
        } else {
            config.faults.push(fault_config);
        }
    }

    pub async fn enable_fault(
        &self,
        fault_type: FaultKind,
        fault_config: FaultConfig,
    ) {
        tracing::debug!("Enabling fault {:?}", fault_type);
        let mut config = self.shared_config.write().await;
        let mut plugins = self.plugins.write().await;

        if let Some(existing) = config.find_mut_by_kind(fault_type) {
            existing.enable();
            plugins.enable_injector(fault_type);
        } else {
            let injector = load_injector(&fault_config);
            plugins.add_injector(injector);
            config.add_fault(fault_config);
        }
    }

    pub async fn disable_fault(
        &self,
        fault_type: FaultKind,
        fault_config: FaultConfig,
    ) {
        tracing::debug!("Disabling fault {:?}", fault_type);
        let mut config = self.shared_config.write().await;
        let mut plugins = self.plugins.write().await;

        if let Some(existing) = config.find_mut_by_kind(fault_type) {
            existing.disable();
            plugins.disable_injector(fault_type);
        }
    }
}
