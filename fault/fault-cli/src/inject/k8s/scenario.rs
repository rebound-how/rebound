use std::collections::BTreeMap;

use anyhow::Result;
use json_patch::Patch as JsonPatch;
use k8s_openapi::api::apps::v1::Deployment;
use k8s_openapi::api::apps::v1::DeploymentSpec;
use k8s_openapi::api::apps::v1::DeploymentStrategy;
use k8s_openapi::api::core::v1::ConfigMap;
use k8s_openapi::api::core::v1::ConfigMapVolumeSource;
use k8s_openapi::api::core::v1::Container;
use k8s_openapi::api::core::v1::PodSecurityContext;
use k8s_openapi::api::core::v1::Service;
use k8s_openapi::api::core::v1::ServiceAccount;
use k8s_openapi::api::core::v1::Volume;
use k8s_openapi::api::core::v1::VolumeMount;
use k8s_openapi::apimachinery::pkg::apis::meta::v1::LabelSelector;
use k8s_openapi::apimachinery::pkg::apis::meta::v1::ObjectMeta;
use k8s_openapi::apimachinery::pkg::util::intstr::IntOrString;
use kube::Api;
use kube::Client;
use kube::api::DeleteParams;
use kube::api::Patch;
use kube::api::PatchParams;
use kube::api::PostParams;
use serde_json::from_value;
use serde_json::json;

use crate::discovery::types::K8sSpecSnapshot;
use crate::discovery::types::Resource;

pub async fn inject_fault_scenario(
    client: Client,
    svc: &Resource,
    scenario: String,
    container_image: String,
    api_address: String,
) -> Result<K8sSpecSnapshot> {
    let ns = &svc.meta.ns;
    let orig_name = &svc.meta.name;
    let backend_name = format!("{}-backend", orig_name);
    let proxy_name = format!("{}-proxy", orig_name);

    // Create the backend Service
    let backend_svc = build_backend_service(svc, &backend_name);
    Api::<Service>::namespaced(client.clone(), ns)
        .create(&PostParams::default(), &backend_svc)
        .await?;

    // Prepare labels & config for the proxy
    let mut labels = BTreeMap::new();
    labels.insert("app".into(), proxy_name.clone());

    // Determine the original service's first port
    let orig_port =
        svc.content["spec"]["ports"][0]["port"].as_i64().unwrap() as i32;

    // Build each proxy object
    let sa = build_service_account(ns, &proxy_name, &labels);
    let cm = build_config_map(
        ns,
        &format!("{}-config", proxy_name),
        &labels,
        scenario,
    );
    let proxy_deploy = build_scenario_deployment(
        ns,
        &proxy_name,
        &labels,
        &cm.metadata.name.clone().unwrap(),
        &container_image,
        api_address,
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

    //let patch = json!({ "spec": { "selector": labels.clone(), "ports":
    // patched_ports } });
    let patch: JsonPatch = from_value(json!([
        {
          "op": "replace",
          "path": "/spec/selector",
          "value":  labels
        },
    ]))
    .unwrap();

    svc_api
        .patch(orig_name, &PatchParams::default(), &Patch::Json::<()>(patch))
        .await?;

    let snapshot =
        K8sSpecSnapshot { selector: original_selector, ports: Vec::new() };

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

    let patch: JsonPatch = from_value(json!([
        {
          "op": "replace",
          "path": "/spec/selector",
          "value":  original_snapshot.selector
        },
        {
          "op": "replace",
          "path": "/spec/ports",
          "value": original_snapshot.ports
        }
    ]))
    .unwrap();

    svc_api.patch(orig_name, &pp, &Patch::Json::<()>(patch)).await?;

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

//////////////////////////////////////////////////////////////////////////////
/// Private functions
//////////////////////////////////////////////////////////////////////////////

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

fn build_config_map(
    ns: &str,
    name: &str,
    labels: &BTreeMap<String, String>,
    scenario: String,
) -> ConfigMap {
    let mut data = BTreeMap::new();
    data.insert("scenario.yaml".to_string(), scenario);

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

fn build_scenario_deployment(
    ns: &str,
    name: &str,
    labels: &BTreeMap<String, String>,
    config_map_name: &str,
    image: &str,
    api_adress: String,
) -> Deployment {
    let cm_volume = Volume {
        name: "scenario-cm".into(),
        config_map: Some(ConfigMapVolumeSource {
            name: config_map_name.into(),
            ..Default::default()
        }),
        ..Default::default()
    };

    let cm_mount = VolumeMount {
        name: "scenario-cm".into(),
        mount_path: "/home/nonroot/scenario".into(),
        read_only: Some(true),
        ..Default::default()
    };

    let container = Container {
        name: name.into(),
        image: Some(image.into()),
        image_pull_policy: Some("Always".into()),
        tty: Some(true),
        args: Some(vec![
            "--log-stdout".into(),
            "--log-level".into(),
            "debug".into(),
            "scenario".into(),
            "run".into(),
            "--api-address".into(),
            format!("http://{}", api_adress),
            "--scenario".into(),
            "/home/nonroot/scenario/scenario.file".into(),
        ]),
        volume_mounts: Some(vec![cm_mount]),
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
                    volumes: Some(vec![cm_volume]),
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
