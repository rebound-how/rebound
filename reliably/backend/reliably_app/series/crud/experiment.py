import logging
from collections import deque
from datetime import date, datetime, timezone
from statistics import fmean
from typing import Any, Dict, List

from pydantic import UUID4
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from reliably_app.database import SessionLocal
from reliably_app.series import models

__all__ = [
    "initialize_experiment_series",
    "has_experiment_series",
    "delete_experiment_series",
    "consume_execution",
    "consume_experiment",
    "drop_experiment",
    "drop_execution",
]
logger = logging.getLogger("reliably_app")


async def initialize_experiment_series(
    org_id: UUID4, exp_id: UUID4, experiment: Dict[str, Any]
) -> None:
    async with SessionLocal() as db:
        db.add(
            models.Series(
                kind="exp-executions-dist-per-day",
                org_id=org_id,
                experiment_id=exp_id,
                execution_id=None,
                plan_id=None,
                data={},
            )
        )

        db.add(
            models.Series(
                kind="exp-executions-as-series",
                org_id=org_id,
                experiment_id=exp_id,
                execution_id=None,
                plan_id=None,
                data=[],
            )
        )

        db.add(
            models.Series(
                kind="exp-scores",
                org_id=org_id,
                experiment_id=exp_id,
                execution_id=None,
                plan_id=None,
                data={},
            )
        )

        await db.commit()


async def has_experiment_series(
    db: AsyncSession, org_id: UUID4, exp_id: UUID4
) -> bool:
    q = select(models.Series.id)
    q = q.where(models.Series.org_id == str(org_id))
    q = q.where(models.Series.experiment_id == str(exp_id))
    q = q.limit(1)

    return (await db.execute(q)).scalars().first() is not None


async def delete_experiment_series(org_id: UUID4, exp_id: UUID4) -> None:
    async with SessionLocal() as db:
        q = delete(models.Series)
        q = q.where(models.Series.org_id == str(org_id))
        q = q.where(models.Series.experiment_id == str(exp_id))

        await db.execute(q)
        await db.commit()


async def consume_execution(
    org_id: UUID4,
    exp_id: UUID4,
    exec_id: UUID4,
    plan_id: UUID4 | None,
    journal: Dict[str, Any],
) -> None:
    async with SessionLocal() as db:
        r = (
            (
                await db.execute(
                    select(models.Series)
                    .where(models.Series.org_id == str(org_id))
                    .where(models.Series.experiment_id == str(exp_id))
                    .where(models.Series.kind == "exp-executions-as-series")
                    .order_by(desc(models.Series.created_date))
                    .limit(1)
                    .with_for_update()
                )
            )
            .scalars()
            .first()
        )

        if r:
            series = add_activities_duration(journal, exec_id)
            if series:
                r.data.append(series)
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
                    .where(models.Series.experiment_id == str(exp_id))
                    .where(models.Series.kind == "exp-executions-dist-per-day")
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

    async with SessionLocal() as db:
        r = (
            (
                await db.execute(
                    select(models.Series)
                    .where(models.Series.org_id == str(org_id))
                    .where(models.Series.experiment_id == str(exp_id))
                    .where(models.Series.kind == "exp-scores")
                    .order_by(desc(models.Series.created_date))
                    .limit(1)
                    .with_for_update()
                )
            )
            .scalars()
            .first()
        )

        if r:
            if update_experiment_scores(r.data, journal, exec_id) is True:
                # tell SA that we changed something
                flag_modified(r, "data")
                await db.commit()
            else:
                await db.rollback()


async def consume_experiment(org_id: UUID4, experiment: Dict[str, Any]) -> None:
    return None


async def drop_experiment(org_id: UUID4, experiment: Dict[str, Any]) -> None:
    return None


async def drop_execution(
    org_id: UUID4, exp_id: UUID4, exec_id: UUID4, journal: Dict[str, Any]
) -> None:
    async with SessionLocal() as db:
        r = (
            (
                await db.execute(
                    select(models.Series)
                    .where(models.Series.org_id == str(org_id))
                    .where(models.Series.experiment_id == str(exp_id))
                    .where(models.Series.kind == "exp-executions-as-series")
                    .order_by(desc(models.Series.created_date))
                    .limit(1)
                    .with_for_update()
                )
            )
            .scalars()
            .first()
        )

        if r:
            remove_activities_duration(r.data, exec_id)

            # tell SA that we changed something
            flag_modified(r, "data")

            await db.commit()

    async with SessionLocal() as db:
        r = (
            (
                await db.execute(
                    select(models.Series)
                    .where(models.Series.org_id == str(org_id))
                    .where(models.Series.experiment_id == str(exp_id))
                    .where(models.Series.kind == "exp-executions-dist-per-day")
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

    async with SessionLocal() as db:
        r = (
            (
                await db.execute(
                    select(models.Series)
                    .where(models.Series.org_id == str(org_id))
                    .where(models.Series.experiment_id == str(exp_id))
                    .where(models.Series.kind == "exp-scores")
                    .order_by(desc(models.Series.created_date))
                    .limit(1)
                    .with_for_update()
                )
            )
            .scalars()
            .first()
        )

        if r:
            if remove_experiment_scores(r.data, exec_id) is True:
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


def add_activities_duration(
    journal: Dict[str, Any], exec_id: UUID4
) -> Dict[str, Any] | None:
    start = journal.get("start")
    if not start:
        return None

    journal_dt_ts = to_date(start)

    activities = {}
    x = journal.get("experiment", {})
    ssh = x.get("steady-state-hypothesis", {})
    activities["ssh-before"] = ssh.get("probes", [])
    activities["method"] = x.get("method", [])
    activities["ssh-after"] = ssh.get("probes", [])
    activities["rollback"] = x.get("rollbacks", [])

    items = []
    for loc in activities:
        for activity in activities[loc]:
            item = {
                "name": activity["name"],
                "kind": activity["type"],
                "status": [None],
                "tolerance_met": [None],
                "loc": loc,
                "data": [None],
            }
            items.append(item)

    activities = {
        "ssh-before": [],
        "method": [],
        "ssh-after": [],
        "rollback": [],
    }

    ssh = journal.get("steady_states", {})
    activities["ssh-before"].extend((ssh.get("before") or {}).get("probes", []))
    activities["method"].extend(journal.get("run", []))
    activities["ssh-after"].extend((ssh.get("after") or {}).get("probes", []))
    activities["rollback"].extend(journal.get("rollbacks", []))

    index = 0
    for loc in ("ssh-before", "method", "ssh-after", "rollback"):
        for activity in activities[loc]:
            try:
                item = items[index]
            except IndexError:
                logger.warning(
                    f"Execution {exec_id}: index {index} outside of items "
                    f"boundaries: {items}"
                )
                continue
            item["data"][0] = activity.get("duration", 0)
            item["status"][0] = activity.get("status", None)
            item["tolerance_met"][0] = activity.get("tolerance_met", None)

            index = index + 1

    series = {"id": str(exec_id), "ts": journal_dt_ts, "data": items}

    return series


def remove_activities_duration(
    series: List[Dict[str, Any]], exec_id: UUID4
) -> None:
    for s in series:
        if s["id"] == exec_id:
            series.remove(s)
            break


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
        },
    )

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

    if journal.get("deviated"):
        r["deviated"] += 1
    elif journal.get("status") == "failed":
        r["failed"] += 1
    elif journal.get("status") == "completed":
        r["completed"] += 1
    elif journal.get("status") == "aborted":
        r["aborted"] += 1

    # back to zeros... let's not waste space
    if any(list(r.values())) is False:
        dist.pop(r, None)  # type: ignore

    return True


def update_experiment_scores(
    dist: Dict[str, Any], journal: Dict[str, Any], exec_id: UUID4
) -> bool:
    start = journal.get("start")
    if not start:
        return False

    last_results = deque(dist.get("lasts", []), 10)

    execution_score = 0.0
    if journal.get("deviated"):
        execution_score = 0.0
    elif journal.get("status") == "failed":
        execution_score = 0.5
    elif journal.get("status") == "completed":
        execution_score = 1.0
    elif journal.get("status") == "aborted":
        execution_score = 0.0

    dt = (
        datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%f")
        .replace(tzinfo=timezone.utc)
        .isoformat()
    )
    last_results.append((str(exec_id), dt, execution_score))
    dist["lasts"] = list(last_results)
    dist["score"] = fmean((s[2] for s in last_results))

    return True


def remove_experiment_scores(dist: Dict[str, Any], exec_id: UUID4) -> bool:
    execution_id = str(exec_id)

    last_results = dist.get("lasts", [])
    for pair in last_results:
        if pair[0] == execution_id:
            last_results.remove(pair)
            break

    dist["lasts"] = last_results

    if not last_results:
        dist["score"] = None
    else:
        dist["score"] = fmean((s[2] for s in last_results))

    return True
