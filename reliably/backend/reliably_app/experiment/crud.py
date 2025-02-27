import logging
from typing import Any, Dict, List, cast

from pydantic import UUID4
from sqlalchemy import String, asc, delete, desc, func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import bindparam

from reliably_app.database import DictBundle, SessionLocal
from reliably_app.experiment import models, schemas

__all__ = [
    "does_experiment_belong_to_org",
    "create_experiment",
    "get_experiment",
    "get_experiments",
    "delete_experiment",
    "count_experiments",
    "get_all_experiments",
    "get_experiments_summary",
    "search_experiments_by_title",
    "replace_experiment",
]
logger = logging.getLogger("reliably_app")


async def create_experiment(
    db: AsyncSession, org_id: UUID4, exp: schemas.ExperimentCreate
) -> models.Experiment:
    db_exp = models.Experiment(
        org_id=org_id, template_id=exp.template_id, definition=exp.definition
    )
    db.add(db_exp)
    await db.commit()

    db_exp_id = db_exp.id
    async with SessionLocal() as session:
        add_control_block(str(org_id), str(db_exp_id), exp.definition)

        await session.execute(
            update(models.Experiment)
            .where(models.Experiment.id == db_exp_id)
            .values(definition=exp.definition)
        )
        await session.commit()

    return cast(models.Experiment, db_exp)


async def count_experiments(db: AsyncSession, org_id: UUID4) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.Experiment.id)).where(
                    models.Experiment.org_id == str(org_id)
                )
            )
        ).scalar_one(),
    )


async def get_experiment(
    db: AsyncSession, exp_id: UUID4
) -> models.Experiment | None:
    return cast(models.Experiment, await db.get(models.Experiment, str(exp_id)))


async def get_experiments(
    db: AsyncSession, org_id: UUID4, page: int = 0, limit: int = 10
) -> List[models.Experiment]:
    results = await db.execute(
        select(models.Experiment)
        .where(models.Experiment.org_id == str(org_id))
        .order_by(asc(models.Experiment.definition["title"]))
        .offset(page)
        .limit(limit)
    )
    return results.scalars().all()


async def get_all_experiments(
    db: AsyncSession, org_id: UUID4
) -> List[Dict[str, str]]:
    results = await db.execute(
        select(
            DictBundle(
                "x",
                models.Experiment.id.label("id"),
                models.Experiment.definition["title"].label("title"),
                models.Experiment.executions_count.label("executions_count"),
            ),
        )
        .where(models.Experiment.org_id == str(org_id))
        .order_by(asc(models.Experiment.definition["title"]))
    )
    return results.scalars().all()


async def get_experiments_summary(
    db: AsyncSession, org_id: UUID4, page: int = 0, limit: int = 10
) -> List[Dict[str, Any]]:
    from reliably_app import execution, series

    results = await db.execute(
        select(
            DictBundle(
                "x",
                models.Experiment.id.label("id"),
                models.Experiment.created_date.label("created_date"),
                models.Experiment.definition["title"].label("title"),
                models.Experiment.definition["description"].label("desc"),
                models.Experiment.executions_count.label("executions_count"),
            )
        )
        .where(models.Experiment.org_id == str(org_id))
        .order_by(asc(models.Experiment.definition["title"]))
        .offset(page)
        .limit(limit)
    )
    experiments = results.scalars().all()
    x_ids = list(set([x["id"] for x in experiments]))

    executions = []
    for x_id in x_ids:
        results = await db.execute(
            select(
                DictBundle(
                    "x",
                    execution.models.Execution.experiment_id.label("exp_id"),
                    execution.models.Execution.created_date.label(
                        "created_date"
                    ),
                    execution.models.Execution.result["status"].label("status"),
                )
            )
            .where(execution.models.Execution.org_id == str(org_id))
            .where(execution.models.Execution.experiment_id == x_id)
            .order_by(desc(execution.models.Execution.created_date))
            .limit(5)
        )
        executions.extend(results.scalars().all())

    results = await db.execute(
        select(
            DictBundle(
                "x",
                series.models.Series.experiment_id.label("exp_id"),
                series.models.Series.data["score"].label("score"),
                series.models.Series.data["lasts"].label("trend"),
            )
        )
        .where(series.models.Series.org_id == str(org_id))
        .where(series.models.Series.kind == "exp-scores")
        .where(series.models.Series.experiment_id.in_(x_ids))
    )
    scores = results.scalars().all()

    x_mapping = {
        x["id"]: {
            "id": x["id"],
            "created_by": None,
            "created_date": x["created_date"],
            "title": x["title"],
            "desc": x["desc"],
            "org_id": str(org_id),
            "last_statuses": [],
            "last_execution": None,
            "score": None,
            "trend": [],
            "executions_count": int(x["executions_count"]),
        }
        for x in experiments
    }

    for xc in executions:
        x_mapping[xc["exp_id"]]["last_statuses"].append(xc["status"])
        if x_mapping[xc["exp_id"]]["last_execution"] is None:
            x_mapping[xc["exp_id"]]["last_execution"] = xc["created_date"]

    for sc in scores:
        x_mapping[sc["exp_id"]]["score"] = sc["score"]
        x_mapping[sc["exp_id"]]["trend"] = sc["trend"]

    return list(x_mapping.values())


async def delete_experiment(db: AsyncSession, exp_id: UUID4) -> None:
    await db.execute(
        delete(models.Experiment).where(models.Experiment.id == str(exp_id))
    )
    await db.commit()


async def replace_experiment(
    db: AsyncSession, exp: models.Experiment, new_exp: schemas.ExperimentEdit
) -> None:
    exp.definition = new_exp.experiment  # type: ignore
    db.add(exp)
    await db.commit()


async def does_experiment_belong_to_org(
    db: AsyncSession,
    org_id: UUID4,
    exp_id: UUID4,
) -> bool:
    result = await db.execute(
        select(models.Experiment.id)
        .where(models.Experiment.id == str(exp_id))
        .where(models.Experiment.org_id == str(org_id))
    )
    return result.scalar() is not None


def add_control_block(
    org_id: str, exp_id: str, experiment: Dict[str, Any]
) -> None:
    """
    Adds the control block to the experiment
    """
    c = experiment.setdefault("controls", [])
    c.append(
        {
            "name": "reliably",
            "provider": {
                "type": "python",
                "module": "chaosreliably.controls.experiment",
                "arguments": {
                    "org_id": org_id,
                    "exp_id": exp_id,
                },
            },
        }
    )


async def update_executions_count(
    db: AsyncSession, org_id: UUID4, exp_id: UUID4
) -> None:
    from reliably_app import execution

    await db.execute(
        update(models.Experiment)
        .where(models.Experiment.id == str(exp_id))
        .where(models.Experiment.org_id == str(org_id))
        .values(
            executions_count=select(func.count(execution.models.Execution.id))
            .where(execution.models.Execution.org_id == str(org_id))
            .where(execution.models.Execution.experiment_id == str(exp_id))
            .scalar_subquery()
        )
    )
    await db.commit()


async def total_executions_per_org(db: AsyncSession, org_id: UUID4) -> int:
    r = await db.execute(
        select(func.sum(models.Experiment.executions_count)).where(
            models.Experiment.org_id == str(org_id)
        )
    )

    return cast(int, r.scalar_one())


async def total_experiments_per_org(db: AsyncSession, org_id: UUID4) -> int:
    r = await db.execute(
        select(func.count(models.Experiment.id)).where(
            models.Experiment.org_id == str(org_id)
        )
    )

    return cast(int, r.scalar_one())


async def search_experiments_by_title(
    db: AsyncSession, org_id: UUID4, term: str, page: int = 0, limit: int = 10
) -> List[models.Experiment]:
    result = await db.execute(
        select(models.Experiment)
        .where(models.Experiment.org_id == str(org_id))
        .where(
            text(
                f"COALESCE({models.Experiment.__tablename__}.definition ->> 'title', '') like :search_text"  # noqa
            ).bindparams(bindparam("search_text", f"%{term}%", String))
        )
        .order_by(desc(models.Experiment.created_date))
        .offset(page)
        .limit(limit)
    )
    return result.scalars().all()


async def search_experiments_summary_by_title(
    db: AsyncSession, org_id: UUID4, term: str, page: int = 0, limit: int = 10
) -> List[Dict[str, Any]]:
    from reliably_app import execution, series

    results = await db.execute(
        select(
            DictBundle(
                "x",
                models.Experiment.id.label("id"),
                models.Experiment.created_date.label("created_date"),
                models.Experiment.definition["title"].label("title"),
                models.Experiment.definition["description"].label("desc"),
                models.Experiment.executions_count.label("executions_count"),
            )
        )
        .where(models.Experiment.org_id == str(org_id))
        .where(
            text(
                f"COALESCE({models.Experiment.__tablename__}.definition ->> 'title', '') ilike :search_text"  # noqa
            ).bindparams(bindparam("search_text", f"%{term}%", String))
        )
        .order_by(asc(models.Experiment.definition["title"]))
        .offset(page)
        .limit(limit)
    )
    experiments = results.scalars().all()
    x_ids = list(set([x["id"] for x in experiments]))

    executions = []
    for x_id in x_ids:
        results = await db.execute(
            select(
                DictBundle(
                    "x",
                    execution.models.Execution.experiment_id.label("exp_id"),
                    execution.models.Execution.created_date.label(
                        "created_date"
                    ),
                    execution.models.Execution.result["status"].label("status"),
                )
            )
            .where(execution.models.Execution.org_id == str(org_id))
            .where(execution.models.Execution.experiment_id == x_id)
            .order_by(desc(execution.models.Execution.created_date))
            .limit(5)
        )
        executions.extend(results.scalars().all())

    results = await db.execute(
        select(
            DictBundle(
                "x",
                series.models.Series.experiment_id.label("exp_id"),
                series.models.Series.data["score"].label("score"),
                series.models.Series.data["lasts"].label("trend"),
            )
        )
        .where(series.models.Series.org_id == str(org_id))
        .where(series.models.Series.kind == "exp-scores")
        .where(series.models.Series.experiment_id.in_(x_ids))
    )
    scores = results.scalars().all()

    x_mapping = {
        x["id"]: {
            "id": x["id"],
            "created_by": None,
            "created_date": x["created_date"],
            "title": x["title"],
            "desc": x["desc"],
            "org_id": str(org_id),
            "last_statuses": [],
            "last_execution": None,
            "score": None,
            "trend": [],
            "executions_count": int(x["executions_count"]),
        }
        for x in experiments
    }

    for xc in executions:
        x_mapping[xc["exp_id"]]["last_statuses"].append(xc["status"])
        if x_mapping[xc["exp_id"]]["last_execution"] is None:
            x_mapping[xc["exp_id"]]["last_execution"] = xc["created_date"]

    for sc in scores:
        x_mapping[sc["exp_id"]]["score"] = sc["score"]
        x_mapping[sc["exp_id"]]["trend"] = sc["trend"]

    return list(x_mapping.values())


async def count_experiments_summary_by_title(
    db: AsyncSession, org_id: UUID4, term: str, page: int = 0, limit: int = 10
) -> int:
    result = await db.execute(
        select(func.count(models.Experiment.id))
        .where(models.Experiment.org_id == str(org_id))
        .where(
            text(
                f"COALESCE({models.Experiment.__tablename__}.definition ->> 'title', '') ilike :search_text"  # noqa
            ).bindparams(bindparam("search_text", f"%{term}%", String))
        )
    )
    return cast(int, result.scalar())


async def get_experiment_summary(
    db: AsyncSession, org_id: UUID4, experiment_id: UUID4
) -> Dict[str, Any]:
    from reliably_app import execution, series

    results = await db.execute(
        select(
            DictBundle(
                "x",
                models.Experiment.id.label("id"),
                models.Experiment.created_date.label("created_date"),
                models.Experiment.definition["title"].label("title"),
                models.Experiment.definition["description"].label("desc"),
                models.Experiment.executions_count.label("executions_count"),
            )
        )
        .where(models.Experiment.org_id == str(org_id))
        .where(models.Experiment.id == str(experiment_id))
    )
    exp = results.scalars().first()
    x_id = str(exp["id"])  # type: ignore

    executions = []
    results = await db.execute(
        select(
            DictBundle(
                "x",
                execution.models.Execution.experiment_id.label("exp_id"),
                execution.models.Execution.created_date.label("created_date"),
                execution.models.Execution.result["status"].label("status"),
            )
        )
        .where(execution.models.Execution.org_id == str(org_id))
        .where(execution.models.Execution.experiment_id == x_id)
        .order_by(desc(execution.models.Execution.created_date))
        .limit(5)
    )
    executions.extend(results.scalars().all())

    results = await db.execute(
        select(
            DictBundle(
                "x",
                series.models.Series.experiment_id.label("exp_id"),
                series.models.Series.data["score"].label("score"),
                series.models.Series.data["lasts"].label("trend"),
            )
        )
        .where(series.models.Series.org_id == str(org_id))
        .where(series.models.Series.kind == "exp-scores")
        .where(series.models.Series.experiment_id == x_id)
    )
    scores = results.scalars().all()

    x_mapping = {
        "id": exp["id"],  # type: ignore
        "created_by": None,
        "created_date": exp["created_date"],  # type: ignore
        "title": exp["title"],  # type: ignore
        "desc": exp["desc"],  # type: ignore
        "org_id": str(org_id),
        "last_statuses": [],
        "last_execution": None,
        "score": None,
        "trend": [],
        "executions_count": int(exp["executions_count"]),  # type: ignore
    }

    for xc in executions:
        x_mapping["last_statuses"].append(xc["status"])
        if x_mapping["last_execution"] is None:
            x_mapping["last_execution"] = xc["created_date"]

    for sc in scores:
        x_mapping["score"] = sc["score"]
        x_mapping["trend"] = sc["trend"]

    return x_mapping
