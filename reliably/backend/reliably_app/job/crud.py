import logging
from datetime import datetime, timezone
from typing import List, Literal, cast

import orjson
import pytz
from croniter import croniter
from pydantic import UUID4, AwareDatetime
from sqlalchemy import delete, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app.database import SessionLocal
from reliably_app.job import models, schemas

__all__ = [
    "create_job",
    "count_jobs",
    "get_job",
    "get_jobs",
]
logger = logging.getLogger("reliably_app")


async def create_job(
    db: AsyncSession,
    org_id: UUID4 | str,
    job: schemas.JobCreate,
) -> models.Job:
    db_job = models.Job(
        org_id=str(org_id),
        claimed=False,
        user_id=str(job.user_id),
        next_run_date=job.next_run_date,
        pattern=job.pattern,
        timezone=job.timezone,
        suspended=False,
        definition=orjson.loads(job.definition.model_dump_json()),
    )
    db.add(db_job)
    await db.commit()

    return cast(models.Job, db_job)


async def count_jobs(db: AsyncSession, org_id: UUID4) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.Job.id)).where(
                    models.Job.org_id == str(org_id)
                )
            )
        ).scalar_one(),
    )


async def get_job(db: AsyncSession, job_id: UUID4 | str) -> models.Job | None:
    return cast(models.Job, await db.get(models.Job, str(job_id)))


async def get_jobs(
    db: AsyncSession, org_id: UUID4, page: int = 0, limit: int = 10
) -> List[models.Job]:
    results = await db.execute(
        select(models.Job)
        .where(models.Job.org_id == str(org_id))
        .offset(page)
        .limit(limit)
    )
    return results.scalars().all()


async def get_non_errored_jobs(
    db: AsyncSession, org_id: UUID4
) -> List[models.Job]:
    results = await db.execute(
        select(models.Job)
        .where(models.Job.org_id == str(org_id))
        .where(models.Job.errored.is_(None))  # noqa
    )
    return results.scalars().all()


async def get_job_by_type(
    db: AsyncSession,
    org_id: UUID4 | str,
    type: Literal["plan", "snapshot"],
    type_key: str,
    type_value: str,
) -> models.Job | None:
    result = await db.execute(
        select(models.Job)
        .where(models.Job.org_id == str(org_id))
        .where(models.Job.definition["type"].astext == type)
        .where(models.Job.definition[type_key].astext == type_value)
        .order_by(desc(models.Job.created_date))
        .limit(1)
    )
    return result.scalars().first()


async def get_most_recent_job_by_type(
    db: AsyncSession,
    org_id: UUID4 | str,
    type: Literal["plan", "snapshot"],
) -> models.Job | None:
    result = await db.execute(
        select(models.Job)
        .where(models.Job.org_id == str(org_id))
        .where(models.Job.definition["type"].astext == type)
        .order_by(desc(models.Job.created_date))
        .limit(1)
    )
    return result.scalars().first()


async def claim_job(db: AsyncSession, job_id: str) -> None:
    await db.execute(
        update(models.Job).where(models.Job.id == job_id).values(claimed=True)
    )

    await db.commit()


async def run_next_at(db: AsyncSession, job_id: str, dt: datetime) -> None:
    await db.execute(
        update(models.Job)
        .where(models.Job.id == job_id)
        .values(next_run_date=dt)
    )

    await db.commit()


async def get_next_jobs(db: AsyncSession, d: datetime) -> List[UUID4]:
    results = await db.execute(
        select(models.Job.id)
        .where(models.Job.next_run_date == d)
        .where(models.Job.suspended.is_(False))
    )

    return results.scalars().all()


async def enqueue_job(org_id: UUID4 | str, job: schemas.JobCreate) -> None:
    async with SessionLocal() as db:
        logger.debug("Enqueuing new job")

        if not job.next_run_date:
            dt = get_next_run_at_datetime(job.pattern, job.timezone)
            job.next_run_date = dt

        db_job = await create_job(db, org_id, job)

        logger.info(
            f"Job {str(db_job.id)} enqueued. Run will occur on "
            f"{job.next_run_date.isoformat()}"
        )


async def remove_job(
    db: AsyncSession, org_id: UUID4 | str, job_id: UUID4 | str
) -> None:
    await db.execute(
        delete(models.Job)
        .where(models.Job.org_id == str(org_id))
        .where(models.Job.id == str(job_id))
    )

    await db.commit()


async def resume_job(
    db: AsyncSession, org_id: UUID4 | str, job_id: UUID4 | str
) -> None:
    await db.execute(
        update(models.Job)
        .where(models.Job.org_id == str(org_id))
        .where(models.Job.id == str(job_id))
        .values(suspended=False)
    )

    await db.commit()


async def suspend_job(
    db: AsyncSession, org_id: UUID4 | str, job_id: UUID4 | str
) -> None:
    await db.execute(
        update(models.Job)
        .where(models.Job.org_id == str(org_id))
        .where(models.Job.id == str(job_id))
        .values(suspended=True)
    )

    await db.commit()


async def schedule_next(job_id: str, pattern: str, tz: str | None) -> None:
    run_at = get_next_run_at_datetime(pattern, tz)
    logger.info(f"Scheduling Job {job_id} next run at {run_at.isoformat()}")

    async with SessionLocal() as db:
        await run_next_at(db, job_id, run_at)


def get_next_run_at_datetime(
    pattern: str, tz: str | None = "Etc/UTC"
) -> AwareDatetime:
    if not tz:
        tzone = pytz.utc
    else:
        tzone = pytz.timezone(tz)  # type: ignore

    utcnow = datetime.now().astimezone(tz=tzone)
    iter = croniter(pattern, utcnow, ret_type=datetime)
    run_at: datetime = next(iter)
    return run_at.replace(second=0, microsecond=0)


async def batch_schedule_next() -> None:
    utcnow = (
        datetime.now()
        .astimezone(tz=timezone.utc)
        .replace(second=0, microsecond=0)
    )
    logger.debug(
        "Looking for any jobs that should be re-scheduled "
        f"after {utcnow.isoformat()}"
    )

    async with SessionLocal() as db:
        results = await db.execute(
            select(models.Job)
            .where(models.Job.errored.is_not(True))  # noqa
            .where(models.Job.next_run_date < utcnow)
        )
        jobs = results.scalars().all()

        for job in jobs:
            run_at = get_next_run_at_datetime(job.pattern, job.timezone)
            logger.info(f"Rescheduling Job {job.id} at {run_at}")
            await db.execute(
                update(models.Job)
                .where(models.Job.id == str(job.id))
                .values(next_run_date=run_at)
            )

        await db.commit()
