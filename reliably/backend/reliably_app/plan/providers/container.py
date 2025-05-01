import asyncio
import logging
import secrets
from typing import Dict, List, Tuple, cast
from urllib.parse import urlparse

import docker
from docker.errors import NotFound
from docker.models.containers import Container

from reliably_app import (
    agent,
    deployment,
    environment,
    experiment,
    integration,
    job,
    notification,
    token,
)
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

    logger.info(f"Executing plan {str(plan.id)} locally from a container")

    if plan.definition.schedule.type == "cron":
        async with SessionLocal() as db:
            j = await job.crud.get_job_by_type(
                db, org_id, "plan", "plan_id", str(plan.id)
            )
            if not j:
                await job.crud.enqueue_job(
                    org_id,
                    job.schemas.JobCreate(
                        user_id=user_id,
                        pattern=plan.definition.schedule.pattern,
                        timezone=plan.definition.schedule.timezone,
                        definition=job.schemas.JobPlan(
                            type="plan",
                            plan_id=plan.id,
                        ),
                    ),
                )
                return None
            else:
                await asyncio.to_thread(
                    stop_and_remove_container,
                    plan,
                    cast(
                        deployment.schemas.DeploymentContainerDefinition,
                        dep.definition,
                    ),
                    env,
                )

    token = await create_agent_token(str(plan.id), org_id, user_id)

    async with SessionLocal() as db:
        experiment_summary = await experiment.crud.get_experiment_summary(
            db,
            org_id,  # type: ignore
            plan.definition.experiments[0],
        )
        await notification.tasks.notify_event(
            notification.schemas.PlanEvent(
                org_id=org_id,
                kind="plan-phases",
                plan=plan,
                deployment=dep,
                experiment=experiment_summary,
            )
        )

    container_id = await asyncio.to_thread(
        run_container,
        plan,
        cast(
            deployment.schemas.DeploymentContainerDefinition,
            dep.definition,
        ),
        env,
        integrations,
        org_id,
        user_id,
        token,
    )

    plan_id = str(plan.id)
    add_background_async_task(
        supervise_container(event, container_id, plan_id),
        name=f"Supervisor-{plan_id}",
    )


async def delete_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
    env: environment.schemas.Environment | None,
) -> None:
    logger.info(f"Deleting plan {str(plan.id)} from local system")

    if plan.definition.schedule.type == "cron":
        async with SessionLocal() as db:
            j = await job.crud.get_job_by_type(
                db, plan.org_id, "plan", "plan_id", str(plan.id)
            )
            if j:
                await job.crud.remove_job(db, plan.org_id, str(j.id))

    await asyncio.to_thread(
        stop_and_remove_container,
        plan,
        cast(
            deployment.schemas.DeploymentContainerDefinition,
            dep.definition,
        ),
        env,
    )


async def suspend_plan(
    plan: schemas.Plan, dep: deployment.schemas.Deployment
) -> None:
    async with SessionLocal() as db:
        j = await job.crud.get_job_by_type(
            db, plan.org_id, "plan", "plan_id", str(plan.id)
        )
        if j:
            await job.crud.suspend_job(db, str(plan.org_id), str(j.id))


async def resume_plan(
    plan: schemas.Plan, dep: deployment.schemas.Deployment
) -> None:
    async with SessionLocal() as db:
        j = await job.crud.get_job_by_type(
            db, plan.org_id, "plan", "plan_id", str(plan.id)
        )
        if j:
            # we must update the date of the next run as otherwise it's in the
            # past meaning the job would never get rescheduled
            await job.crud.schedule_next(
                str(j.id), str(j.pattern), str(j.timezone)
            )
            await job.crud.resume_job(db, str(plan.org_id), str(j.id))


###############################################################################
# Private functions
###############################################################################
def get_endpoint_info(domain: str) -> Tuple[str, str]:
    p = urlparse(domain)
    return (p.scheme, p.netloc)


def get_job_name(plan: schemas.Plan, is_cron: bool = False) -> str:
    return f"reliably-plan-{str(plan.id)}-{secrets.token_hex(4)}"


def run_container(
    plan: schemas.Plan,
    dep: deployment.schemas.DeploymentContainerDefinition,
    env: environment.schemas.Environment | None,
    integrations: List[integration.schemas.IntegrationFull],
    org_id: str,
    user_id: str,
    token: str,
) -> str:
    settings = get_settings()

    is_cron = plan.definition.schedule.type == "cron"
    name = get_job_name(plan, is_cron)
    logger.info(f"Trying to create Docker container with name '{name}'")

    v = {}
    if dep.volumes:
        v = {k: v.model_dump() for k, v in dep.volumes.items()}

    command = [
        "service",
        "plan",
        "execute",
        "--set-status",
        "--log-stdout",
        "--load-environment",
        str(plan.id),
    ]

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
        "RELIABLY_SERVICE_TOKEN": token,
        "RELIABLY_SERVICE_HOST": service_host,
        "RELIABLY_DOMAIN": settings.RELIABLY_DOMAIN,
        "RELIABLY_HOST": host,
        "RELIABLY_VERIFY_TLS": verify_tls,
        "RELIABLY_USE_HTTP": use_http,
        "RELIABLY_ORGANIZATION_ID": org_id,
        "RELIABLY_USER_ID": user_id,
        "RELIABLY_PLAN_ID": str(plan.id),
    }

    client = docker.from_env()
    try:
        c = client.containers.run(
            dep.image,
            name=name,
            command=command,
            detach=True,
            volumes=v,
            environment=variables,
            working_dir=dep.working_dir,
            labels={
                "plan_id": str(plan.id),
                "org_id": str(org_id),
                "user_id": str(user_id),
            },
        )
    except Exception:
        logger.error("Failed to launch Docker container", exc_info=True)
        raise PlanFailedError(str(plan.id), "Internal Plan Error")

    logger.info(f"Created Docker container [ID: {c.id}]")

    return cast(str, c.id)


def stop_and_remove_container(
    plan: schemas.Plan,
    dep: deployment.schemas.DeploymentContainerDefinition,
    env: environment.schemas.Environment | None,
) -> None:
    plan_id = str(plan.id)
    logger.info(f"Trying to remove Docker container for plan '{plan_id}'")

    client = docker.from_env()
    try:
        ctns = client.containers.list(filters={"label": f"plan_id={plan_id}"})
    except NotFound:
        return None

    # logs = c.logs()
    # logger.info(f"Container [ID: {c.id}] logs: {logs}")

    for c in ctns:
        c.remove(force=True)
        logger.info(f"Removed Docker container [ID: {c.id}]")


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


def get_container(container_id: str) -> Container | None:
    client = docker.from_env()
    try:
        return client.containers.get(container_id)
    except NotFound:
        return None


async def supervise_container(
    event: asyncio.Event, container_id: str, plan_id: str
) -> None:
    short_ct_id = container_id[:12]

    logger.debug(
        f"Started supervision of container {short_ct_id} for plan {plan_id}"
    )

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
                f"of container {short_ct_id}"
            )
            return None

        logger.debug(f"Checking on container {short_ct_id} for plan {plan_id}")
        ct = await asyncio.to_thread(get_container, container_id=container_id)

        if pl and not ct:
            logger.debug(
                f"Container {short_ct_id} is gone but plan "
                f"{plan_id} still exists"
            )
            return None

        if not ct:
            return None

        if p and ct.status == "exited":
            if p.status in (
                schemas.PlanStatus.creating,
                schemas.PlanStatus.created,
            ):
                logger.warning(
                    f"Container {short_ct_id} exited before "
                    f"plan {plan_id} started"
                )
                async with SessionLocal() as db:
                    await crud.set_status(
                        db,
                        plan_id,
                        schemas.PlanStatus.creation_error,
                        error=f"Container '{short_ct_id}' exited abnormally",
                    )
                return None
