import asyncio
import base64
import logging
import secrets
from typing import Any, Dict, List, Tuple, Union, cast
from urllib.parse import urlparse

import msgspec
from kubernetes import client, config
from ruamel.yaml import YAML

from reliably_app import agent, deployment, environment, integration, token
from reliably_app.config import get_settings
from reliably_app.database import SessionLocal
from reliably_app.plan import crud, schemas
from reliably_app.plan.errors import PlanFailedError

__all__ = ["delete_plan", "execute_plan"]

logger = logging.getLogger("reliably_app")


async def execute_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
    env: environment.schemas.Environment | None,
    integrations: List[integration.schemas.IntegrationFull],
    org_id: str,
    user_id: str,
) -> None:
    from reliably_app.background import add_background_async_task, event

    logger.info(f"Executing plan {str(plan.id)} locally")

    tk = await create_agent_token(str(plan.id), org_id, user_id)

    timezone: str | None = None
    pattern: str | None = None
    is_cron = False
    if plan.definition.schedule.type == "cron":
        pattern = plan.definition.schedule.pattern
        timezone = plan.definition.schedule.timezone
        is_cron = True

    d = cast(
        deployment.schemas.DeploymentKubernetesJobDefinition, dep.definition
    )

    job_name = get_job_name(plan, is_cron)

    await asyncio.to_thread(
        apply_job,
        d,
        tk,
        org_id,
        user_id,
        str(plan.id),
        job_name,
        pattern,
        timezone,
    )

    plan_id = str(plan.id)
    add_background_async_task(
        supervise_job(
            event,
            d,
            plan_id,
            job_name,
            namespace=d.namespace,
            is_cron=False if pattern is None else True,
        ),
        name=f"Supervisor-k8s-{plan_id}",
    )


async def delete_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
    env: environment.schemas.Environment | None,
) -> None:
    plan_id = str(plan.id)
    logger.info(f"Deleting plan {plan_id} from local system")

    d = cast(
        deployment.schemas.DeploymentKubernetesJobDefinition, dep.definition
    )

    if not d.image and not d.manifest:
        raise PlanFailedError(
            plan_id, "deployment is missing image or manifest"
        )

    is_cron = plan.definition.schedule.type == "cron"
    await asyncio.to_thread(delete_job, d, plan_id, is_cron)


async def suspend_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
) -> None:
    logger.debug(f"Suspending Kubernetes job for plan {plan.id}")
    await asyncio.to_thread(
        switch_suspend_flag, suspend=True, plan=plan, dep=dep
    )


async def resume_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
) -> None:
    logger.debug(f"Resuming Kubernetes job for plan {plan.id}")
    await asyncio.to_thread(
        switch_suspend_flag, suspend=False, plan=plan, dep=dep
    )


###############################################################################
# Private functions
###############################################################################
async def create_agent_token(plan_id: str, org_id: str, user_id: str) -> str:
    secret_name = f"SECRET_{plan_id}"

    async with SessionLocal() as db:
        agt = await agent.crud.get_user_internal_agent(
            db,
            org_id,  # type: ignore
            user_id,  # type: ignore
        )
        if not agt:
            raise PlanFailedError(
                plan_id, "failed to lookup internal agent to run plan"
            )

        agt_token = await token.crud.get_by_token_name(db, secret_name)
        if not agt_token:
            tc = token.schemas.TokenCreate(name=secret_name)
            agt_token = await token.crud.create_token(
                db,
                org_id,  # type: ignore
                agt.user_id,  # type: ignore
                tc,
            )

        return cast(str, agt_token.token.decode("utf-8"))


def load_kubernetes_config(
    dep: deployment.schemas.DeploymentKubernetesJobDefinition,
) -> client.Configuration | None:
    if dep.use_in_cluster_credentials:
        logger.debug("Loading in cluster Kubernets config")
        config.load_incluster_config()
        return client.Configuration.get_default_copy()
    elif dep.credentials is not None:
        logger.debug("Loading deployment Kubernetes config")
        yaml = YAML(typ="safe")
        creds = dep.clear_credentials
        c = yaml.load(creds)

        loader = config.kube_config.KubeConfigLoader(
            config_dict=c, config_base_path=None
        )

        cfg = client.Configuration()
        loader.load_and_set(cfg)
        return cfg
    else:
        logger.debug("Loading local default Kubernetes config")
        config.load_kube_config()
        return client.Configuration.get_default_copy()


def apply_job(
    dep: deployment.schemas.DeploymentKubernetesJobDefinition,
    tk: str,
    org_id: str,
    user_id: str,
    plan_id: str,
    job_name: str,
    pattern: str | None,
    timezone: str | None,
) -> None:
    settings = get_settings()

    cfg = load_kubernetes_config(dep)
    api_client = client.ApiClient(configuration=cfg)

    name = job_name

    if pattern:
        job = create_cron_job(plan_id, dep, name, pattern, timezone)
    else:
        job = create_oneshot_job(plan_id, dep, name)

    add_labels(job, plan_id, org_id, name)

    pod_template = get_pod_template(job)
    add_environment_vars(pod_template["spec"], plan_id, user_id, org_id, tk)
    add_labels(pod_template, plan_id, org_id, name)

    if settings.DEPLOYMENT_STRATEGY == "k8s":
        secret = create_secret(job, tk, plan_id, name)
        add_labels(secret, plan_id, org_id, name)

        v1 = client.CoreV1Api(api_client=api_client)
        try:
            v1.create_namespaced_secret(
                namespace=dep.namespace,
                body=secret,
            )
        except client.rest.ApiException as e:
            logger.debug(
                f"Failed to create Kubernetes Secret: {str(e)}", exc_info=True
            )
            raise PlanFailedError(
                plan_id, "Failed to create Kubernetes secret for job"
            )

        logger.debug(
            f"Secret {name} has been created. Waiting 10s before we can use it "
            "from the job"
        )

    batchv1 = client.BatchV1Api(api_client=api_client)
    try:
        if pattern:
            batchv1.create_namespaced_cron_job(
                namespace=dep.namespace, body=job
            )
        else:
            batchv1.create_namespaced_job(namespace=dep.namespace, body=job)
    except client.rest.ApiException as e:
        logger.debug(
            f"Failed to create Kubernetes Job: {str(e)}", exc_info=True
        )
        raise PlanFailedError(plan_id, "Failed to create Kubernetes job")

    logger.debug(f"Job {name} has been created")


def delete_job(
    dep: deployment.schemas.DeploymentKubernetesJobDefinition,
    plan_id: str,
    is_cron: bool = False,
) -> None:
    settings = get_settings()

    cfg = load_kubernetes_config(dep)
    k8s_client = client.ApiClient(configuration=cfg)

    batchv1 = client.BatchV1Api(api_client=k8s_client)
    try:
        if is_cron:
            name = f"reliably-plan-{plan_id}"
            logger.debug(f"Deleting Kubernetes job {name}")

            batchv1.delete_namespaced_cron_job(
                name=name,
                namespace=dep.namespace,
                body=client.V1DeleteOptions(
                    propagation_policy="Foreground", grace_period_seconds=5
                ),
            )
        else:
            jobs = cast(
                client.V1JobList,
                batchv1.list_namespaced_job(
                    namespace=dep.namespace,
                    label_selector=f"reliably.com/plan={plan_id}",
                ),
            )

            for job in cast(List[client.V1Job], jobs.items):
                name = cast(client.V1ObjectMeta, job.metadata).name
                logger.debug(f"Deleting Kubernetes job {name}")
                batchv1.delete_namespaced_job(
                    name=name,
                    namespace=dep.namespace,
                    body=client.V1DeleteOptions(
                        propagation_policy="Foreground", grace_period_seconds=5
                    ),
                )
    except client.rest.ApiException as e:
        logger.debug(
            f"Failed to delete Kubernetes Job: {str(e)}", exc_info=True
        )

    if settings.DEPLOYMENT_STRATEGY == "k8s":
        logger.debug(f"Deleting Kubernetes secret {name}")
        v1 = client.CoreV1Api(api_client=k8s_client)
        try:
            v1.delete_namespaced_secret(
                name=name,
                namespace=dep.namespace,
                body=client.V1DeleteOptions(
                    propagation_policy="Foreground", grace_period_seconds=5
                ),
            )
        except client.rest.ApiException as e:
            logger.debug(
                f"Failed to delete Kubernetes Secret: {str(e)}", exc_info=True
            )


def add_labels(
    o: Dict[str, Any], plan_id: str, org_id: str, job_name: str
) -> None:
    md = o.setdefault("metadata", {})
    md["name"] = job_name

    labels = md.setdefault("labels", {})
    labels["reliably.com/plan"] = plan_id
    labels["reliably.com/org"] = org_id

    labels["app.kubernetes.io/managed-by"] = "reliably"
    labels["app.kubernetes.io/component"] = "experiment"
    labels["app.kubernetes.io/name"] = f"plan-{plan_id}"

    annotations = md.setdefault("annotations", {})
    annotations["reliably.com/plan"] = plan_id
    annotations["reliably.com/org"] = org_id


def create_secret(
    job: Dict[str, Any],
    tk: str,
    plan_id: str,
    name: str,
) -> Dict[str, Any]:
    toml = f"""
[service]
token="{tk}"
    """.strip()

    secret = {
        "apiVersion": "v1",
        "kind": "Secret",
        "type": "Opaque",
        "metadata": {
            "name": name,
        },
        "data": {
            "cfg": base64.b64encode(toml.encode("utf-8")).decode("utf-8"),
        },
    }

    pod_spec = get_pod_template(job)["spec"]
    ct = pod_spec["containers"][0]

    mounts = ct.setdefault("volumeMounts", [])
    mounts.append(
        {
            "name": "reliably-env",
            "mountPath": "/home/svc/.config/reliably/config.toml",
            "subPath": "cfg",
            "readOnly": True,
        }
    )

    volumes = pod_spec.setdefault("volumes", [])
    volumes.append({"name": "reliably-env", "secret": {"secretName": name}})

    return secret


def get_service_account_volume() -> dict[str, Any]:
    return {
        "name": "service-account-token",
        "projected": {
            "sources": [
                {
                    "serviceAccountToken": {
                        "expirationSeconds": 7200,
                        "path": "token",
                    }
                },
                {
                    "downwardAPI": {
                        "items": [
                            {
                                "path": "namespace",
                                "fieldRef": {
                                    "apiVersion": "v1",
                                    "fieldPath": "metadata.namespace",
                                },
                            }
                        ]
                    }
                },
                {
                    "configMap": {
                        "name": "kube-root-ca.crt",
                        "items": [{"key": "ca.crt", "path": "ca.crt"}],
                    }
                },
            ]
        },
    }


def get_pod_template(job: Dict[str, Any]) -> Dict[str, Any]:
    if job["kind"] == "CronJob":
        return cast(
            dict[str, Any], job["spec"]["jobTemplate"]["spec"]["template"]
        )

    return cast(dict[str, Any], job["spec"]["template"])


def get_endpoint_info(domain: str) -> Tuple[str, str]:
    p = urlparse(domain)
    return (p.scheme, p.netloc)


def add_environment_vars(
    pod: Dict[str, Any],
    plan_id: str,
    user_id: str,
    org_id: str,
    tk: str,
) -> None:
    settings = get_settings()

    scheme, domain = get_endpoint_info(settings.RELIABLY_DOMAIN)
    host = domain
    service_host = f"{scheme}://{domain}"

    if settings.CLI_RELIABLY_SERVICE_HOST:
        service_host = settings.CLI_RELIABLY_SERVICE_HOST

    if settings.CLI_RELIABLY_HOST:
        host = settings.CLI_RELIABLY_HOST

    use_http = "false" if service_host.startswith("https://") else "true"
    verify_tls = "false" if use_http else "true"

    if settings.CLI_RELIABLY_VERIFY_TLS is not None:
        verify_tls = "true" if settings.CLI_RELIABLY_VERIFY_TLS else "false"

    variables: Dict[str, str] = {
        "RELIABLY_SERVICE_HOST": service_host,
        "RELIABLY_HOST": host,
        "RELIABLY_ORGANIZATION_ID": org_id,
        "RELIABLY_VERIFY_TLS": verify_tls,
        "RELIABLY_USE_HTTP": use_http,
        "RELIABLY_USER_ID": user_id,
        "RELIABLY_PLAN_ID": plan_id,
        "RELIABLY_CLI_CONFIG": "/home/svc/.config/reliably/config.toml",
    }

    if settings.DEPLOYMENT_STRATEGY != "k8s":
        variables["RELIABLY_SERVICE_TOKEN"] = tk

    envvars = pod["containers"][0].setdefault("env", [])
    for k, v in variables.items():
        envvars.append({"name": k, "value": v})


def create_oneshot_job(
    plan_id: str,
    dep: deployment.schemas.DeploymentKubernetesJobDefinition,
    name: str,
) -> Dict[str, Any]:
    p: Dict[str, Any] | None
    if dep.use_default_manifest:
        p = get_default_pod_spec(dep.image)  # type: ignore
    else:
        logger.debug("Using Kubernetes pod manifest as provided by user")
        p = dep.parsed_manifest

    if not p:
        raise PlanFailedError(plan_id, "deployment is missing a Pod manifest")

    spec = p["spec"]

    spec["containers"][0]["args"] = [
        "service",
        "plan",
        "execute",
        "--set-status",
        "--log-stdout",
        "--load-environment",
        plan_id,
    ]

    job = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": name,
            "labels": p["metadata"].get("labels", {}),
            "annotations": p["metadata"].get("annotations", {}),
        },
        "spec": {"template": {"spec": spec}},
    }

    return job


def get_job_name(plan: schemas.Plan, is_cron: bool = False) -> str:
    if not is_cron:
        return f"reliably-plan-{str(plan.id)}-{secrets.token_hex(4)}"

    return f"reliably-plan-{str(plan.id)}"


def create_cron_job(
    plan_id: str,
    dep: deployment.schemas.DeploymentKubernetesJobDefinition,
    name: str,
    pattern: str,
    timezone: str | None,
) -> Dict[str, Any]:
    p: Dict[str, Any] | None
    if dep.use_default_manifest:
        p = get_default_pod_spec(dep.image)  # type: ignore
    else:
        logger.debug("Using Kubernetes pod manifest as provided by user")
        p = dep.parsed_manifest

    if not p:
        raise PlanFailedError(plan_id, "deployment is missing a Pod manifest")

    spec = p["spec"]

    spec["containers"][0]["args"] = [
        "service",
        "plan",
        "execute",
        "--set-status",
        "--log-stdout",
        "--load-environment",
        plan_id,
    ]

    job = {
        "apiVersion": "batch/v1",
        "kind": "CronJob",
        "metadata": {
            "name": name,
            "labels": p["metadata"].get("labels", {}),
            "annotations": p["metadata"].get("annotations", {}),
        },
        "spec": {
            "schedule": pattern,
            "startingDeadlineSeconds": 10,
            "concurrencyPolicy": "Forbid",
            "jobTemplate": {"spec": {"template": {"spec": spec}}},
        },
    }

    if timezone:
        job["spec"]["timeZone"] = timezone  # type: ignore

    if dep.use_default_manifest and dep.use_in_cluster_credentials:
        job["spec"]["volumes"] = [get_service_account_volume()]  # type: ignore
        vm = spec["containers"][0].setdefault("volumeMounts", [])
        vm.append(
            {
                "name": "service-account-token",
                "mountPath": "/home/svc/.config/rebound/sa",
                "readOnly": True,
            }
        )

    return job


def get_default_pod_spec(image: str) -> Dict[str, Any]:
    pod = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "annotations": {
                "reliably.com/default-template": "true",
            },
        },
        "spec": {
            "restartPolicy": "Never",
            "serviceAccountName": "reliably-job",
            "securityContext": {
                "runAsUser": 1001,
                "runAsGroup": 1001,
            },
            "containers": [
                {
                    "name": "job",
                    "image": image,
                    "imagePullPolicy": "Always",
                    "resources": {
                        "limits": {"cpu": "200m", "memory": "256Mi"},
                        "requests": {"cpu": "200m", "memory": "256Mi"},
                    },
                    "securityContext": {
                        "allowPrivilegeEscalation": False,
                    },
                }
            ],
        },
    }

    return pod


def get_k8s_job(
    k8s_client: client.ApiClient,
    name: str,
    namespace: str,
    is_cron: bool,
) -> Union[client.V1CronJob, client.V1Job] | None:
    v1 = client.BatchV1Api(api_client=k8s_client)

    try:
        if is_cron:
            return v1.read_namespaced_cron_job(
                name=name,
                namespace=namespace,
            )
        else:
            return v1.read_namespaced_job(
                name=name,
                namespace=namespace,
            )
    except client.rest.ApiException as e:
        logger.debug(f"Failed to get Kubernetes Job: {str(e)}", exc_info=True)

    return None


def get_last_job_event(
    k8s_client: client.ApiClient, plan_id: str, namespace: str
) -> dict[str, None]:
    v1 = client.CoreV1Api(api_client=k8s_client)
    r = v1.list_namespaced_event(
        namespace=namespace,
        field_selector=f"involvedObject.name=reliably-plan-{plan_id}",
        limit=1,
        _preload_content=False,
    )

    return msgspec.json.decode(r.data)  # type: ignore


async def supervise_job(
    event: asyncio.Event,
    dep: deployment.schemas.DeploymentKubernetesJobDefinition,
    plan_id: str,
    job_name: str,
    namespace: str,
    is_cron: bool,
) -> None:
    name = job_name
    logger.debug(f"Started supervision of Kubernetes job for plan {plan_id}")

    cfg = load_kubernetes_config(dep)
    k8s_client = client.ApiClient(configuration=cfg)

    wait_for = 3
    while not event.is_set():
        await asyncio.sleep(wait_for)
        wait_for += 3

        async with SessionLocal() as db:
            pl = await crud.get_plan(db, plan_id)

        if not pl:
            return None

        p = schemas.Plan.model_validate(pl, from_attributes=True)
        if p.status in (
            schemas.PlanStatus.creation_error,
            schemas.PlanStatus.running,
            schemas.PlanStatus.completed,
            schemas.PlanStatus.running_error,
        ):
            # we properly started the container, even if the plan fails
            # the correct status will be recorded for the plan
            logger.debug(
                f"Plan {plan_id} started normally, stopping supervision "
                f"of Kubernetes job {name}"
            )
            return None

        logger.debug(f"Checking on Kubernetes job {name} for plan {plan_id}")
        job = await asyncio.to_thread(
            get_k8s_job,
            k8s_client=k8s_client,
            name=name,
            namespace=namespace,
            is_cron=is_cron,
        )

        if pl and not job:
            logger.debug(
                f"Kubernetes Job {name} is gone but plan {plan_id} still exists"
            )
            return None

        if not job:
            return None

        job_event = await asyncio.to_thread(
            get_last_job_event,
            k8s_client=k8s_client,
            namespace=namespace,
            plan_id=plan_id,
        )

        if len(job_event["items"]) > 0:  # type: ignore
            item = job_event["items"][0]  # type: ignore
            if item["reason"] == "FailedCreate":
                logger.debug(f"Kubernetes Job {name} failed to create: {item}")

                async with SessionLocal() as db:
                    await crud.set_status(
                        db,
                        plan_id,
                        schemas.PlanStatus.creation_error,
                        error=(
                            f"Kubernetes Job '{name}' failed to create: "
                            f"{item['message']}"
                        ),
                    )
                return None

        if isinstance(job, client.V1CronJob):
            if not job.status.active:
                continue

            j = job.status.active[0]
            job = get_k8s_job(k8s_client, j.name, j.namespace, False)
            status = job.status  # type: ignore
        else:
            status = job.status

        if p and status.failed and status.failed > 1:
            if p.status in (
                schemas.PlanStatus.creating,
                schemas.PlanStatus.created,
            ):
                logger.warning(
                    f"Kubernetes Job {name} is failing to start {status}"
                )
                async with SessionLocal() as db:
                    await crud.set_status(
                        db,
                        plan_id,
                        schemas.PlanStatus.created,
                        error=(
                            f"Kubernetes Job '{name}' seems to have trouble "
                            "to start have two attempts"
                        ),
                    )
                return None


def switch_suspend_flag(
    suspend: bool, plan: schemas.Plan, dep: deployment.schemas.Deployment
) -> None:
    d = cast(
        deployment.schemas.DeploymentKubernetesJobDefinition, dep.definition
    )
    namespace = d.namespace
    job_name = get_job_name(plan, True)

    name = job_name

    cfg = load_kubernetes_config(d)
    k8s_client = client.ApiClient(configuration=cfg)

    job = get_k8s_job(
        k8s_client=k8s_client,
        name=name,
        namespace=namespace,
        is_cron=True,
    )

    if not job:
        logger.warning(
            f"Cannot change Kubernetes job {name} state. Job is missing."
        )
        return None

    batchv1 = client.BatchV1Api(api_client=k8s_client)
    batchv1.patch_namespaced_cron_job(
        name=name, namespace=namespace, body={"spec": {"suspend": suspend}}
    )

    return None
