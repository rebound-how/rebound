use std::collections::BTreeMap;
use std::time::Instant;

use anyhow::Result;
use async_trait::async_trait;
use k8s_openapi::api::apps::v1::Deployment;
use k8s_openapi::api::apps::v1::DeploymentSpec;
use k8s_openapi::api::apps::v1::DeploymentStrategy;
use k8s_openapi::api::core::v1::ConfigMap;
use k8s_openapi::api::core::v1::Container;
use k8s_openapi::api::core::v1::EnvFromSource;
use k8s_openapi::api::core::v1::Pod;
use k8s_openapi::api::core::v1::PodSecurityContext;
use k8s_openapi::api::core::v1::Service;
use k8s_openapi::api::core::v1::ServiceAccount;
use k8s_openapi::apimachinery::pkg::apis::meta::v1::LabelSelector;
use k8s_openapi::apimachinery::pkg::apis::meta::v1::ObjectMeta;
use k8s_openapi::apimachinery::pkg::util::intstr::IntOrString;
use kube::api::ListParams;
use kube::Api;
use kube::Client;
use kube::api::DeleteParams;
use kube::api::Patch;
use kube::api::PatchParams;
use kube::api::PostParams;
use tokio::time::sleep;
use std::time::Duration;
use serde_json;
use serde_json::json;

use crate::discovery::k8s::discover_kubernetes_resources;
use crate::discovery::types::K8sSpecSnapshot;
use crate::discovery::types::Resource;

/// A discovered, addressable backend service.
pub struct ServiceResource {
    pub name: String,
    pub address: String,
}

/// Data needed to roll back an injection.
pub struct InjectionHandle {
    pub rollback_token: String,
}

/// Common interface for fault‐proxy injection on different platforms.
#[async_trait]
pub trait Platform {
    /// List all “services” available for injection.
    async fn discover(&self) -> Result<Vec<ServiceResource>>;

    /// Inject a proxy into the given service, returning a handle for rollback.
    async fn inject(
        &mut self,
        svc: &ServiceResource,
    ) -> Result<InjectionHandle>;

    /// Roll back a previous injection.
    async fn rollback(
        &self,
        svc: &ServiceResource,
        handle: InjectionHandle,
    ) -> Result<()>;

    /// Update the proxy parameters.
    async fn update(
        &mut self,
        fault_settings: &mut BTreeMap<String, String>,
    ) -> Result<()>;

    async fn wait_ready(&self, svc: &ServiceResource) -> Result<()>;

    async fn wait_cleanup(&self, svc: &ServiceResource) -> Result<()>;
}

/// Kubernetes implementation of `Platform`.
pub struct KubernetesPlatform {
    client: Client,
    namespace: String,
    fault_settings: BTreeMap<String, String>,
    resources: Vec<Resource>,
}

impl KubernetesPlatform {
    /// Construct from an existing kubeconfig / in‐cluster config.
    pub async fn new(
        namespace: &str,
        fault_settings: BTreeMap<String, String>,
    ) -> Result<Self> {
        let client = Client::try_default().await?;
        let resources = discover_kubernetes_resources(namespace).await?;
        Ok(Self {
            client,
            fault_settings,
            namespace: namespace.to_string(),
            resources,
        })
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

    async fn inject(
        &mut self,
        svc: &ServiceResource,
    ) -> Result<InjectionHandle> {
        let fault_vars = &mut self.fault_settings.clone();
        let full = self.find_resource(&svc.name);
        let snapshot =
            inject_fault_proxy(self.client.clone(), full, fault_vars).await?;

        let token = serde_json::to_string(&snapshot)?;
        Ok(InjectionHandle { rollback_token: token })
    }

    async fn rollback(
        &self,
        svc: &ServiceResource,
        handle: InjectionHandle,
    ) -> Result<()> {
        let snapshot: K8sSpecSnapshot =
            serde_json::from_str(&handle.rollback_token)?;
        let full = self.find_resource(&svc.name);
        rollback_fault_injection(self.client.clone(), full, snapshot).await?;
        Ok(())
    }
    
    async fn update(
        &mut self,
        fault_settings: &mut BTreeMap<String, String>,
    ) -> Result<()> {
        self.fault_settings.clear();
        self.fault_settings.append(fault_settings);

        Ok(())
    }

    async fn wait_ready(&self, svc: &ServiceResource) -> anyhow::Result<()> {
        let deploy_name = format!("{}-proxy", svc.name);
        let api: Api<Deployment> = Api::namespaced(self.client.clone(), &self.namespace);

        let start = Instant::now();
        let timeout = Duration::from_secs(30);
        let poll_interval = Duration::from_secs(2);

        loop {
            let d = api.get(&deploy_name).await?;

            let spec_replicas = d
                .spec
                .as_ref()
                .and_then(|s| s.replicas)
                .unwrap_or(1);
            let available = d
                .status
                .as_ref()
                .and_then(|s| s.available_replicas)
                .unwrap_or(0);

            if available >= spec_replicas {
                return Ok(());
            }

            if start.elapsed() > timeout {
                anyhow::bail!(
                    "timed out waiting for Deployment '{}' to become ready: {}/{} available",
                    deploy_name,
                    available,
                    spec_replicas
                );
            }

            sleep(poll_interval).await;
        }
    }

    async fn wait_cleanup(&self, svc: &ServiceResource) -> Result<()> {
        let ns = &self.namespace;
        let proxy_name   = format!("{}-proxy", svc.name);
        let backend_name = format!("{}-backend", svc.name);

        let dp = Duration::from_secs(30);
        let interval = Duration::from_secs(2);
        let start = Instant::now();

        // prepare all the APIs we’ll check
        let deploys: Api<Deployment> = Api::namespaced(self.client.clone(), ns);
        let services: Api<Service>   = Api::namespaced(self.client.clone(), ns);
        let cms: Api<ConfigMap>      = Api::namespaced(self.client.clone(), ns);
        let sas: Api<ServiceAccount> = Api::namespaced(self.client.clone(), ns);
        let pods: Api<Pod>           = Api::namespaced(self.client.clone(), ns);

        loop {
            // check each resource for non-existence
            let d_exist = deploys.get_opt(&proxy_name).await?.is_some();
            let s_exist = services.get_opt(&proxy_name).await?.is_some()
                        || services.get_opt(&backend_name).await?.is_some();
            let cm_exist= cms.get_opt(&format!("{}-config", proxy_name)).await?.is_some();
            let sa_exist= sas.get_opt(&proxy_name).await?.is_some();
            // also wait for any proxy pods to vanish
            let lp = ListParams::default().labels(&format!("app={}-proxy", svc.name));
            let pod_list = pods.list(&lp).await?;
            let pods_exist = !pod_list.items.is_empty();

            if !(d_exist || s_exist || cm_exist || sa_exist || pods_exist) {
                return Ok(());
            }

            if start.elapsed() > dp {
                anyhow::bail!("timed out waiting for cleanup of `{}`", svc.name);
            }
            sleep(interval).await;
        }
    }
}

/// Build the ServiceAccount
fn build_service_account(
    ns: &str,
    name: &str,
    labels: &BTreeMap<String, String>,
) -> ServiceAccount {
    ServiceAccount {
        metadata: ObjectMeta {
            namespace: Some(ns.into()),
            name: Some(name.into()),
            labels: Some(labels.clone()),
            ..Default::default()
        },
        automount_service_account_token: Some(false),
        ..Default::default()
    }
}

/// Build the ConfigMap
fn build_config_map(
    ns: &str,
    name: &str,
    labels: &BTreeMap<String, String>,
    data: BTreeMap<String, String>,
) -> ConfigMap {
    ConfigMap {
        metadata: ObjectMeta {
            namespace: Some(ns.into()),
            name: Some(name.into()),
            labels: Some(labels.clone()),
            ..Default::default()
        },
        data: Some(data),
        ..Default::default()
    }
}

/// Build an intermediate “backend” Service that selects exactly the original
/// pods
fn build_backend_service(original: &Resource, backend_name: &str) -> Service {
    // Pull the original ports & selector out of the Resource’s `content`
    let spec = &original.content["spec"];
    let selector = spec["selector"].clone(); // assume it's an object
    let ports = spec["ports"].clone(); // assume array of {port, targetPort,…}

    Service {
        metadata: k8s_openapi::apimachinery::pkg::apis::meta::v1::ObjectMeta {
            namespace: Some(original.meta.ns.clone()),
            name: Some(backend_name.to_string()),
            labels: Some(BTreeMap::from([
                ("app".into(), backend_name.into()),
                // prevent external clients accidentally using it:
                ("fault-proxy-backend".into(), "true".into()),
            ])),
            ..Default::default()
        },
        spec: Some(k8s_openapi::api::core::v1::ServiceSpec {
            selector: selector.as_object().map(|m| {
                m.iter()
                    .map(|(k, v)| (k.clone(), v.as_str().unwrap().to_string()))
                    .collect()
            }),
            ports: Some(
                ports
                    .as_array()
                    .unwrap()
                    .iter()
                    .map(|p| {
                        let port = p["port"].as_i64().unwrap() as i32;
                        let target_port =
                            p["targetPort"].as_i64().unwrap() as i32;
                        let svc_port = IntOrString::Int(target_port);
                        k8s_openapi::api::core::v1::ServicePort {
                            protocol: Some("TCP".into()),
                            port,
                            target_port: Some(svc_port),
                            ..Default::default()
                        }
                    })
                    .collect(),
            ),
            ..Default::default()
        }),
        ..Default::default()
    }
}

fn build_proxy_deployment(
    ns: &str,
    name: &str,
    labels: &BTreeMap<String, String>,
    config_map_name: &str,
    image: &str,
    proxy_port: i32,
    proxy_arg: String,
) -> Deployment {
    // fault proxy container
    let container = Container {
        name: name.into(),
        image: Some(image.into()),
        image_pull_policy: Some("Always".into()),
        tty: Some(true),
        args: Some(vec![
            "--log-stdout".into(),
            "--log-level".into(),
            "debug".into(),
            "run".into(),
            "--no-ui".into(),
            "--disable-http-proxy".into(),
            "--proxy".into(),
            proxy_arg,
        ]),
        ports: Some(vec![k8s_openapi::api::core::v1::ContainerPort {
            container_port: proxy_port,
            name: Some("proxy".into()),
            ..Default::default()
        }]),
        env_from: Some(vec![EnvFromSource {
            config_map_ref: Some(
                k8s_openapi::api::core::v1::ConfigMapEnvSource {
                    name: config_map_name.into(),
                    ..Default::default()
                },
            ),
            ..Default::default()
        }]),
        security_context: Some(k8s_openapi::api::core::v1::SecurityContext {
            allow_privilege_escalation: Some(false),
            read_only_root_filesystem: Some(true),
            privileged: Some(false),
            capabilities: Some(k8s_openapi::api::core::v1::Capabilities {
                drop: Some(vec!["ALL".into()]),
                ..Default::default()
            }),
            ..Default::default()
        }),
        ..Default::default()
    };

    Deployment {
        metadata: ObjectMeta {
            namespace: Some(ns.into()),
            name: Some(name.into()),
            labels: Some(labels.clone()),
            ..Default::default()
        },
        spec: Some(DeploymentSpec {
            replicas: Some(1),
            selector: LabelSelector {
                match_labels: Some(labels.clone()),
                ..Default::default()
            },
            template: k8s_openapi::api::core::v1::PodTemplateSpec {
                metadata: Some(ObjectMeta {
                    labels: Some(labels.clone()),
                    annotations: Some(BTreeMap::from([(
                        "sidecar.istio.io/inject".into(),
                        "false".into(),
                    )])),
                    ..Default::default()
                }),
                spec: Some(k8s_openapi::api::core::v1::PodSpec {
                    service_account_name: Some(name.into()),
                    security_context: Some(PodSecurityContext {
                        run_as_user: Some(65532),
                        run_as_group: Some(65532),
                        fs_group: Some(65532),
                        ..Default::default()
                    }),
                    containers: vec![container],
                    ..Default::default()
                }),
            },
            strategy: Some(DeploymentStrategy::default()),
            ..Default::default()
        }),
        ..Default::default()
    }
}

pub async fn inject_fault_proxy(
    client: Client,
    svc: &Resource,
    fault_settings: &mut BTreeMap<String, String>,
) -> Result<K8sSpecSnapshot> {
    let ns = &svc.meta.ns;
    let orig_name = &svc.meta.name;
    let backend_name = format!("{}-backend", orig_name);
    let proxy_name = format!("{}-proxy", orig_name);
    let proxy_port = 3180;

    // Create the backend Service
    let backend_svc = build_backend_service(svc, &backend_name);
    Api::<Service>::namespaced(client.clone(), ns)
        .create(&PostParams::default(), &backend_svc)
        .await?;

    // Prepare labels & config for the proxy
    let mut labels = BTreeMap::new();
    labels.insert("app".into(), proxy_name.clone());

    let mut cm_data = BTreeMap::new();
    cm_data.append(fault_settings);

    // Determine the original service's first port
    let orig_port =
        svc.content["spec"]["ports"][0]["port"].as_i64().unwrap() as i32;

    // Build each proxy object
    let sa = build_service_account(ns, &proxy_name, &labels);
    let cm = build_config_map(
        ns,
        &format!("{}-config", proxy_name),
        &labels,
        cm_data,
    );
    let proxy_arg = format!("{}={}:{}", proxy_port, backend_name, orig_port);
    let proxy_deploy = build_proxy_deployment(
        ns,
        &proxy_name,
        &labels,
        &cm.metadata.name.clone().unwrap(),
        "ghcr.io/rebound-how/fault:latest",
        proxy_port,
        proxy_arg,
    );

    // Create the proxy
    let pp = PostParams::default();
    Api::<ServiceAccount>::namespaced(client.clone(), ns)
        .create(&pp, &sa)
        .await?;
    Api::<ConfigMap>::namespaced(client.clone(), ns).create(&pp, &cm).await?;
    Api::<Deployment>::namespaced(client.clone(), ns)
        .create(&pp, &proxy_deploy)
        .await?;

    // Patch the original Service's selector to point at our proxy
    let svc_api: Api<Service> = Api::namespaced(client.clone(), ns);
    let orig_svc = svc_api.get(orig_name).await?;
    let original_selector =
        orig_svc.spec.and_then(|s| s.selector).unwrap_or_default();

    let orig_ports = svc.content["spec"]["ports"]
        .as_array()
        .expect("service must have ports");

    let patched_ports: Vec<_> = orig_ports
        .iter()
        .map(|p| {
            json!({
                "port": p["port"].as_i64().unwrap(),
                "protocol": p.get("protocol").cloned().unwrap_or(json!("TCP")),
                "targetPort": proxy_port,
                "name": p.get("name").cloned().unwrap_or_default(),
            })
        })
        .collect();

    let patch = json!({ "spec": { "selector": labels.clone(), "ports": patched_ports } });
    svc_api
        .patch(
            orig_name,
            &PatchParams::apply("fault-injector"),
            &Patch::Merge(patch),
        )
        .await?;

    let snapshot = K8sSpecSnapshot {
        selector: original_selector,
        ports: orig_ports.to_vec(),
    };

    Ok(snapshot)
}

/// Roll back: restore the Service selector, delete proxy objects & backend
/// Service
pub async fn rollback_fault_injection(
    client: Client,
    svc: &Resource,
    original_snapshot: K8sSpecSnapshot,
) -> Result<()> {
    let ns = &svc.meta.ns;
    let orig_name = &svc.meta.name;
    let backend_name = format!("{}-backend", orig_name);
    let proxy_name = format!("{}-proxy", orig_name);

    // Patch the original Service back
    let svc_api: Api<Service> = Api::namespaced(client.clone(), ns);
    let pp = PatchParams::apply("fault-injector");
    let patch = json!({ "spec": { "selector": original_snapshot.selector, "ports": original_snapshot.ports }});
    svc_api.patch(orig_name, &pp, &Patch::Merge(patch)).await?;

    //Delete all injected artifacts
    let dp = DeleteParams::default();
    let sa_api = Api::<ServiceAccount>::namespaced(client.clone(), ns);
    let cm_api = Api::<ConfigMap>::namespaced(client.clone(), ns);
    let deploy_api = Api::<Deployment>::namespaced(client.clone(), ns);
    let backend_api = Api::<Service>::namespaced(client.clone(), ns);

    // best‐effort deletes, ignoring "not found"
    let _ = sa_api.delete(&proxy_name, &dp).await;
    let _ = cm_api.delete(&format!("{}-config", proxy_name), &dp).await;
    let _ = deploy_api.delete(&proxy_name, &dp).await;
    let _ = backend_api.delete(&backend_name, &dp).await;

    Ok(())
}
