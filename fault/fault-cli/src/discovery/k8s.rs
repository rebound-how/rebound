use std::collections::HashSet;
use std::collections::VecDeque;

use anyhow::Result;
use chrono::DateTime;
use chrono::Utc;
use jsonpath_rust::query::QueryRef;
use jsonpath_rust::query::js_path;
use k8s_openapi::api::core::v1::Pod;
use k8s_openapi::api::core::v1::Service;
use kube::Api;
use kube::Client;
use kube::Resource as KubeResource;
use kube::ResourceExt;
use kube::api::ListParams;
use kube::core::NamespaceResourceScope;
use serde::Serialize;
use serde::de::DeserializeOwned;
use serde_json::Value;

use super::types::Link;
use super::types::Meta;
use super::types::Resource;

pub async fn discover_kubernetes_resources(
    namespace: &str,
) -> Result<Vec<Resource>> {
    let client = Client::try_default().await?;

    let resources = list_resources(client, namespace).await?;

    Ok(resources)
}

async fn list_resources(
    client: Client,
    namespace: &str,
) -> Result<Vec<Resource>> {
    let lp = ListParams::default();

    let pods: Vec<Resource> = {
        let api: Api<Pod> = api_for(client.clone(), namespace);
        let objs = api.list(&lp).await?;
        futures::future::join_all(objs.into_iter().map(obj_to_resource))
            .await
            .into_iter()
            .collect::<Result<_, _>>()?
    };

    let svcs: Vec<Resource> = {
        let api: Api<Service> = api_for(client.clone(), namespace);
        let objs = api.list(&lp).await?;
        futures::future::join_all(objs.into_iter().map(obj_to_resource))
            .await
            .into_iter()
            .collect::<Result<_, _>>()?
    };

    // small temporary in-memory meta holder for querying
    let mut all = serde_json::json!({ "resources": [] });
    for r in svcs.iter().chain(pods.iter()) {
        let mut entry = serde_json::to_value(r)?;
        entry
            .as_object_mut()
            .unwrap()
            .insert("links".into(), serde_json::to_value(&r.links)?);
        all["resources"].as_array_mut().unwrap().push(entry);
    }

    let mut services_to_link: Vec<(
        String,
        String,
        serde_json::Map<String, Value>,
    )> = Vec::new();
    let services: Vec<QueryRef<Value>> =
        js_path("$.resources[? @.meta.kind=='Service']", &all)?;

    for svc in services {
        let svc_obj = svc.val();
        let service_id = svc_obj["id"].as_str().unwrap().to_string();
        let ns = svc_obj["meta"]["ns"].as_str().unwrap().to_string();
        let selectors = svc_obj["content"]["spec"]["selector"]
            .as_object()
            .cloned()
            .unwrap_or_default();
        if !selectors.is_empty() {
            services_to_link.push((service_id, ns, selectors));
        }
    }

    for (service_id, ns, selectors) in services_to_link {
        // build your label filter
        let label_expr = selectors
            .iter()
            .map(|(k, v)| {
                format!(
                    "@.content.metadata.labels['{k}']=='{val}'",
                    k = k,
                    val = v.as_str().unwrap()
                )
            })
            .collect::<Vec<_>>()
            .join(" && ");

        let pod_filter = format!(
            "$.resources[? @.meta.kind=='Pod' \
            && @.meta.ns=='{ns}' \
            && {labels} ]",
            ns = ns,
            labels = label_expr
        );

        let pods: Vec<QueryRef<Value>> = js_path(&pod_filter, &all)?;
        // collect just the pod IDs into a Vec<String>
        let pod_ids: Vec<String> = pods
            .iter()
            .filter_map(|pod_ref| {
                pod_ref
                    .clone()
                    .val()
                    .as_object()
                    .and_then(|o| o.get("id"))
                    .and_then(|v| v.as_str())
                    .map(ToString::to_string)
            })
            .collect();

        for pod_id in pod_ids {
            // Service -> Pod
            add_link_to(
                &mut all,
                &service_id,
                Link {
                    direction: "out".into(),
                    kind: "Pod".into(),
                    path: "$.content.metadata.name".into(),
                    pointer: "$.content.metadata.uid".into(),
                    id: pod_id.clone(),
                },
            )?;

            // Pod -> Service
            add_link_to(
                &mut all,
                &pod_id,
                Link {
                    direction: "in".into(),
                    kind: "Service".into(),
                    path: "$.content.metadata.name".into(),
                    pointer: "$.content.metadata.uid".into(),
                    id: service_id.clone(),
                },
            )?;
        }
    }

    let out: Vec<Resource> =
        serde_json::from_value(serde_json::json!(&all["resources"]))?;
    Ok(out)
}

async fn obj_to_resource<K>(obj: K) -> Result<Resource>
where
    K: ResourceExt + KubeResource + Serialize,
    <K as KubeResource>::DynamicType: Default,
{
    let meta = obj.meta();

    let content = serde_json::to_value(&obj)?;
    let name = meta.name.clone().unwrap();
    let ns = meta.namespace.clone().unwrap_or_default();
    let kind = <K as KubeResource>::kind(&Default::default()).to_string();
    let uid = meta.uid.clone().unwrap_or_default();
    let dt = meta
        .creation_timestamp
        .as_ref()
        .map(|t| {
            DateTime::parse_from_rfc3339(&t.0.to_rfc3339())
                .unwrap()
                .with_timezone(&Utc)
        })
        .unwrap_or_else(Utc::now);
    let display = format!("{}.{}/{}", kind, ns, name);
    let category = match kind.as_str() {
        "Pod" => "compute".to_string(),
        "Service" => "networking".to_string(),
        other => other.to_lowercase(),
    }
    .to_string();

    let links = vec![Link {
        direction: "parent".into(),
        kind: "Namespace".into(),
        path: "$.metadata.namespace".into(),
        pointer: "$.metadata.name".into(),
        id: ns.clone(),
    }];

    Ok(Resource {
        id: uid.clone(),
        meta: Meta {
            name,
            ns,
            display,
            dt,
            kind,
            category,
            platform: None,
            region: None,
            project: None,
        },
        links,
        content,
    })
}

fn add_link_to(all: &mut Value, target_id: &str, link: Link) -> Result<()> {
    // Look up the top‐level "resources" array
    if let Some(resources) =
        all.get_mut("resources").and_then(Value::as_array_mut)
    {
        // Find each entry whose "id" == target_id
        for entry in resources.iter_mut() {
            if entry.get("id").and_then(Value::as_str) == Some(target_id) {
                // Ensure there's a "links" array
                if let Some(links_arr) =
                    entry.get_mut("links").and_then(Value::as_array_mut)
                {
                    // Push our new link
                    links_arr.push(serde_json::to_value(&link)?);
                }
            }
        }
    }
    Ok(())
}

fn api_for<K>(client: Client, namespace: &str) -> Api<K>
where
    K: KubeResource<Scope = NamespaceResourceScope> + DeserializeOwned,
    <K as KubeResource>::DynamicType: Default,
{
    Api::namespaced(client, namespace)
}
