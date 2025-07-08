use std::collections::BTreeMap;

use anyhow::Result;
use async_trait::async_trait;
use google_cloud_longrunning::model::Operation;
use serde::Deserialize;
use serde::Serialize;

use crate::discovery::types::Resource;

pub(crate) mod aws;
#[cfg(feature = "scenario")]
pub(crate) mod event;
pub(crate) mod gcp;
pub(crate) mod k8s;

/// A discovered, addressable backend service.
#[derive(Clone, Debug)]
pub struct ServiceResource {
    pub name: String,
    pub address: String,
}

/// Data needed to roll back an injection.
#[derive(Clone)]
pub struct _InjectionHandle {
    pub rollback_token: String,
}

#[derive(Clone, Serialize, Deserialize, Debug)]
pub enum InjectionHandle {
    Kubernetes { rollback_token: String },
    CloudRun { rollback_token: String, op: Operation },
    Ecs { rollback_token: String, lbs: String },
}

/// Common interface for fault‐proxy injection on different platforms.
#[async_trait]
pub trait Platform {
    /// List all “services” available for injection.
    async fn discover(&self) -> Result<Vec<ServiceResource>>;

    /// Inject a proxy into the given service, returning a handle for rollback.
    async fn inject(&mut self) -> Result<()>;

    /// Roll back a previous injection.
    async fn rollback(&mut self) -> Result<()>;

    /// Set the service resource
    fn set_service(&mut self, service: &str) -> Result<()>;

    /// Get the service resource
    async fn get_service(&self) -> Result<ServiceResource>;

    /// Update the proxy parameters.
    async fn update_fault_settings(
        &mut self,
        fault_settings: &mut BTreeMap<String, String>,
    ) -> Result<()>;

    async fn wait_ready(&mut self) -> Result<()>;

    async fn wait_cleanup(&mut self) -> Result<()>;

    fn get_concrete_resources(&self) -> &Vec<Resource>;

    fn get_concrete_service(&self) -> &Resource;
}
