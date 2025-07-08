use anyhow::Result;
use aws_config::BehaviorVersion;
use aws_sdk_ecs::Client as EcsClient;
use chrono::DateTime;
use chrono::Utc;
use serde_json::json;

use crate::discovery::types::Link;
use crate::discovery::types::Meta;
use crate::discovery::types::Resource;

pub async fn discover_ecs_resources(cluster: &str) -> Result<Vec<Resource>> {
    let config = aws_config::load_defaults(BehaviorVersion::latest()).await;
    let ecs = EcsClient::new(&config);

    let list_resp = ecs.list_services().cluster(cluster).send().await?;
    let service_arns = list_resp.service_arns.unwrap_or_default();

    let desc = ecs
        .describe_services()
        .cluster(cluster)
        .set_services(Some(service_arns.clone()))
        .send()
        .await?;

    let mut out = Vec::new();
    for svc in desc.services.unwrap_or_default().into_iter() {
        let name = svc.service_name.clone().unwrap_or_default();
        let arn = svc.service_arn.clone().unwrap_or_default();

        let content = json!({
            "serviceName":     svc.service_name,
            "serviceArn":      svc.service_arn,
            "clusterArn":      svc.cluster_arn,
            "taskDefinition":  svc.task_definition,
            "desiredCount":    svc.desired_count,
            "runningCount":    svc.running_count,
            "pendingCount":    svc.pending_count,
            "launchType":      svc.launch_type.map(|lt| lt.as_str().to_string()),
        });

        let dt: DateTime<Utc> = Utc::now();
        let display = format!("ecs/{}/{}", cluster, name);
        let meta = Meta {
            name: name.clone(),
            ns: cluster.into(),
            display,
            dt,
            kind: "Service".into(),
            category: "compute".into(),
            platform: Some("ecs".into()),
            region: None,
            project: None,
        };

        let links: Vec<Link> = Vec::new();

        out.push(Resource { id: arn.clone(), meta, links, content });
    }

    Ok(out)
}
