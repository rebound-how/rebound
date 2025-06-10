// src/discovery.rs
use anyhow::Result;
use chrono::Utc;
use google_cloud_gax::paginator::ItemPaginator;
use google_cloud_run_v2::client::Services;
use serde_json::Value;

use crate::discovery::types::Meta;
use crate::discovery::types::Resource;

pub async fn discover_cloud_run_resources(
    project: &str,
    region: &str,
) -> Result<Vec<Resource>> {
    let client = Services::builder().build().await?;

    let parent = format!("projects/{}/locations/{}", project, region);
    let builder = client.list_services().set_parent(&parent);

    let mut out = Vec::new();

    let mut items = builder.by_item();
    while let Some(result) = items.next().await {
        let item = result?;

        let content = serde_json::to_value(&item)?;

        let name = item.name;

        let id = name.rsplit('/').next().unwrap_or(&name).to_string();

        out.push(Resource {
            id: id.clone(),
            meta: Meta {
                name: id.clone(),
                ns: region.to_string(),
                display: format!("CloudRun/{}/{}", region, name),
                dt: Utc::now(),
                kind: "cloudrun".into(),
                category: "serverless".into(),
                platform: Some("gcp".into()),
                project: Some(project.to_string()),
                region: Some(region.to_string()),
            },
            links: Vec::new(),
            content,
        });
    }

    Ok(out)
}
