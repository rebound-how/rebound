import asyncio
import logging
import secrets
from typing import Any, Dict, List, Tuple, cast

import httpx
from starlette.requests import Request

from reliably_app import agent, deployment, environment, integration, token
from reliably_app.config import get_settings
from reliably_app.database import SessionLocal
from reliably_app.observability import span
from reliably_app.plan import schemas
from reliably_app.plan.errors import PlanFailedError
from reliably_app.plan.providers.utils import get_plan_max_duration

__all__ = ["delete_plan", "execute_plan"]

logger = logging.getLogger("reliably_app")
METADATA_BASE = "http://metadata.google.internal/computeMetadata/v1"
METADATA_TOKEN_URL = f"{METADATA_BASE}/instance/service-accounts/default/token"
METADATA_PROJECT_ID_URL = f"{METADATA_BASE}/project/project-id"
METADATA_SA_EMAIL_URL = (
    f"{METADATA_BASE}/instance/service-accounts/default/email"
)


async def execute_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
    env: environment.schemas.Environment | None,
    integrations: List[integration.schemas.IntegrationFull],
    org_id: str,
    user_id: str,
    request: Request | None,
) -> None:
    logger.info(f"Executing plan {str(plan.id)} with Reliably")

    await create_cloud_run_job(
        plan,
        cast(
            deployment.schemas.DeploymentReliablyCloudDefinition,
            dep.definition,
        ),
        env,
        integrations,
        org_id,
        user_id,
        request,
    )


async def delete_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
    env: environment.schemas.Environment | None,
) -> None:
    logger.info(f"Deleting plan {str(plan.id)} from Reliably")

    await delete_cloud_resources(
        plan,
        cast(
            deployment.schemas.DeploymentReliablyCloudDefinition,
            dep.definition,
        ),
    )


async def suspend_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
) -> None:
    plan_id = str(plan.id)

    job_name = f"plan-{plan_id}"

    tk, project_id = await get_gcp_token(audience="")
    if not tk or not project_id:
        logger.error("failed to lookup credentials or project_id")
        raise PlanFailedError(plan_id, "Internal Plan Error")

    logger.debug(f"Suspending plan {plan_id}")

    await pause_job(
        project_id,
        tk,
        job_name,
        cast(
            deployment.schemas.DeploymentReliablyCloudDefinition,
            dep.definition,
        ),
    )


async def resume_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
) -> None:
    plan_id = str(plan.id)

    job_name = f"plan-{plan_id}"

    tk, project_id = await get_gcp_token(audience="")
    if not tk or not project_id:
        logger.error("failed to lookup credentials or project_id")
        raise PlanFailedError(plan_id, "Internal Plan Error")

    logger.debug(f"Suspending plan {plan_id}")

    await resume_job(
        project_id,
        tk,
        job_name,
        cast(
            deployment.schemas.DeploymentReliablyCloudDefinition,
            dep.definition,
        ),
    )


###############################################################################
# Private functions
###############################################################################
async def get_gcp_token(audience: str) -> Tuple[str, str]:
    token = project_id = None

    with span("plan-schedule-get-gcp-info"):
        async with httpx.AsyncClient(http2=True) as client:
            r = await client.get(
                METADATA_TOKEN_URL,
                headers={
                    "Metadata-Flavor": "Google",
                },
            )
            if r.status_code > 399:
                return ("", "")

            token = r.json()["access_token"]

            r = await client.get(
                METADATA_PROJECT_ID_URL,
                headers={
                    "Metadata-Flavor": "Google",
                },
            )
            if r.status_code > 399:
                return (token, "")

            project_id = r.text

        return (token, project_id)


async def create_cloud_run_job(
    plan: schemas.Plan,
    dep: deployment.schemas.DeploymentReliablyCloudDefinition,
    env: environment.schemas.Environment | None,
    integrations: List[integration.schemas.IntegrationFull],
    org_id: str,
    user_id: str,
    request: Request | None,
) -> None:
    settings = get_settings()

    host = settings.RELIABLY_DOMAIN
    if not host.startswith("https://"):
        host = f"https://{host}"

    plan_id = str(plan.id)
    labels = {"cloud.googleapis.com/location": dep.location}

    base_url = (
        f"https://{dep.location}-run.googleapis.com/apis/run.googleapis.com"
    )

    tk, project_id = await get_gcp_token(audience=base_url)
    if not tk or not project_id:
        logger.error("failed to lookup credentials or project_id")
        raise PlanFailedError(plan_id, "Internal Plan Error")

    agent_token = await create_agent_token(plan_id, org_id, user_id)

    sa_email = settings.CLOUDRUN_JOB_SA

    logger.debug(
        f"Scheduling Reliably job in project '{project_id}' with '{sa_email}'"
    )

    envs = build_env(org_id, host, agent_token)

    job_name = f"plan-{plan_id}"

    annotations = get_annotations(dep, org_id, plan_id)
    args = get_args(plan_id)
    nonce = secrets.token_hex(8)
    attributes = get_attributes(org_id, plan_id, job_name, nonce)

    if plan.definition.schedule.type != "cron":
        current_job = await get_job(base_url, project_id, tk, job_name)
        if current_job:
            await replace_job(
                current_job,
                base_url,
                project_id,
                tk,
                job_name,
                labels,
                envs,
                sa_email,
                plan,
                dep,
                args,
                annotations,
                attributes,
            )
        else:
            await create_job(
                base_url,
                project_id,
                tk,
                job_name,
                labels,
                envs,
                sa_email,
                plan,
                dep,
                args,
                annotations,
                attributes,
                nonce,
            )

        await wait_for_job_readyness(
            base_url, project_id, tk, job_name, plan_id, attributes
        )

        await run_plan(base_url, project_id, tk, job_name, plan_id, attributes)
    else:
        await create_job(
            base_url,
            project_id,
            tk,
            job_name,
            labels,
            envs,
            sa_email,
            plan,
            dep,
            args,
            annotations,
            attributes,
            nonce,
        )

        await wait_for_job_readyness(
            base_url, project_id, tk, job_name, plan_id, attributes
        )

        await schedule_cron_job(
            base_url, project_id, tk, job_name, plan, dep, attributes
        )


def get_annotations(
    dep: deployment.schemas.DeploymentReliablyCloudDefinition,
    org_id: str,
    plan_id: str,
) -> Dict[str, str]:
    return {
        "client.knative.dev/user-image": dep.image,
        "run.googleapis.com/client-name": "reliably",
        "run.googleapis.com/launch-stage": "BETA",
        "reliably.com/org": str(org_id),
        "reliably.com/plan": plan_id,
    }


def get_args(plan_id: str) -> List[str]:
    return [
        "service",
        "plan",
        "execute",
        "--set-status",
        "--log-stdout",
        "--load-environment",
        plan_id,
    ]


def get_attributes(
    org_id: str, plan_id: str, job_name: str, nonce: str
) -> Dict[str, str]:
    return {
        "plan_id": plan_id,
        "org_id": str(org_id),
        "job": job_name,
        "nonce": nonce,
    }


async def create_job(
    base_url: str,
    project_id: str,
    gcp_token: str,
    job_name: str,
    labels: Dict[str, str],
    envs: List,
    sa_email: str | None,
    plan: schemas.Plan,
    dep: deployment.schemas.DeploymentReliablyCloudDefinition,
    args: List[str],
    annotations: Dict[str, str],
    attributes: Dict[str, str],
    nonce: str,
) -> None:
    plan_id = str(plan.id)

    howlong = await get_plan_max_duration(str(plan.org_id))

    async with httpx.AsyncClient(http2=True, timeout=60.0) as client:
        client.base_url = httpx.URL(base_url)
        client.headers = httpx.Headers(
            {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {gcp_token}",
            }
        )

        with span("plan-create-job", attributes=attributes):
            r = await client.post(
                f"/v1/namespaces/{project_id}/jobs",
                params={"alt": "json"},
                json={
                    "apiVersion": "run.googleapis.com/v1",
                    "kind": "Job",
                    "metadata": {
                        "annotations": annotations,
                        "labels": labels,
                        "name": job_name,
                        "namespace": project_id,
                        "resourceVersion": secrets.token_hex(12),
                    },
                    "spec": {
                        "template": {
                            "metadata": {
                                "annotations": annotations,
                                "labels": {
                                    "client.knative.dev/nonce": nonce,
                                },
                            },
                            "spec": {
                                "template": {
                                    "spec": {
                                        "serviceAccountName": sa_email,
                                        "maxRetries": 0,
                                        "timeoutSeconds": howlong,
                                        "containers": [
                                            {
                                                "image": dep.image,
                                                "args": args,
                                                "resources": {
                                                    "limits": {
                                                        "memory": "512Mi",
                                                        "cpu": "1.0",
                                                    }
                                                },
                                                "env": envs,
                                            }
                                        ],
                                    }
                                }
                            },
                        }
                    },
                },
            )

            if r.status_code > 399:
                logger.error(
                    "Failed to create Reliably cloud job"
                    f"{r.status_code} => {r.json()} [PLAN: {str(plan.id)}]",
                )
                raise PlanFailedError(plan_id, "Internal Plan Error")

            logger.info(
                f"Plan {plan_id} created [{plan.definition.schedule.type}]: "
                f"{r.status_code}: {r.json()}"
            )


async def replace_job(
    current_job: Dict[str, Any],
    base_url: str,
    project_id: str,
    gcp_token: str,
    job_name: str,
    labels: Dict[str, str],
    envs: List,
    sa_email: str | None,
    plan: schemas.Plan,
    dep: deployment.schemas.DeploymentReliablyCloudDefinition,
    args: List[str],
    annotations: Dict[str, str],
    attributes: Dict[str, str],
) -> None:
    plan_id = str(plan.id)

    md = current_job["metadata"]
    md["annotations"] = annotations
    md["labels"] = labels

    tpl = current_job["spec"]["template"]
    md = tpl["metadata"]
    md["annotations"] = annotations

    sp = tpl["spec"]["template"]["spec"]
    sp["serviceAccountName"] = sa_email

    ct = tpl["spec"]["template"]["spec"]["containers"][0]
    ct["image"] = dep.image
    ct["args"] = args
    ct["env"] = envs

    async with httpx.AsyncClient(http2=True, timeout=60.0) as client:
        client.base_url = httpx.URL(base_url)
        client.headers = httpx.Headers(
            {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {gcp_token}",
            }
        )

        with span("plan-replace-job", attributes=attributes):
            r = await client.put(
                f"/v1/namespaces/{project_id}/jobs/{job_name}",
                params={"alt": "json"},
                json=current_job,
            )

            if r.status_code > 399:
                logger.error(
                    "Failed to replace Reliably cloud job"
                    f"{r.status_code} => {r.json()} [PLAN: {str(plan.id)}]",
                )
                raise PlanFailedError(plan_id, "Internal Plan Error")

            logger.info(
                f"Plan {plan_id} replaced [{plan.definition.schedule.type}]: "
                f"{r.status_code}: {r.json()}"
            )


async def wait_for_job_readyness(
    base_url: str,
    project_id: str,
    gcp_token: str,
    job_name: str,
    plan_id: str,
    attributes: Dict[str, str],
) -> None:
    async with httpx.AsyncClient(http2=True, timeout=60.0) as client:
        client.base_url = httpx.URL(base_url)
        client.headers = httpx.Headers(
            {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {gcp_token}",
            }
        )

        with span("plan-wait-to-be-ready", attributes=attributes):
            for i in range(10):
                r = await client.get(
                    f"/v1/namespaces/{project_id}/jobs/{job_name}?alt=json"
                )

                if r.status_code > 399:
                    logger.error(
                        "Failed to retrieve Reliably cloud job status: "
                        f"{r.status_code} => {r.json()} "
                        f"[PLAN: {plan_id}]",
                    )
                    raise PlanFailedError(plan_id, "Internal Plan Error")

                j = r.json()
                logger.info(f"[Iteration {i}] Status of plan {plan_id}: {j}")
                if "conditions" in j["status"]:
                    condition = j["status"]["conditions"][-1]

                    if (
                        condition["type"] == "Ready"
                        and condition["status"] == "True"
                    ):
                        break
                await asyncio.sleep(0.5)
            else:
                logger.error(
                    f"Job for plan {plan_id} failed to get ready "
                    f"[PLAN: {plan_id}]",
                )
                raise PlanFailedError(plan_id, "Internal Plan Error")


async def run_plan(
    base_url: str,
    project_id: str,
    gcp_token: str,
    job_name: str,
    plan_id: str,
    attributes: Dict[str, str],
) -> None:
    async with httpx.AsyncClient(http2=True, timeout=60.0) as client:
        client.base_url = httpx.URL(base_url)
        client.headers = httpx.Headers(
            {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {gcp_token}",
            }
        )

        with span("plan-running-job", attributes=attributes):
            logger.info(f"Job created for plan {plan_id}. Running it now")

            r = await client.post(
                f"/v1/namespaces/{project_id}/jobs/{job_name}:run"
            )

            if r.status_code > 399:
                logger.error(
                    "Failed to execute Reliably cloud job: "
                    f"{r.status_code} => {r.json()} "
                    f"[PLAN: {plan_id}]",
                )
                raise PlanFailedError(plan_id, "Internal Plan Error")


async def schedule_cron_job(
    base_url: str,
    project_id: str,
    gcp_token: str,
    job_name: str,
    plan: schemas.Plan,
    dep: deployment.schemas.DeploymentReliablyCloudDefinition,
    attributes: Dict[str, str],
) -> None:
    settings = get_settings()
    plan_id = str(plan.id)
    job_id = f"projects/{project_id}/locations/{dep.location}/jobs/{job_name}"  # noqa
    target_url = f"{base_url}/v1/namespaces/{project_id}/jobs/{job_name}:run"  # noqa
    sched_url = f"https://cloudscheduler.googleapis.com/v1/projects/{project_id}/locations/{dep.location}/jobs"  # noqa

    plan_sched = settings.PLAN_SCHEDULER_SA
    pattern = plan.definition.schedule.pattern  # type: ignore
    timezone = plan.definition.schedule.timezone or "Etc/UTC"  # type: ignore
    logger.info(
        f"Scheduling plan {plan_id} with pattern: {pattern} in "
        f"timezone {timezone}"
    )

    attributes["pattern"] = pattern
    attributes["timezone"] = timezone

    async with httpx.AsyncClient(http2=True, timeout=60.0) as client:
        client.base_url = httpx.URL(base_url)
        client.headers = httpx.Headers(
            {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {gcp_token}",
            }
        )

        with span("plan-scheduling-now", attributes=attributes):
            r = await client.post(
                sched_url,
                json={
                    "name": job_id,
                    "description": f"Schedule for plan {plan_id}",
                    "schedule": pattern,
                    "timeZone": timezone,
                    "httpTarget": {
                        "uri": target_url,
                        "httpMethod": "POST",
                        "oauthToken": {"serviceAccountEmail": plan_sched},
                    },
                },
            )

            if r.status_code > 399:
                logger.error(
                    "Failed to schedule Reliably job to run periodically: "
                    f"{r.status_code} => {r.text}"
                    f"[PLAN: {plan_id}]",
                )
                raise PlanFailedError(plan_id, "Internal Plan Error")


async def create_agent_token(plan_id: str, org_id: str, user_id: str) -> str:
    secret_name = f"SECRET_{plan_id}"

    attrs = {
        "plan_id": plan_id,
        "org_id": org_id,
        "user_id": user_id,
    }

    with span("plan-schedule-get-agent-token", attributes=attrs) as s:
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
                with span("plan-schedule-create-agent-token", attributes=attrs):
                    tc = token.schemas.TokenCreate(name=secret_name)
                    agt_token = await token.crud.create_token(
                        db,
                        org_id,  # type: ignore
                        agt.user_id,  # type: ignore
                        tc,
                    )

            s.set_attribute("agent_token_id", str(agt_token.id))

            return cast(str, agt_token.token.decode("utf-8"))


async def delete_cloud_resources(
    plan: schemas.Plan,
    dep: deployment.schemas.DeploymentReliablyCloudDefinition,
) -> None:
    plan_id = str(plan.id)
    job_name = f"plan-{plan_id}"

    secret_name = None
    base_url = (
        f"https://{dep.location}-run.googleapis.com/apis/run.googleapis.com"
    )

    attrs = {
        "plan_id": plan_id,
        "secret_name": secret_name or "",
        "job_name": job_name,
    }

    with span("plan-schedule-get-gcp-info", attributes=attrs):
        tk, project_id = await get_gcp_token(audience=base_url)
        if not tk or not project_id:
            logger.error(
                f"failed to lookup credentials or project_id [PLAN: {plan.id}]"
            )
            raise PlanFailedError(plan_id, "Internal Plan Error")

        async with httpx.AsyncClient(http2=True, timeout=60.0) as client:
            client.base_url = httpx.URL(base_url)
            client.headers = httpx.Headers(
                {
                    "Accept": "application/json; charset=utf-8",
                    "Authorization": f"Bearer {tk}",
                }
            )

            if plan.definition.schedule.type == "cron":
                sched_url = f"https://cloudscheduler.googleapis.com/v1/projects/{project_id}/locations/{dep.location}/jobs/{job_name}"  # noqa
                r = await client.delete(sched_url)
                if r.status_code > 399 and r.status_code != 404:
                    logger.error(
                        "Failed to delete Reliably scheduler job"
                        f"{r.status_code} => {r.text}"
                        f" [PLAN: {plan.id}]"
                    )
                    raise PlanFailedError(plan_id, "Internal Plan Error")

            r = await client.delete(
                f"/v1/namespaces/{project_id}/jobs/{job_name}"
            )
            if r.status_code > 399 and r.status_code != 404:
                logger.error(
                    "Failed to delete Reliably job"
                    f"{r.status_code} => {r.text} "
                    f"[PLAN: {plan.id}]"
                )
                raise PlanFailedError(plan_id, "Internal Plan Error")


def build_env(
    org_id: str,
    host: str,
    agent_token: str,
) -> List:
    envs: List = []

    envs.append({"name": "RELIABLY_SERVICE_HOST", "value": host})
    envs.append({"name": "RELIABLY_ORGANIZATION_ID", "value": org_id})
    envs.append({"name": "RELIABLY_SERVICE_TOKEN", "value": agent_token})
    envs.append(
        {"name": "RELIABLY_CATCH_SIGTERM_BEFORE_CHAOSTOOLKIT", "value": "1"}
    )

    return envs


async def get_job(
    base_url: str, project_id: str, gcp_token: str, job_name: str
) -> Dict[str, Any] | None:
    async with httpx.AsyncClient(http2=True, timeout=60.0) as client:
        client.base_url = httpx.URL(base_url)
        client.headers = httpx.Headers(
            {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {gcp_token}",
            }
        )

        r = await client.get(f"/v1/namespaces/{project_id}/jobs/{job_name}")
        if r.status_code > 399:
            return None

        return cast(dict[str, Any], r.json())


async def pause_job(
    project_id: str,
    gcp_token: str,
    job_name: str,
    dep: deployment.schemas.DeploymentReliablyCloudDefinition,
) -> Dict[str, Any] | None:
    sched_url = f"https://cloudscheduler.googleapis.com/v1/projects/{project_id}/locations/{dep.location}/jobs/{job_name}:pause"  # noqa

    async with httpx.AsyncClient(http2=True, timeout=60.0) as client:
        client.headers = httpx.Headers(
            {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {gcp_token}",
            }
        )

        r = await client.post(sched_url)
        if r.status_code > 399:
            logger.warning(f"Failed to pause scheduled job: {r.text}")

        return None


async def resume_job(
    project_id: str,
    gcp_token: str,
    job_name: str,
    dep: deployment.schemas.DeploymentReliablyCloudDefinition,
) -> Dict[str, Any] | None:
    sched_url = f"https://cloudscheduler.googleapis.com/v1/projects/{project_id}/locations/{dep.location}/jobs/{job_name}:resume"  # noqa

    async with httpx.AsyncClient(http2=True, timeout=60.0) as client:
        client.headers = httpx.Headers(
            {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {gcp_token}",
            }
        )

        r = await client.post(sched_url)
        if r.status_code > 399:
            logger.warning(f"Failed to resume scheduled job: {r.text}")

        return None
