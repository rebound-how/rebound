use std::collections::BTreeMap;
use std::time::Duration;
use std::time::Instant;

use anyhow::Result;
use anyhow::anyhow;
use async_trait::async_trait;
use aws_config::BehaviorVersion;
use aws_sdk_ecs::Client as EcsClient;
use aws_sdk_ecs::types::ContainerDefinition;
use aws_sdk_ecs::types::KeyValuePair;
use aws_sdk_ecs::types::LoadBalancer;
use aws_sdk_ecs::types::NetworkMode;
use aws_sdk_ecs::types::PortMapping;
use rand::Rng;
use tokio::time::sleep;

use crate::discovery::aws::discover_ecs_resources;
use crate::discovery::types::Resource;
use crate::inject::InjectionHandle;
use crate::inject::Platform;
use crate::inject::ServiceResource;

#[derive(serde::Serialize, serde::Deserialize)]
struct LambdaSnapshot {
    primary_version: String,
    additional_weights: Option<BTreeMap<String, f64>>,
}

pub struct EcsPlatform {
    client: EcsClient,
    cluster: String,
    region: String,
    service_name: String,
    resources: Vec<Resource>,
    fault_image: String,
    fault_settings: Option<BTreeMap<String, String>>,
    injection_handle: Option<InjectionHandle>,
}

#[derive(serde::Serialize, serde::Deserialize)]
struct LB {
    target_group_arn: String,
    container_name: String,
    container_port: i32,
}

impl EcsPlatform {
    pub async fn new_proxy(
        region: &str,
        cluster: &str,
        service_name: &str,
        fault_image: String,
        fault_settings: BTreeMap<String, String>,
    ) -> Result<Self> {
        let config = aws_config::load_defaults(BehaviorVersion::latest()).await;
        let client = EcsClient::new(&config);
        let resources = discover_ecs_resources(&cluster).await?;
        Ok(Self {
            client,
            cluster: cluster.into(),
            region: region.into(),
            service_name: service_name.into(),
            resources,
            fault_image,
            fault_settings: Some(fault_settings),
            injection_handle: None,
        })
    }

    fn find_selected(&self) -> Result<&Resource> {
        self.resources
            .iter()
            .find(|r| r.meta.name == self.service_name)
            .ok_or_else(|| anyhow!("Service `{}` not found", self.service_name))
    }

    fn to_service_resource(r: &Resource) -> ServiceResource {
        ServiceResource { name: r.meta.name.clone(), address: r.id.clone() }
    }

    fn random_proxy_port() -> i32 {
        let mut rng = rand::rng();
        rng.random_range(50000..=55000)
    }
}

#[async_trait]
impl Platform for EcsPlatform {
    async fn discover(&self) -> Result<Vec<ServiceResource>> {
        Ok(self.resources.iter().map(Self::to_service_resource).collect())
    }

    fn set_service(&mut self, service: &str) -> Result<()> {
        if self.resources.iter().any(|r| r.meta.name == service) {
            self.service_name = service.to_string();
            Ok(())
        } else {
            Err(anyhow!("ECS service `{}` not found", service))
        }
    }

    async fn get_service(&self) -> Result<ServiceResource> {
        let r = self.find_selected()?;
        tracing::debug!("ECS service selected: {}", r);
        Ok(Self::to_service_resource(r))
    }

    async fn inject(&mut self) -> Result<()> {
        let svc = self.get_service().await?;
        let desc = self
            .client
            .describe_services()
            .cluster(&self.cluster)
            .services(&svc.name)
            .send()
            .await?;
        let ecs_svc = desc
            .services
            .as_ref()
            .and_then(|s| s.first())
            .ok_or_else(|| anyhow!("Service not found"))?;
        let old_td = ecs_svc.task_definition.clone().unwrap();
        let old_lbs: Vec<LB> = ecs_svc
            .load_balancers
            .clone()
            .unwrap_or_default()
            .iter()
            .map(|lb| LB {
                target_group_arn: lb.target_group_arn.as_ref().unwrap().clone(),
                container_name: lb.container_name.as_ref().unwrap().clone(),
                container_port: lb.container_port.unwrap(),
            })
            .collect();

        let td = self
            .client
            .describe_task_definition()
            .task_definition(&old_td)
            .send()
            .await?
            .task_definition
            .unwrap();

        let proxy_port = Self::random_proxy_port();

        let vars: Vec<KeyValuePair> = self
            .fault_settings
            .clone()
            .unwrap()
            .iter()
            .map(|(k, v)| {
                KeyValuePair::builder()
                    .set_name(Some(k.into()))
                    .set_value(Some(v.into()))
                    .build()
            })
            .collect::<Vec<KeyValuePair>>();

        let mut containers =
            td.container_definitions.clone().unwrap_or_default();
        let app_ct = &containers[0];

        let main_port = app_ct
            .port_mappings
            .as_ref()
            .and_then(|ports| ports.first())
            .and_then(|p| p.container_port)
            .ok_or_else(|| anyhow!("No port mapping found on container"))?;

        let mut fault_builder = ContainerDefinition::builder()
            .name("fault-proxy")
            .image(&self.fault_image)
            .essential(false)
            .port_mappings(
                PortMapping::builder()
                    .container_port(proxy_port)
                    .host_port(proxy_port)
                    .build(),
            )
            .set_environment(Some(vars))
            .set_command(Some(vec![
                "--log-stdout".into(),
                "--log-level".into(),
                "debug".into(),
                "run".into(),
                "--no-ui".into(),
                "--disable-http-proxy".into(),
                "--upstream".into(),
                "*".into(),
                "--proxy".into(),
                format!("{}=127.0.0.1:{}", proxy_port, main_port),
            ]));

        if let Some(log_cfg) = app_ct.log_configuration.clone() {
            fault_builder = fault_builder.log_configuration(log_cfg);
        }

        let fault_ct = fault_builder.build();

        containers[0] = ContainerDefinition::builder()
            .set_name(app_ct.name.clone())
            .set_image(app_ct.image.clone())
            .set_port_mappings(app_ct.port_mappings.clone())
            .set_cpu(Some(app_ct.cpu))
            .set_memory(app_ct.memory)
            .set_entry_point(app_ct.entry_point.clone())
            .set_command(app_ct.command.clone())
            .set_log_configuration(app_ct.log_configuration.clone())
            .essential(true)
            .build();
        containers.push(fault_ct);

        let updated_lbs = ecs_svc
            .load_balancers
            .as_ref()
            .unwrap()
            .iter()
            .map(|lb| {
                LoadBalancer::builder()
                    .target_group_arn(lb.target_group_arn.as_ref().unwrap())
                    .container_name("fault-proxy")
                    .container_port(proxy_port)
                    .build()
            })
            .collect::<Vec<_>>();

        let register_resp = self
            .client
            .register_task_definition()
            .family(td.family.unwrap())
            .network_mode(NetworkMode::from(td.network_mode.unwrap().as_str()))
            .set_cpu(td.cpu.clone())
            .set_memory(td.memory.clone())
            .set_execution_role_arn(td.execution_role_arn.clone())
            .set_task_role_arn(td.task_role_arn.clone())
            .set_container_definitions(Some(containers))
            .send()
            .await?;

        let new_td =
            register_resp.task_definition.unwrap().task_definition_arn.unwrap();

        tracing::info!("Task Def {}", new_td);

        self.client
            .update_service()
            .cluster(&self.cluster)
            .service(&svc.name)
            .task_definition(&new_td)
            .set_load_balancers(Some(updated_lbs))
            .send()
            .await?;

        // 7) Save old_td for rollback
        self.injection_handle = Some(InjectionHandle::Ecs {
            rollback_token: old_td,
            lbs: serde_json::to_string(&old_lbs)?,
        });

        Ok(())
    }

    async fn rollback(&mut self) -> Result<()> {
        if let Some(InjectionHandle::Ecs { rollback_token, lbs }) =
            self.injection_handle.take()
        {
            let svc = self.get_service().await?;

            let lbs: Vec<LB> = serde_json::from_str(&lbs)?;
            let original_lbs = lbs
                .iter()
                .map(|slb| {
                    LoadBalancer::builder()
                        .target_group_arn(&slb.target_group_arn)
                        .container_name(&slb.container_name)
                        .container_port(slb.container_port)
                        .build()
                })
                .collect::<Vec<_>>();

            self.client
                .update_service()
                .cluster(&self.cluster)
                .service(&svc.name)
                .task_definition(&rollback_token)
                .set_load_balancers(Some(original_lbs.clone()))
                .send()
                .await?;
        }
        Ok(())
    }

    async fn update_fault_settings(
        &mut self,
        settings: &mut BTreeMap<String, String>,
    ) -> Result<()> {
        self.rollback().await?;
        self.fault_settings = Some(settings.clone());
        self.inject().await
    }

    async fn wait_ready(&mut self) -> Result<()> {
        let svc = self.get_service().await?;
        let start = Instant::now();
        let timeout = Duration::from_secs(120);
        let interval = Duration::from_secs(2);

        loop {
            let desc = self
                .client
                .describe_services()
                .cluster(&self.cluster)
                .services(&svc.name)
                .send()
                .await?;
            let s = desc.services.as_ref().unwrap()[0].clone();
            if s.running_count == s.desired_count {
                return Ok(());
            }
            if start.elapsed() > timeout {
                return Err(anyhow!(
                    "Timed out waiting for ECS service to stabilize"
                ));
            }
            sleep(interval).await;
        }
    }

    async fn wait_cleanup(&mut self) -> Result<()> {
        self.wait_ready().await
    }

    fn get_concrete_resources(&self) -> &Vec<Resource> {
        &self.resources
    }

    fn get_concrete_service(&self) -> &Resource {
        self.find_selected().unwrap()
    }
}
