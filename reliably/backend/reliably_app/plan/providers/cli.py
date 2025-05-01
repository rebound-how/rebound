import asyncio
import importlib.resources
import logging
import os
import random
import shutil
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator, Tuple, cast
from urllib.parse import urlparse

from reliably_app import (
    agent,
    deployment,
    environment,
    experiment,
    job,
    notification,
    token,
)
from reliably_app.config import get_settings
from reliably_app.database import SessionLocal
from reliably_app.observability import span
from reliably_app.plan import crud, schemas
from reliably_app.plan.errors import PlanFailedError

__all__ = ["delete_plan", "execute_plan"]
logger = logging.getLogger("reliably_app")

PROCS: dict[str, asyncio.subprocess.Process] = {}
LOCK = asyncio.Lock()


async def execute_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
    env: environment.schemas.Environment,
    org_id: str,
    user_id: str,
) -> None:  # noqa
    cli_def = cast(deployment.schemas.DeploymentCLIDefinition, dep.definition)
    if cli_def.mode == "manual":
        return None

    await create_cli_job(plan, dep, env, org_id, user_id)


async def delete_plan(
    plan: schemas.Plan, dep: deployment.schemas.Deployment
) -> None:
    cli_def = cast(deployment.schemas.DeploymentCLIDefinition, dep.definition)
    if cli_def.mode == "manual":
        return None

    if plan.definition.schedule.type == "cron":
        async with SessionLocal() as db:
            j = await job.crud.get_job_by_type(
                db, plan.org_id, "plan", "plan_id", str(plan.id)
            )
            if j:
                await job.crud.remove_job(db, plan.org_id, str(j.id))

    await terminate_cli(plan, cli_def)


async def suspend_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
) -> None:
    async with SessionLocal() as db:
        j = await job.crud.get_job_by_type(
            db, plan.org_id, "plan", "plan_id", str(plan.id)
        )
        if j:
            await job.crud.suspend_job(db, str(plan.org_id), str(j.id))


async def resume_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
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


async def create_cli_job(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
    env: environment.schemas.Environment,
    org_id: str,
    user_id: str,
) -> None:
    from reliably_app.background import add_background_async_task

    plan_id = str(plan.id)

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

    agent_token = await create_agent_token(plan_id, org_id, user_id)

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

    add_background_async_task(
        run_cli(
            plan,
            dep,
            env,
            org_id,
            user_id,
            agent_token,
        ),
        name=f"Supervisor-CLI-{plan_id}",
    )


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


async def run_cli(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
    env: environment.schemas.Environment,
    org_id: str,
    user_id: str,
    agent_token: str,
) -> None:
    from reliably_app.background import add_background_async_task, event

    cli_def = cast(deployment.schemas.DeploymentCLIDefinition, dep.definition)

    settings = get_settings()

    plan_id = str(plan.id)

    bin = shutil.which("uvx")
    if not bin:
        raise PlanFailedError(
            plan_id,
            "Cannot run plan using the local CLI depoloyment strategy, "
            "missing `uvx` in PATH",
        )

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

    variables: dict[str, str] = {
        "RELIABLY_SERVICE_TOKEN": agent_token,
        "RELIABLY_SERVICE_HOST": service_host,
        "RELIABLY_DOMAIN": settings.RELIABLY_DOMAIN,
        "RELIABLY_HOST": host,
        "RELIABLY_VERIFY_TLS": verify_tls,
        "RELIABLY_USE_HTTP": use_http,
        "RELIABLY_ORGANIZATION_ID": org_id,
        "RELIABLY_USER_ID": user_id,
        "RELIABLY_PLAN_ID": plan_id,
        "PATH": os.getenv("PATH"),  # type: ignore
        "USER": os.getenv("USER"),  # type: ignore
    }

    # only retain the LANG/LC_* variables as they might be relevant to the run
    e = os.environ
    variables.update(
        {v: e[v] for v in e if v.startswith("LC_") or v.startswith("LANG")}
    )

    with execution_directory(cli_def.base_dir) as d:
        args = ["--isolated", "--compile-bytecode", "--directory", str(d)]

        if cli_def.py_version:
            args.extend(
                [
                    "--python",
                    cli_def.py_version,
                    "--python-preference",
                    "only-managed",
                ]
            )

        baseline_reqs = get_baseline_requirements()

        if cli_def.py_dependencies:
            baseline_reqs = f"{baseline_reqs}\n{cli_def.py_dependencies}"

        requirements = d / Path("requirements.txt")
        requirements.write_text(baseline_reqs)
        args.extend(["--with-requirements", str(requirements.absolute())])

        args.extend(
            [
                "--from",
                "reliably-cli",
                "reliably",
                "service",
                "plan",
                "execute",
                "--set-status",
                "--log-stdout",
                "--load-environment",
                plan_id,
            ]
        )

        proc = await asyncio.create_subprocess_exec(
            bin,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=variables,
            cwd=str(d),
        )

        async with LOCK:
            PROCS[plan_id] = proc

        add_background_async_task(
            supervise_cli(event, plan_id),
            name=f"Supervisor-CLI-{plan_id}",
        )

        try:
            pid = proc.pid
            logger.info(f"Started plan {plan_id} process [PID {pid}]")
            await asyncio.gather(
                consume_process_stream(proc.stdout),
                consume_process_stream(proc.stderr),
            )

            await proc.wait()

            logger.info(f"Plan {plan_id} process exited [PID {pid}]")
        finally:
            async with LOCK:
                PROCS.pop(plan_id, None)


async def consume_process_stream(stream: asyncio.StreamReader | None) -> None:
    if stream is None:
        return None

    while True:
        if stream.at_eof():
            break

        line = await stream.readline()
        if line:
            logger.debug(line.decode("utf-8"))
        else:
            break


async def terminate_cli(
    plan: schemas.Plan, dep: deployment.schemas.DeploymentCLIDefinition
) -> None:
    plan_id = str(plan.id)
    proc = cast(asyncio.subprocess.Process, PROCS.pop(plan_id, None))

    if proc is not None:
        try:
            logger.debug(f"Terminating plan {plan_id} process [PID {proc.pid}]")
            await proc.terminate()  # type: ignore
        finally:
            pass


async def supervise_cli(event: asyncio.Event, plan_id: str) -> None:
    async with LOCK:
        proc = cast(asyncio.subprocess.Process, PROCS.get(plan_id, None))
        if not proc:
            return None

    pid = proc.pid

    logger.info(
        f"Started supervision of CLI process [PID {pid}] for plan {plan_id}"
    )

    wait_for = 3
    while not event.is_set():
        async with LOCK:
            if plan_id not in PROCS:
                return None

        # add a bit of jitter
        await asyncio.sleep(wait_for + random.random())

        async with SessionLocal() as db:
            pl = await crud.get_plan(db, plan_id)

        if not pl:
            return None

        p = schemas.Plan.model_validate(pl, from_attributes=True)
        if p.status in (
            schemas.PlanStatus.creation_error,
            schemas.PlanStatus.running_error,
        ):
            # we properly started the container, even if the plan fails
            # the correct status will be recorded for the plan
            logger.info(
                f"Plan {plan_id} failed to run, stopping supervision "
                f"of process {pid}"
            )
            return None

        logger.debug(f"Checking on process {pid} for plan {plan_id}")

        if p.status == schemas.PlanStatus.completed:
            logger.info(f"Plan {plan_id} completed, exiting supervision")
            return None

        if proc.returncode is not None:
            if p.status in (
                schemas.PlanStatus.creating,
                schemas.PlanStatus.created,
            ):
                logger.warning(
                    f"Process {pid} exited before plan {plan_id} started"
                )
                async with SessionLocal() as db:
                    await crud.set_status(
                        db,
                        plan_id,
                        schemas.PlanStatus.creation_error,
                        error=f"Process '{pid}' exited abnormally",
                    )
                return None


@contextmanager
def execution_directory(base_dir: Path | None) -> Generator[Path, None, None]:
    if base_dir:
        yield base_dir
    else:
        with TemporaryDirectory() as d:
            yield Path(d)


@lru_cache
def get_baseline_requirements() -> str:
    with importlib.resources.path("reliably_app.data", "requirements.txt") as p:
        if not p.absolute().is_file():
            return ""

        return p.read_text()
