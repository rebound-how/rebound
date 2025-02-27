import logging
from datetime import date, datetime, timezone
from typing import Any, Dict

from pydantic import UUID4
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from reliably_app.database import SessionLocal
from reliably_app.series import models

__all__ = [
    "initialize_org_series",
    "has_org_series",
    "delete_org_series",
    "consume_execution",
    "consume_experiment",
    "drop_experiment",
    "drop_execution",
]
logger = logging.getLogger("reliably_app")


async def initialize_org_series(org_id: UUID4) -> None:
    async with SessionLocal() as db:
        db.add(
            models.Series(
                kind="org-executions-dist-per-day",
                org_id=org_id,
                experiment_id=None,
                execution_id=None,
                plan_id=None,
                data={},
            )
        )

        db.add(
            models.Series(
                kind="org-contributions-for-experiments",
                org_id=org_id,
                experiment_id=None,
                execution_id=None,
                plan_id=None,
                data={},
            )
        )

        db.add(
            models.Series(
                kind="org-contributions-for-executions",
                org_id=org_id,
                experiment_id=None,
                execution_id=None,
                plan_id=None,
                data={"experiments": {}},
            )
        )

        await db.commit()


async def has_org_series(db: AsyncSession, org_id: UUID4) -> bool:
    q = (
        select(models.Series.id)
        .where(models.Series.org_id == str(org_id))
        .where(models.Series.experiment_id.is_(None))
        .limit(1)
    )

    return (await db.execute(q)).scalars().first() is not None


async def delete_org_series(db: AsyncSession, org_id: UUID4) -> None:
    q = delete(models.Series)
    q = q.where(models.Series.org_id == str(org_id))

    await db.execute(q)
    await db.commit()


async def consume_execution(
    org_id: UUID4, exp_id: UUID4, exec_id: UUID4, journal: Dict[str, Any]
) -> None:
    async with SessionLocal() as db:
        r = (
            (
                await db.execute(
                    select(models.Series)
                    .where(models.Series.org_id == str(org_id))
                    .where(
                        models.Series.kind == "org-contributions-for-executions"
                    )
                    .order_by(desc(models.Series.created_date))
                    .limit(1)
                    .with_for_update()
                )
            )
            .scalars()
            .first()
        )

        if r:
            if (
                add_contributions_from_executions(
                    r.data, exp_id, exec_id, journal
                )
                is True
            ):
                # tell SA that we changed something
                flag_modified(r, "data")
                await db.commit()
            else:
                await db.rollback()

    async with SessionLocal() as db:
        r = (
            (
                await db.execute(
                    select(models.Series)
                    .where(models.Series.org_id == str(org_id))
                    .where(models.Series.kind == "org-executions-dist-per-day")
                    .order_by(desc(models.Series.created_date))
                    .limit(1)
                    .with_for_update()
                )
            )
            .scalars()
            .first()
        )

        if r:
            if add_results_to_distribution(r.data, journal) is True:
                # tell SA that we changed something
                flag_modified(r, "data")
                await db.commit()
            else:
                await db.rollback()


async def drop_execution(
    org_id: UUID4, exp_id: UUID4, exec_id: UUID4 | None, journal: Dict[str, Any]
) -> None:
    if not exec_id:
        async with SessionLocal() as db:
            r = (
                (
                    await db.execute(
                        select(models.Series)
                        .where(models.Series.org_id == str(org_id))
                        .where(
                            models.Series.kind
                            == "org-contributions-for-executions"
                        )
                        .order_by(desc(models.Series.created_date))
                        .limit(1)
                        .with_for_update()
                    )
                )
                .scalars()
                .first()
            )

            if r:
                if (
                    remove_contributions_from_execution(r.data, exp_id, exec_id)
                    is True
                ):
                    # tell SA that we changed something
                    flag_modified(r, "data")
                    await db.commit()
                else:
                    await db.rollback()

    async with SessionLocal() as db:
        r = (
            (
                await db.execute(
                    select(models.Series)
                    .where(models.Series.org_id == str(org_id))
                    .where(models.Series.kind == "org-executions-dist-per-day")
                    .order_by(desc(models.Series.created_date))
                    .limit(1)
                    .with_for_update()
                )
            )
            .scalars()
            .first()
        )

        if r:
            if remove_results_from_distribution(r.data, journal) is True:
                # tell SA that we changed something
                flag_modified(r, "data")
                await db.commit()
            else:
                await db.rollback()

    return None


async def consume_experiment(org_id: UUID4, experiment: Dict[str, Any]) -> None:
    async with SessionLocal() as db:
        r = (
            (
                await db.execute(
                    select(models.Series)
                    .where(models.Series.org_id == str(org_id))
                    .where(
                        models.Series.kind
                        == "org-contributions-for-experiments"
                    )
                    .order_by(desc(models.Series.created_date))
                    .limit(1)
                    .with_for_update()
                )
            )
            .scalars()
            .first()
        )

        if r:
            if add_contributions_from_experiment(r.data, experiment) is True:
                # tell SA that we changed something
                flag_modified(r, "data")
                await db.commit()
            else:
                await db.rollback()

    return None


async def drop_experiment(
    org_id: UUID4,
    exp_id: UUID4,
    experiment: Dict[str, Any],
) -> None:
    async with SessionLocal() as db:
        r = (
            (
                await db.execute(
                    select(models.Series)
                    .where(models.Series.org_id == str(org_id))
                    .where(
                        models.Series.kind
                        == "org-contributions-for-experiments"
                    )
                    .order_by(desc(models.Series.created_date))
                    .limit(1)
                    .with_for_update()
                )
            )
            .scalars()
            .first()
        )

        if r:
            if remove_contributions_from_experiment(r.data, experiment) is True:
                # tell SA that we changed something
                flag_modified(r, "data")
                await db.commit()
            else:
                await db.rollback()

    async with SessionLocal() as db:
        r = (
            (
                await db.execute(
                    select(models.Series)
                    .where(models.Series.org_id == str(org_id))
                    .where(
                        models.Series.kind == "org-contributions-for-executions"
                    )
                    .order_by(desc(models.Series.created_date))
                    .limit(1)
                    .with_for_update()
                )
            )
            .scalars()
            .first()
        )

        if r:
            if remove_contributions_from_execution(r.data, exp_id) is True:
                # tell SA that we changed something
                flag_modified(r, "data")
                await db.commit()
            else:
                await db.rollback()

    return None


###############################################################################
# Internal series handling functions
###############################################################################
def to_date(ts: str) -> date:
    """
    Convert a Chaos Toolkit timestamp to its date only.
    """
    return (
        datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
        .replace(tzinfo=timezone.utc)
        .date()
    )


def add_contributions_from_executions(
    recorded_contribs: Dict[str, Dict[str, Any]],
    exp_id: UUID4,
    exec_id: UUID4,
    journal: Dict[str, Any],
) -> bool:
    start = journal.get("start")
    if not start:
        return False

    x = journal.get("experiment", {})
    title = x.get("title")
    contributions = x.get("contributions", {})
    experiments = recorded_contribs.get("experiments", {})

    x_id = str(exp_id)
    xc_id = str(exec_id)

    current = experiments.setdefault(x_id, {"x": [], "c": {}, "t": None})
    current["c"] = contributions
    current["t"] = title
    current["x"].append((xc_id, start))

    return True


def remove_contributions_from_execution(
    recorded_contribs: Dict[str, Dict[str, Any]],
    exp_id: UUID4,
    exec_id: UUID4 | None = None,
) -> bool:
    x_id = str(exp_id)
    experiments = recorded_contribs.get("experiments", {})
    if x_id not in experiments:
        return False

    if exec_id:
        xc_id = str(exec_id)
        for key in experiments[x_id]["x"]:
            if key[0] == xc_id:
                experiments[x_id]["x"].remove(key)
                break
    else:
        experiments.pop(x_id)

    return True


def add_contributions_from_experiment(
    recorded_contribs: Dict[str, int], experiment: Dict[str, Any]
) -> bool:
    contributions = experiment.get("contributions", {})
    if not contributions:
        return False

    for c in contributions:
        c = c.lower()
        if c in recorded_contribs:
            recorded_contribs[c] = recorded_contribs[c] + 1
        else:
            recorded_contribs[c] = 1

    return True


def remove_contributions_from_experiment(
    recorded_contribs: Dict[str, int], experiment: Dict[str, Any]
) -> bool:
    contributions = experiment.get("contributions")
    if not contributions:
        return False

    for c in contributions:
        c = c.lower()
        if c in recorded_contribs:
            recorded_contribs[c] = recorded_contribs[c] - 1
            if recorded_contribs[c] < 1:
                recorded_contribs.pop(c, None)
        else:
            recorded_contribs.pop(c, None)

    return True


def add_results_to_distribution(
    dist: Dict[str, Dict[str, Any]],
    journal: Dict[str, Any],
) -> bool:
    start = journal.get("start")
    if not start:
        return False

    dt = str(to_date(start))

    r = dist.setdefault(
        dt,
        {
            "deviated": 0,
            "failed": 0,
            "completed": 0,
            "interrupted": 0,
            "aborted": 0,
            "total": 0,
        },
    )

    r["total"] += 1

    if journal.get("deviated"):
        r["deviated"] += 1
    elif journal.get("status") == "failed":
        r["failed"] += 1
    elif journal.get("status") == "completed":
        r["completed"] += 1
    elif journal.get("status") == "interrupted":
        r["interrupted"] += 1
    elif journal.get("status") == "aborted":
        r["aborted"] += 1

    return True


def remove_results_from_distribution(
    dist: Dict[str, Dict[str, Any]],
    journal: Dict[str, Any],
) -> bool:
    start = journal.get("start")
    if not start:
        return False

    dt = str(to_date(start))

    r = dist.get(dt)
    if not r:
        return False

    r["total"] -= 1

    if journal.get("deviated"):
        r["deviated"] -= 1
    elif journal.get("status") == "failed":
        r["failed"] -= 1
    elif journal.get("status") == "completed":
        r["completed"] -= 1
    elif journal.get("status") == "aborted":
        r["aborted"] -= 1

    # back to zeros... let's not waste space
    if dist and any(list(r.values())) is False:
        dist.pop(dt, None)

    return True
