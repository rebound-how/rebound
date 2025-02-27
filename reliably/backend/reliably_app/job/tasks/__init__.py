import asyncio
import logging
from datetime import datetime, timezone

from reliably_app import plan, snapshot
from reliably_app.database import SessionLocal
from reliably_app.job import crud, errors, schemas
from reliably_app.plan.providers import schedule_plan
from reliably_app.snapshot.tasks import schedule_discovery

__all__ = [
    "process_jobs",
]
logger = logging.getLogger("reliably_app")

TASKS: set[asyncio.Task] = set()
SUPERVISOR: asyncio.Task | None = None


async def process_jobs(event: asyncio.Event) -> None:
    global SUPERVISOR

    asyncio.create_task(populate_jobs())

    task = asyncio.create_task(process_all(event))
    task.add_done_callback(finished)
    SUPERVISOR = task


###############################################################################
# Private functions
###############################################################################
async def populate_jobs() -> None:
    await crud.batch_schedule_next()


def finished(task: asyncio.Task) -> None:
    global SUPERVISOR

    SUPERVISOR = None
    task.remove_done_callback(finished)

    if task.done():
        if task.cancelled():
            logger.info("Job supervisor was cancelled")
        else:
            x = task.exception()
            if x is not None:
                logger.error("Job supervisor errored", exc_info=x)


async def process_all(event: asyncio.Event) -> None:
    while not event.is_set():
        job_ids = []
        utcnow = (
            datetime.now()
            .astimezone(tz=timezone.utc)
            .replace(second=0, microsecond=0)
        )

        async with SessionLocal() as db:
            jobs = await crud.get_next_jobs(db, utcnow)
            job_ids = [str(j) for j in jobs]

        if job_ids:
            logger.debug(
                f"Found {len(job_ids)} jobs run at {utcnow.isoformat()}"
            )
            for job_id in job_ids:
                new_task(job_id)
            job_ids.clear()

        await asyncio.sleep(60)


async def process_one(job_id: str) -> None:
    logger.info(f"Processing job {job_id}")

    async with SessionLocal() as db:
        db_job = await crud.get_job(db, job_id)
        if not db_job:
            return None

        if not db_job.claimed:
            await crud.claim_job(db, job_id)

        job = schemas.Job.model_validate(db_job, from_attributes=True)

        await crud.schedule_next(job_id, str(db_job.pattern), job.timezone)

    match job.definition.type:
        case "plan":
            try:
                await process_plan_job(job)
            except plan.errors.PlanFailedError as x:
                raise errors.JobError(job_id, x.message) from x

        case "snapshot":
            try:
                await process_snapshot_job(job)
            except snapshot.errors.DiscoveryError as x:
                raise errors.JobError(job_id, x.message) from x


async def process_plan_job(job: schemas.Job) -> None:
    plan_id = job.definition.plan_id  # type: ignore
    logger.info(f"Processing plan {plan_id} from Job {job.id}")

    async with SessionLocal() as db:
        p = await plan.crud.get_plan(db, plan_id)
        if not p:
            return None

    task = plan.schemas.Plan.model_validate(p, from_attributes=True)

    await schedule_plan(task, str(job.org_id), str(job.user_id), None)


async def process_snapshot_job(job: schemas.Job) -> None:
    integration_id = job.definition.integration_id  # type: ignore
    logger.info(f"Discovering resources {integration_id} from Job {job.id}")

    await schedule_discovery(
        str(integration_id),
        str(job.org_id),
        str(job.user_id),
        str(job.definition.agent_id) if job.definition.agent_id else None,  # type: ignore
    )


def forget_task(task: asyncio.Task) -> None:
    try:
        TASKS.remove(task)
    except KeyError:
        pass

    job_id = task.get_name()
    logger.info(f"Removing Job {job_id} background task")

    task.remove_done_callback(forget_task)

    if task.done():
        if task.cancelled():
            logger.info(f"Job {job_id} was cancelled")
        else:
            x = task.exception()
            if x is not None:
                logger.warning(f"Job {job_id} errored", exc_info=x)


def new_task(job_id: str) -> None:
    t = asyncio.create_task(process_one(job_id), name=job_id)
    TASKS.add(t)
    t.add_done_callback(forget_task)

    logger.debug(f"Running Job {job_id} in background")
