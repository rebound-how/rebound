use std::collections::BTreeMap;
use std::time::Duration;
use std::time::Instant;

use anyhow::Result;
use anyhow::anyhow;
use async_trait::async_trait;
use google_cloud_longrunning::client::Operations;
use google_cloud_run_v2::client::Services;
use google_cloud_run_v2::model::Container;
use google_cloud_run_v2::model::ContainerPort;
use google_cloud_run_v2::model::EnvVar;
use google_cloud_run_v2::model::RevisionTemplate;
use google_cloud_run_v2::model::TrafficTarget;
use google_cloud_run_v2::model::TrafficTargetAllocationType;
use rand::Rng;
use tokio::time::sleep;

use crate::discovery::gcp::discover_cloud_run_resources;
use crate::discovery::types::Resource;
use crate::inject::InjectionHandle;
use crate::inject::Platform;
use crate::inject::ServiceResource;

pub struct CloudRunPlatform {
    project: String,
    region: String,
    service_name: String,
    traffic_percent: u32,
    container_image: String,
    fault_settings: Option<BTreeMap<String, String>>,
    resources: Vec<Resource>,
    injection_handle: Option<InjectionHandle>,
}

impl CloudRunPlatform {
    pub async fn new_proxy(
        project: &str,
        region: &str,
        service: &str,
        traffic_percent: u32,
        container_image: String,
        fault_settings: BTreeMap<String, String>,
    ) -> Result<Self> {
        let resources = discover_cloud_run_resources(project, region).await?;
        Ok(Self {
            project: project.into(),
            region: region.into(),
            service_name: service.into(),
            traffic_percent: traffic_percent.min(100),
            container_image,
            fault_settings: Some(fault_settings),
            resources,
            injection_handle: None,
        })
    }

    fn cached_services(&self) -> Vec<ServiceResource> {
        self.resources
            .iter()
            .filter(|r| r.meta.kind == "Service")
            .map(|r| ServiceResource {
                name: r.meta.name.clone(),
                address: r.content["uri"]
                    .as_str()
                    .unwrap_or(&r.meta.name)
                    .to_string(),
            })
            .collect()
    }
}

#[async_trait]
impl Platform for CloudRunPlatform {
    async fn discover(&self) -> Result<Vec<ServiceResource>> {
        Ok(self.cached_services())
    }

    fn set_service(&mut self, service: &str) -> Result<()> {
        if self.resources.iter().any(|r| r.meta.name == service) {
            self.service_name = service.into();
            Ok(())
        } else {
            Err(anyhow!("service `{}` not found", service))
        }
    }

    async fn get_service(&self) -> Result<ServiceResource> {
        let r = self
            .resources
            .iter()
            .find(|r| r.meta.name == self.service_name)
            .ok_or_else(|| anyhow!("no service selected"))?;
        let addr =
            r.content["uri"].as_str().unwrap_or(&r.meta.name).to_string();
        Ok(ServiceResource { name: r.meta.name.clone(), address: addr })
    }

    async fn inject(&mut self) -> Result<()> {
        let svc = self.get_service().await?;
        let name = format!(
            "projects/{}/locations/{}/services/{}",
            self.project, self.region, svc.name
        );

        tracing::debug!("Injecting into {}", name);

        let client = Services::builder().build().await?;

        let mut builder = client.get_service();
        builder = builder.set_name(&name);

        let mut service = builder.send().await?;

        let old = service.template.clone();
        let token = serde_json::to_string(&old)?;

        if let Some(ref mut template) = service.template {
            if let Some(main_ct) = template.containers.first_mut() {
                let mut main_port = 8080i32;

                if main_ct.ports.len() > 0 {
                    let port = main_ct.ports.remove(0);
                    main_port = port.container_port;
                }

                let fault_port = random_port();

                let mut container = Container::default();
                container = container.set_name("fault-proxy".to_string());
                container = container.set_image(self.container_image.clone());
                container = container.set_args(vec![
                    "--log-stdout".into(),
                    "--log-level".into(),
                    "debug".into(),
                    "run".into(),
                    "--no-ui".into(),
                    "--disable-http-proxy".into(),
                    "--upstream".into(),
                    "*".into(),
                    "--proxy".into(),
                    format!("{}=127.0.0.1:{}", fault_port, main_port),
                ]);

                let vars = self
                    .fault_settings
                    .clone()
                    .unwrap()
                    .iter()
                    .map(|(k, v)| {
                        let mut env = EnvVar::default();
                        env = env.set_name(k);
                        env = env.set_value(v);
                        env
                    })
                    .collect::<Vec<EnvVar>>();

                container = container.set_env(vars);

                let mut new_ct_port = ContainerPort::default();
                new_ct_port = new_ct_port.set_name("http1".to_string());
                new_ct_port = new_ct_port.set_container_port(fault_port);
                container = container.set_ports(vec![new_ct_port]);

                container =
                    container.set_depends_on(vec![main_ct.name.clone()]);

                template.containers.push(container);
            }

            let mut new_target = TrafficTarget::default();
            new_target.r#type = TrafficTargetAllocationType::Latest;
            new_target.percent = self.traffic_percent as i32;

            service.traffic = vec![new_target];

            let mut builder = client.update_service();
            builder = builder.set_service(service);
            let op = builder.send().await?;

            tracing::debug!("Operation {}", op.name);

            self.injection_handle =
                Some(InjectionHandle::CloudRun { rollback_token: token, op });
        }

        Ok(())
    }

    async fn rollback(&mut self) -> Result<()> {
        if let Some(InjectionHandle::CloudRun { rollback_token, op }) =
            self.injection_handle.take()
        {
            let svc = self.get_service().await?;
            let name = format!(
                "projects/{}/locations/{}/services/{}",
                self.project, self.region, svc.name
            );

            let client = Services::builder().build().await?;

            let old: RevisionTemplate = serde_json::from_str(&rollback_token)?;

            let mut builder = client.get_service();
            builder = builder.set_name(&name);

            let mut service = builder.send().await?;

            let mut new_target = TrafficTarget::default();
            new_target.r#type = TrafficTargetAllocationType::Latest;
            new_target.percent = 100i32;

            service.traffic = vec![new_target];
            service.template = Some(old);

            let mut builder = client.update_service();
            builder = builder.set_service(service);
            let op = builder.send().await?;

            self.injection_handle =
                Some(InjectionHandle::CloudRun { rollback_token, op });
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
        if let Some(InjectionHandle::CloudRun { rollback_token: _, op }) =
            self.injection_handle.take()
        {
            let start = Instant::now();
            let timeout = Duration::from_secs(120);
            let interval = Duration::from_secs(2);

            let client = Operations::builder().build().await?;

            loop {
                tracing::debug!("Waiting on operation {}", op.name);

                // it appears this has a bug has it always returns a 404
                let mut builder = client.get_operation();
                builder = builder.set_name(op.name.clone());

                let op = builder.send().await?;

                if op.done {
                    tracing::debug!("Service revision updated");
                    return Ok(());
                }

                if start.elapsed() > timeout {
                    return Err(anyhow!(
                        "timed out waiting for GCP operation `{}` to complete",
                        op.name.clone()
                    ));
                }

                sleep(interval).await;
            }
        }

        Ok(())
    }

    async fn wait_cleanup(&mut self) -> Result<()> {
        if let Some(InjectionHandle::CloudRun { rollback_token: _, op }) =
            self.injection_handle.take()
        {
            let start = Instant::now();
            let timeout = Duration::from_secs(120);
            let interval = Duration::from_secs(2);

            let client = Operations::builder().build().await?;

            loop {
                let mut builder = client.get_operation();
                builder = builder.set_name(op.name.clone());

                let op = builder.send().await?;

                if op.done {
                    return Ok(());
                }

                if start.elapsed() > timeout {
                    return Err(anyhow!(
                        "timed out waiting for GCP operation `{}` to complete",
                        op.name.clone()
                    ));
                }

                sleep(interval).await;
            }
        }

        Ok(())
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

fn random_port() -> i32 {
    let mut rng = rand::rng();
    rng.random_range(50000..=55000)
}
