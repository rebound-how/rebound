import logging
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, cast

from pydantic import UUID4
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app.series import models
from reliably_app.series.crud import experiment, org  # noqa

__all__ = [
    "get_series_by_kind",
    "transform_series",
    "transform_contributions_series",
    "to_utc_timestamp",
]
logger = logging.getLogger("reliably_app")


async def get_series_by_kind(
    db: AsyncSession,
    org_id: UUID4,
    kind: str,
    exp_id: UUID4 | None = None,
    limit: int | None = 100,
    page: int | None = 0,
) -> models.Series | None:
    """
    Given a series, return its data bound by the window defined by page/limit.
    """
    q = select(models.Series).where(models.Series.org_id == str(org_id))
    q = q.where(models.Series.kind == kind)

    if exp_id:
        q = q.where(models.Series.experiment_id == str(exp_id))

    if limit is not None and page is not None:
        q = (
            q.order_by(asc(models.Series.created_date))
            .offset(page)
            .limit(limit)
        )

    return (await db.execute(q)).scalars().first()


def to_utc_timestamp(ts: str) -> float:
    """
    Convert a Chaos Toolkit timestamp to a UTC datetime and return it as
    an epoch timestamp.
    """
    return (
        datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )


def transform_series(
    series: models.Series, offset: int | None = 0, count: int | None = 1
) -> Dict[str, Any]:
    """
    Transform any recorded series and prepare it to be handled on the client
    side in an uniform way.
    """
    s: Dict[str, Any] = {"labels": [], "datasets": []}
    results = cast(List, series.data)  # noqa: E203
    if (offset is not None) and (count is not None):
        results = results[-count:]
    num_results = len(results)

    by_locs = {}
    collated = []
    for loc in ("ssh-before", "method", "ssh-after", "rollback"):
        global_loc = {
            "name": loc,
            "data": [None] * num_results,
            "stack": "aggregate",
        }
        by_locs[loc] = global_loc
        collated.append(global_loc)

    for j, r in enumerate(results):
        collated_durations: Dict[str, int | None] = {
            "ssh-before": None,
            "ssh-after": None,
            "method": None,
            "rollback": None,
        }

        s["labels"].append(r["id"])
        for i, d in enumerate(r["data"]):
            try:
                serie = s["datasets"][i]
                serie["data"].append(d["data"][0])
            except IndexError:
                serie = deepcopy(d)
                serie["stack"] = "breakdown"
                s["datasets"].append(serie)

            c = collated_durations[serie["loc"]] or 0
            collated_durations[serie["loc"]] = c + (d["data"][0] or 0)

        for loc in collated_durations:
            by_locs[loc]["data"][j] = collated_durations[loc]  # type: ignore

    s["datasets"].extend(collated)
    return s


def transform_contributions_series(series: models.Series) -> Dict[str, Any]:
    s: Dict[str, Any] = {"labels": [], "datasets": [{"data": []}]}

    data = cast(Dict, series.data)

    for c, v in data.items():
        s["labels"].append(c)
        s["datasets"][0]["data"].append(v)

    return s
