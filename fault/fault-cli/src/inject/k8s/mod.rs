use std::collections::BTreeMap;
use std::time::Duration;
use std::time::Instant;

use anyhow::Result;
use anyhow::anyhow;
use async_trait::async_trait;
use k8s_openapi::api::batch::v1::Job;
use k8s_openapi::api::core::v1::ConfigMap;
use k8s_openapi::api::core::v1::Pod;
use k8s_openapi::api::core::v1::Service;
use k8s_openapi::api::core::v1::ServiceAccount;
use kube::Api;
use kube::Client;
use kube::api::ListParams;
use tokio::time::sleep;

pub(crate) mod run;
pub(crate) mod scenario;

use crate::discovery::k8s::discover_kubernetes_resources;
use crate::discovery::types::K8sSpecSnapshot;
use crate::discovery::types::Resource;
use crate::inject::InjectionHandle;
use crate::inject::Platform;
use crate::inject::ServiceResource;

/// Kubernetes implementation of `Platform`.
#[derive(Clone)]
pub struct KubernetesPlatform {
    client: Client,
    namespace: String,
    scenario: Option<String>,
    fault_settings: Option<BTreeMap<String, String>>,
    service_name: String,
    container_image: String,
    api_address: String,
    resources: Vec<Resource>,
    injection_handle: Option<InjectionHandle>,
}

impl KubernetesPlatform {
    pub async fn new_proxy(
        namespace: &str,
        service: &str,
        container_image: &str,
        api_address: &str,
        fault_settings: BTreeMap<String, String>,
    ) -> Result<Self> {
        let client = Client::try_default().await?;
        let resources = discover_kubernetes_resources(namespace).await?;
        Ok(Self {
            client,
            fault_settings: Some(fault_settings.clone()),
            scenario: None,
            namespace: namespace.to_string(),
            service_name: service.to_string(),
            container_image: container_image.to_string(),
            api_address: api_address.to_string(),
            resources,
            injection_handle: None,
        })
    }

    pub async fn new_scenario(
        namespace: &str,
        service: &str,
        container_image: &str,
        api_address: &str,
        scenario: String,
    ) -> Result<Self> {
        let client = Client::try_default().await?;
        let resources = discover_kubernetes_resources(namespace).await?;
        Ok(Self {
            client,
            fault_settings: None,
            scenario: Some(scenario.clone()),
            namespace: namespace.to_string(),
            service_name: service.to_string(),
            container_image: container_image.to_string(),
            api_address: api_address.to_string(),
            resources,
            injection_handle: None,
        })
    }

    fn is_scenario(&self) -> bool {
        return self.scenario.is_some();
    }

    fn is_proxy(&self) -> bool {
        return self.fault_settings.is_some();
    }

    /// Helper: get only the Service‐kind entries (with address)
    fn cached_services(&self) -> Vec<ServiceResource> {
        self.resources
            .iter()
            .filter(|r| r.meta.kind == "Service")
            .map(|r| {
                let addr = r.content["spec"]["clusterIP"]
                    .as_str()
                    .unwrap_or(&r.meta.name)
                    .to_string();
                ServiceResource { name: r.meta.name.clone(), address: addr }
            })
            .collect()
    }

    /// Helper: find the full Resource for a given name
    fn find_resource(&self, name: &str) -> &Resource {
        self.resources
            .iter()
            .find(|r| r.meta.name == name)
            .expect("service must exist in cache")
    }
}

#[async_trait]
impl Platform for KubernetesPlatform {
    async fn discover(&self) -> Result<Vec<ServiceResource>> {
        Ok(self.cached_services())
    }

    async fn get_service(&self) -> Result<ServiceResource> {
        let svcs = self.discover().await?;
        let svc = match svcs.into_iter().find(|s| s.name == self.service_name) {
            Some(m) => m,
            None => {
                return Err(anyhow!(format!(
                    "service '{}' could not be found",
                    self.service_name
                )));
            }
        };

        Ok(svc)
    }

    fn set_service(&mut self, service: &str) -> Result<()> {
        self.service_name = service.to_string();
        Ok(())
    }

    async fn inject(&mut self) -> Result<()> {
        let svc = self.get_service().await?;
        let full = self.find_resource(&svc.name);
        let snapshot;

        if self.is_proxy() {
            let fault_vars = &mut self.fault_settings.clone().unwrap().clone();
            snapshot = run::inject_fault_proxy(
                self.client.clone(),
                full,
                fault_vars,
                self.container_image.clone(),
                self.api_address.clone(),
            )
            .await?;
        } else {
            snapshot = scenario::inject_fault_scenario(
                self.client.clone(),
                full,
                self.scenario.clone().unwrap(),
                self.container_image.clone(),
                self.api_address.clone(),
            )
            .await?;
        }

        let token = serde_json::to_string(&snapshot)?;
        self.injection_handle =
            Some(InjectionHandle::Kubernetes { rollback_token: token });
        Ok(())
    }

    async fn rollback(&mut self) -> Result<()> {
        if let Some(handle) = &self.injection_handle {
            let svc = self.get_service().await?;
            if let Some(InjectionHandle::Kubernetes { rollback_token }) =
                self.injection_handle.take()
            {
                let snapshot: K8sSpecSnapshot =
                    serde_json::from_str(&rollback_token)?;
                let full = self.find_resource(&svc.name);
                if self.is_proxy() {
                    run::rollback_fault_injection(
                        self.client.clone(),
                        full,
                        snapshot,
                    )
                    .await?;
                } else {
                    scenario::rollback_fault_injection(
                        self.client.clone(),
                        full,
                        snapshot,
                    )
                    .await?;
                }
            }
        }

        Ok(())
    }

    async fn update_fault_settings(
        &mut self,
        fault_settings: &mut BTreeMap<String, String>,
    ) -> Result<()> {
        if let Some(ref mut settings) = self.fault_settings {
            settings.clear();
            settings.append(fault_settings);
        }

        Ok(())
    }

    async fn wait_ready(&mut self) -> Result<()> {
        let svc = self.get_service().await?;
        let ns = &self.namespace;
        let proxy_name = format!("{}-proxy", svc.name);

        let pods_api: Api<Pod> = Api::namespaced(self.client.clone(), ns);
        let start = Instant::now();
        let timeout = Duration::from_secs(60);
        let interval = Duration::from_millis(300);

        loop {
            let lp =
                ListParams::default().labels(&format!("app={}", proxy_name));
            let pod_list = pods_api.list(&lp).await?;

            // Check each pod for phase=Running and condition Ready=True
            for pod in pod_list.items.iter() {
                if let Some(status) = pod.status.as_ref() {
                    if status.phase.as_deref() == Some("Running") {
                        if let Some(conds) = status.conditions.as_ref() {
                            if conds.iter().any(|c| {
                                c.type_ == "Ready" && c.status == "True"
                            }) {
                                return Ok(());
                            }
                        }
                    }
                }
            }

            if start.elapsed() > timeout {
                anyhow::bail!(
                    "Timed out waiting for proxy pod `{}` to become Ready",
                    proxy_name
                );
            }
            sleep(interval).await;
        }
    }

    async fn wait_cleanup(&mut self) -> Result<()> {
        let svc = self.get_service().await?;
        let ns = &self.namespace;
        let proxy_name = format!("{}-proxy", svc.name);
        let backend_name = format!("{}-backend", svc.name);

        let dp = Duration::from_secs(30);
        let interval = Duration::from_secs(2);
        let start = Instant::now();

        // prepare all the APIs we’ll check
        let jobs: Api<Job> = Api::namespaced(self.client.clone(), ns);
        let services: Api<Service> = Api::namespaced(self.client.clone(), ns);
        let cms: Api<ConfigMap> = Api::namespaced(self.client.clone(), ns);
        let sas: Api<ServiceAccount> = Api::namespaced(self.client.clone(), ns);
        let pods: Api<Pod> = Api::namespaced(self.client.clone(), ns);

        loop {
            // check each resource for non-existence
            let j_exist = jobs.get_opt(&proxy_name).await?.is_some();
            let s_exist = services.get_opt(&proxy_name).await?.is_some()
                || services.get_opt(&backend_name).await?.is_some();
            let cm_exist =
                cms.get_opt(&format!("{}-config", proxy_name)).await?.is_some();
            let sa_exist = sas.get_opt(&proxy_name).await?.is_some();
            // also wait for any proxy pods to vanish
            let lp =
                ListParams::default().labels(&format!("app={}", proxy_name));
            let pod_list = pods.list(&lp).await?;
            let pods_exist = !pod_list.items.is_empty();

            if !(j_exist || s_exist || cm_exist || sa_exist || pods_exist) {
                return Ok(());
            }

            if start.elapsed() > dp {
                anyhow::bail!(
                    "timed out waiting for cleanup of `{}`",
                    svc.name
                );
            }
            sleep(interval).await;
        }
    }

    fn get_concrete_resources(&self) -> &Vec<Resource> {
        &self.resources
    }

    fn get_concrete_service(&self) -> &Resource {
        self.resources
            .iter()
            .find(|r| {
                r.meta.kind == "Service" && r.meta.name == self.service_name
            })
            .unwrap()
    }
}
