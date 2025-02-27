from datetime import date, datetime, timedelta
from typing import Any, Dict, List, cast

from pydantic import UUID4
from sqlalchemy import (
    Boolean,
    asc,
    case,
    delete,
    desc,
    func,
    literal_column,
    select,
    text,
    update,
)
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app.database import DictBundle
from reliably_app.execution import models, schemas

__all__ = [
    "does_execution_belong_to_org",
    "is_execution_linked_to_experiment",
    "create_execution",
    "get_execution",
    "get_executions_by_org",
    "get_executions_by_experiment",
    "get_executions_by_plan",
    "delete_execution",
    "count_executions_by_org",
    "count_executions_by_plan",
    "count_executions_by_experiment",
    "delete_experiment_executions",
    "update_execution_result",
    "get_executions_summary",
]


async def create_execution(
    db: AsyncSession,
    org_id: UUID4,
    exp_id: UUID4,
    user_id: UUID4,
    exp: schemas.ExecutionCreate,
) -> models.Execution:
    db_exp = models.Execution(
        org_id=org_id,
        experiment_id=exp_id,
        plan_id=str(exp.plan_id) if exp.plan_id else None,
        user_id=str(user_id) if user_id else None,
        result=exp.result,
        log=exp.log,
        user_state=schemas.ExecutionPendingState().model_dump(),
    )
    db.add(db_exp)
    await db.commit()

    return cast(models.Execution, db_exp)


async def update_execution_result(
    db: AsyncSession,
    org_id: UUID4,
    exp_id: UUID4,
    exec_id: UUID4,
    payload: schemas.ExecutionCreate,
) -> None:
    q = (
        update(models.Execution)
        .where(models.Execution.id == str(exec_id))
        .where(models.Execution.experiment_id == str(exp_id))
        .where(models.Execution.org_id == str(org_id))
        .values(result=payload.result, log=payload.log)
    )

    await db.execute(q)
    await db.commit()


async def count_running_executions_by_org(
    db: AsyncSession, org_id: UUID4
) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.Execution.id))
                .where(models.Execution.org_id == str(org_id))
                .where(
                    models.Execution.user_state["current"].astext == "running"
                )
            )
        ).scalar_one(),
    )


async def count_executions_by_org(db: AsyncSession, org_id: UUID4) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.Execution.id)).where(
                    models.Execution.org_id == str(org_id)
                )
            )
        ).scalar_one(),
    )


async def count_executions_by_experiment(
    db: AsyncSession, exp_id: UUID4
) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.Execution.id)).where(
                    models.Execution.experiment_id == str(exp_id)
                )
            )
        ).scalar_one(),
    )


async def count_executions_by_plan(db: AsyncSession, plan_id: UUID4) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.Execution.id)).where(
                    models.Execution.plan_id == str(plan_id)
                )
            )
        ).scalar_one(),
    )


async def get_execution(
    db: AsyncSession, exec_id: UUID4
) -> models.Execution | None:
    return cast(models.Execution, await db.get(models.Execution, str(exec_id)))


async def get_execution_without_log(
    db: AsyncSession, exec_id: UUID4
) -> Row | None:
    results = await db.execute(
        select(
            models.Execution.id,
            models.Execution.created_date,
            models.Execution.org_id,
            models.Execution.experiment_id,
            models.Execution.plan_id,
            models.Execution.user_id,
            models.Execution.user_state,
            models.Execution.result,
        ).where(models.Execution.id == str(exec_id))
    )
    return results.first()


async def get_execution_without_log_nor_journal(
    db: AsyncSession, exec_id: UUID4
) -> Row | None:
    results = await db.execute(
        select(
            models.Execution.id,
            models.Execution.created_date,
            models.Execution.org_id,
            models.Execution.experiment_id,
            models.Execution.plan_id,
            models.Execution.user_id,
            models.Execution.user_state,
        ).where(models.Execution.id == str(exec_id))
    )
    return results.first()


async def get_executions_by_org(
    db: AsyncSession, org_id: UUID4, page: int = 0, limit: int = 10
) -> List[models.Execution]:
    results = await db.execute(
        select(models.Execution)
        .where(models.Execution.org_id == str(org_id))
        .order_by(desc(models.Execution.created_date))
        .offset(page)
        .limit(limit)
    )
    return results.scalars().all()


async def get_executions_by_experiment(
    db: AsyncSession, exp_id: UUID4, page: int = 0, limit: int = 10
) -> List[models.Execution]:
    results = await db.execute(
        select(models.Execution)
        .where(models.Execution.experiment_id == str(exp_id))
        .order_by(desc(models.Execution.created_date))
        .offset(page)
        .limit(limit)
    )
    return results.scalars().all()


async def get_executions_by_plan(
    db: AsyncSession, plan_id: UUID4, page: int = 0, limit: int = 10
) -> List[models.Execution]:
    results = await db.execute(
        select(models.Execution)
        .where(models.Execution.plan_id == str(plan_id))
        .order_by(desc(models.Execution.created_date))
        .offset(page)
        .limit(limit)
    )
    return results.scalars().all()


async def delete_execution(db: AsyncSession, exec_id: UUID4) -> None:
    await db.execute(
        delete(models.Execution).where(models.Execution.id == str(exec_id))
    )
    await db.commit()


async def delete_experiment_executions(db: AsyncSession, exp_id: UUID4) -> None:
    await db.execute(
        delete(models.Execution).where(
            models.Execution.experiment_id == str(exp_id)
        )
    )
    await db.commit()


async def does_execution_belong_to_org(
    db: AsyncSession,
    org_id: UUID4,
    exec_id: UUID4,
) -> bool:
    result = await db.execute(
        select(models.Execution.id)
        .where(models.Execution.id == str(exec_id))
        .where(models.Execution.org_id == str(org_id))
    )
    return result.scalar() is not None


async def is_execution_linked_to_experiment(
    db: AsyncSession,
    exp_id: UUID4,
    exec_id: UUID4,
) -> bool:
    result = await db.execute(
        select(models.Execution.id)
        .where(models.Execution.id == str(exec_id))
        .where(models.Execution.experiment_id == str(exp_id))
    )
    return result.scalar() is not None


async def get_executions_summary(
    db: AsyncSession, org_id: UUID4, exp_id: UUID4
) -> List[Dict[str, Any]]:
    results = await db.execute(
        select(
            DictBundle(
                "x",
                models.Execution.id.label("id"),
                models.Execution.result["deviated"].label("deviated"),
                models.Execution.result["status"].label("status"),
                models.Execution.result["start"].label("start"),
                models.Execution.result["end"].label("end"),
            )
        )
        .where(models.Execution.org_id == str(org_id))
        .where(models.Execution.experiment_id == str(exp_id))
        .order_by(asc(models.Execution.created_date))
    )
    return results.scalars().all()


async def set_user_state(
    db: AsyncSession,
    org_id: UUID4,
    exec_id: UUID4,
    state: Dict[str, Any],
) -> None:
    q = (
        update(models.Execution)
        .where(models.Execution.id == str(exec_id))
        .where(models.Execution.org_id == str(org_id))
        .values(user_state=state)
    )

    await db.execute(q)
    await db.commit()


async def get_user_state(
    db: AsyncSession, org_id: UUID4, exec_id: UUID4
) -> Dict[str, str]:
    q = (
        select(models.Execution.user_state)
        .where(models.Execution.id == str(exec_id))
        .where(models.Execution.org_id == str(org_id))
    )

    result = await db.execute(q)
    return result.scalars().first()  # type: ignore


async def compute_metrics(
    db: AsyncSession, org_id: UUID4
) -> Dict[str, int | Dict[str, Any]]:
    per_day = await count_executions_per_day(db, org_id)
    per_month = await count_executions_month(db, org_id)
    per_week = await count_executions_week(db, org_id)
    per_user_total = await count_executions_per_user(db, org_id)

    per_user_this_week = await executions_per_user_this_week(db, org_id)

    impact_per_plan = await impact_per_plan_dist(db, org_id)
    impact_per_tag = await impact_per_tag_dist(db, org_id)

    exp_scores = await get_experiment_scores(db, org_id)
    plan_scores = await get_plan_scores(db, org_id)

    running_count = await get_running_count(db, org_id)

    contrib_per_experiment = await get_contributions_per_experiment(db, org_id)
    contrib_per_executions = await get_contributions_per_execution(db, org_id)

    return {
        "per_period": {
            "per_day": per_day,
            "per_week": per_week,
            "per_month": per_month,
        },
        "per_user": {
            "total": per_user_total,
            "current_week": per_user_this_week,
        },
        "impacts": {"per_plan": impact_per_plan, "per_tag": impact_per_tag},
        "scores": {"per_experiment": exp_scores, "per_plan": plan_scores},
        "running_count": running_count,
        "contributions": {
            "per_experiment": contrib_per_experiment,
            "per_execution": contrib_per_executions,
        },
    }


async def count_executions_per_user(
    db: AsyncSession, org_id: UUID4
) -> List[Dict[str, str | int]]:
    from reliably_app import account

    q = (
        select(
            models.Execution.user_id,
            account.models.User.username.label("username"),
            func.count(func.distinct(models.Execution.id)).label("count"),
        )
        .where(models.Execution.org_id == str(org_id))
        .where(models.Execution.user_id.is_not(None))
        .join(
            account.models.User,
            account.models.User.id == models.Execution.user_id,
        )
        .group_by(models.Execution.user_id, account.models.User.id)
    )

    result = await db.execute(q)
    return [
        {"user_id": r[0], "username": r[1], "count": r[2]} for r in result.all()
    ]


async def executions_per_user_this_week(
    db: AsyncSession,
    org_id: UUID4,
) -> List[Dict[str, UUID4 | str | datetime | bool | float]]:
    from reliably_app import account, plan

    today = date.today()
    start_of_week = today - timedelta(days=6)

    q = (
        select(
            account.models.User.id.label("user_id"),
            account.models.User.username.label("username"),
            models.Execution.id.label("execution_id"),
            models.Execution.created_date.label("started_on"),
            models.Execution.result["status"].label("status"),
            models.Execution.result["deviated"].label("deviated"),
            plan.models.Plan.definition["title"].label("plan_title"),
            plan.models.Plan.id.label("plan_id"),
            models.Execution.experiment_id.label("experiment_id"),
            models.Execution.result["duration"].label("duration"),
        )
        .where(models.Execution.org_id == str(org_id))
        .where(models.Execution.user_id.is_not(None))
        .where(models.Execution.created_date >= start_of_week)
        .join(plan.models.Plan, plan.models.Plan.id == models.Execution.plan_id)
        .join(
            account.models.User,
            account.models.User.id == models.Execution.user_id,
        )
    )

    result = await db.execute(q)
    return [
        {
            "user_id": r[0],
            "username": r[1],
            "execution_id": r[2],
            "started_on": r[3],
            "status": r[4],
            "deviated": r[5],
            "plan_title": r[6],
            "plan_id": r[7],
            "experiment_id": r[8],
            "duration": r[9],
        }
        for r in result.all()
    ]


async def count_executions_per_day(
    db: AsyncSession, org_id: UUID4
) -> List[Dict[str, datetime | int]]:
    q = (
        select(
            func.date_trunc("day", models.Execution.created_date).label("day"),
            func.count(func.distinct(models.Execution.id)).label("count"),
        )
        .where(models.Execution.org_id == str(org_id))
        .where(models.Execution.user_id.is_not(None))
        .group_by("day")
    )

    result = await db.execute(q)
    return [{"day": r[0], "count": r[1]} for r in result.all()]


async def count_executions_month(
    db: AsyncSession, org_id: UUID4
) -> List[Dict[str, datetime | int]]:
    q = (
        select(
            func.date_trunc("month", models.Execution.created_date).label(
                "month"
            ),
            func.count(func.distinct(models.Execution.id)).label("count"),
        )
        .where(models.Execution.org_id == str(org_id))
        .where(models.Execution.user_id.is_not(None))
        .group_by("month")
    )

    result = await db.execute(q)
    return [{"month": r[0], "count": r[1]} for r in result.all()]


async def count_executions_week(
    db: AsyncSession, org_id: UUID4
) -> List[Dict[str, datetime | int]]:
    q = (
        select(
            func.date_trunc("week", models.Execution.created_date).label(
                "week"
            ),
            func.count(func.distinct(models.Execution.id)).label("count"),
        )
        .where(models.Execution.org_id == str(org_id))
        .where(models.Execution.user_id.is_not(None))
        .group_by("week")
    )

    result = await db.execute(q)
    return [{"week": r[0], "count": r[1]} for r in result.all()]


async def impact_per_plan_dist(
    db: AsyncSession,
    org_id: UUID4,
) -> List[Dict[str, Any]]:
    from reliably_app import plan

    today = date.today()
    start_of_week = today - timedelta(days=6)

    q = (
        select(
            plan.models.Plan.id.label("plan_id"),
            plan.models.Plan.definition["title"].label("plan_title"),
            func.count(func.distinct(models.Execution.id)).label("count"),
            func.sum(
                case(
                    (
                        models.Execution.result["deviated"].astext == "true",
                        literal_column("1"),
                    ),
                    else_=literal_column("0"),
                )
            ).label("deviated"),
            func.sum(
                case(
                    (
                        models.Execution.result["status"].astext == "completed",
                        literal_column("1"),
                    ),
                    else_=literal_column("0"),
                )
            ).label("completed"),
        )
        .where(models.Execution.org_id == str(org_id))
        .where(models.Execution.user_id.is_not(None))
        .where(models.Execution.created_date >= start_of_week)
        .join(plan.models.Plan, plan.models.Plan.id == models.Execution.plan_id)
        .group_by(plan.models.Plan.id, "plan_title")
    )

    result = await db.execute(q)
    return [
        {
            "plan_id": r[0],
            "plan_title": r[1],
            "total": r[2],
            "deviated": r[3],
            "completed": r[4],
        }
        for r in result.all()
    ]


async def impact_per_tag_dist(
    db: AsyncSession,
    org_id: UUID4,
) -> List[Dict[str, Any]]:
    today = date.today()
    start_of_week = today - timedelta(days=6)

    q = (
        select(
            func.distinct(
                func.jsonb_array_elements_text(
                    text(
                        f"{models.Execution.__tablename__}.result #> '{{experiment,tags}}'"  # noqa
                    )
                )
            ).label("tags"),
            func.count(func.distinct(models.Execution.id)).label("count"),
            func.sum(
                case(
                    (
                        models.Execution.result["deviated"].astext == "true",
                        literal_column("1"),
                    ),
                    else_=literal_column("0"),
                )
            ).label("deviated"),
            func.sum(
                case(
                    (
                        models.Execution.result["status"].astext == "completed",
                        literal_column("1"),
                    ),
                    else_=literal_column("0"),
                )
            ).label("completed"),
        )
        .where(models.Execution.org_id == str(org_id))
        .where(models.Execution.user_id.is_not(None))
        .where(models.Execution.created_date >= start_of_week)
        .group_by("tags")
    )

    result = await db.execute(q)
    return [
        {
            "tag": r[0],
            "total": r[1],
            "deviated": r[2],
            "completed": r[3],
        }
        for r in result.all()
    ]


async def get_experiment_scores(
    db: AsyncSession,
    org_id: UUID4,
) -> List[Dict[str, Any]]:
    from reliably_app import experiment

    sub = (
        select(
            models.Execution.id,
            models.Execution.org_id,
            models.Execution.experiment_id,
            models.Execution.created_date,
            models.Execution.result["status"].astext.label("status"),
            models.Execution.result["deviated"]
            .astext.cast(Boolean)
            .label("deviated"),
            func.row_number()
            .over(
                partition_by=models.Execution.experiment_id,
                order_by=desc(models.Execution.created_date),
            )
            .label("rownum"),
        )
        .where(models.Execution.org_id == str(org_id))
        .subquery()
    )

    q = (
        select(
            sub.c.experiment_id,
            func.count(func.distinct(sub.c.id)).label("count"),
            experiment.models.Experiment.definition["title"].astext.label(
                "title"
            ),
            case(
                (
                    func.date_part(
                        "day",
                        func.current_timestamp()
                        - (func.array_agg(sub.c.created_date))[1],
                    )
                    == 0,
                    literal_column("100"),
                ),
                (
                    func.date_part(
                        "day",
                        func.current_timestamp()
                        - (func.array_agg(sub.c.created_date))[1],
                    )
                    > 28,
                    literal_column("0"),
                ),
                else_=func.round(
                    0.14656
                    * func.date_part(
                        "day",
                        func.current_timestamp()
                        - (func.array_agg(sub.c.created_date))[1],
                    )
                    * func.date_part(
                        "day",
                        func.current_timestamp()
                        - (func.array_agg(sub.c.created_date))[1],
                    )
                    - 7.7048
                    * func.date_part(
                        "day",
                        func.current_timestamp()
                        - (func.array_agg(sub.c.created_date))[1],
                    )
                    + 103.79
                ),
            ).label("freshness"),
            func.round(
                func.avg(
                    case(
                        (
                            sub.c.deviated,
                            literal_column("0"),
                        ),
                        (
                            sub.c.status == "failed",
                            literal_column("0.5"),
                        ),
                        (
                            sub.c.status == "completed",
                            literal_column("1.0"),
                        ),
                        (
                            sub.c.status == "aborted",
                            literal_column("0"),
                        ),
                        else_=literal_column("0"),
                    )
                ),
                2,
            ).label("score"),
        )
        .select_from(sub)
        .join(
            experiment.models.Experiment,
            experiment.models.Experiment.id == sub.c.experiment_id,
        )
        .where(sub.c.org_id == str(org_id))
        .where(sub.c.rownum <= 10)
        .group_by(
            sub.c.experiment_id,
            "title",
        )
    )

    result = await db.execute(q)
    return [
        {
            "experiment_id": r[0],
            "execution_count": r[1],
            "experiment_title": r[2],
            "freshness": r[3],
            "score": r[4],
        }
        for r in result.all()
    ]


async def get_plan_scores(
    db: AsyncSession,
    org_id: UUID4,
) -> List[Dict[str, Any]]:
    from reliably_app import plan

    sub = (
        select(
            models.Execution.id,
            models.Execution.org_id,
            models.Execution.plan_id,
            models.Execution.created_date,
            models.Execution.result["status"].astext.label("status"),
            models.Execution.result["deviated"]
            .astext.cast(Boolean)
            .label("deviated"),
            func.row_number()
            .over(
                partition_by=models.Execution.experiment_id,
                order_by=desc(models.Execution.created_date),
            )
            .label("rownum"),
        )
        .where(models.Execution.org_id == str(org_id))
        .subquery()
    )

    q = (
        select(
            sub.c.plan_id,
            func.count(func.distinct(sub.c.id)).label("count"),
            plan.models.Plan.definition["title"].astext.label("title"),
            case(
                (
                    func.date_part(
                        "day",
                        func.current_timestamp()
                        - (func.array_agg(sub.c.created_date))[1],
                    )
                    == 0,
                    literal_column("100"),
                ),
                (
                    func.date_part(
                        "day",
                        func.current_timestamp()
                        - (func.array_agg(sub.c.created_date))[1],
                    )
                    > 28,
                    literal_column("0"),
                ),
                else_=func.round(
                    0.14656
                    * func.date_part(
                        "day",
                        func.current_timestamp()
                        - (func.array_agg(sub.c.created_date))[1],
                    )
                    * func.date_part(
                        "day",
                        func.current_timestamp()
                        - (func.array_agg(sub.c.created_date))[1],
                    )
                    - 7.7048
                    * func.date_part(
                        "day",
                        func.current_timestamp()
                        - (func.array_agg(sub.c.created_date))[1],
                    )
                    + 103.79
                ),
            ).label("freshness"),
            func.round(
                func.avg(
                    case(
                        (
                            sub.c.deviated,
                            literal_column("0"),
                        ),
                        (
                            sub.c.status == "failed",
                            literal_column("0.5"),
                        ),
                        (
                            sub.c.status == "completed",
                            literal_column("1.0"),
                        ),
                        (
                            sub.c.status == "aborted",
                            literal_column("0"),
                        ),
                        else_=literal_column("0"),
                    )
                ),
                2,
            ).label("score"),
        )
        .select_from(sub)
        .join(plan.models.Plan, plan.models.Plan.id == sub.c.plan_id)
        .where(sub.c.org_id == str(org_id))
        .where(sub.c.rownum <= 10)
        .where(sub.c.plan_id.is_not(None))
        .group_by(sub.c.plan_id, "title")
    )

    result = await db.execute(q)
    return [
        {
            "plan_id": r[0],
            "execution_count": r[1],
            "plan_title": r[2],
            "freshness": r[3],
            "score": r[4],
        }
        for r in result.all()
    ]


async def get_running_count(db: AsyncSession, org_id: UUID4) -> int:
    q = (
        select(
            func.count(func.distinct(models.Execution.id)).label("count"),
        )
        .where(models.Execution.org_id == str(org_id))
        .where(models.Execution.user_id.is_not(None))
        .where(models.Execution.user_state["current"].astext == "running")
    )

    result = await db.execute(q)
    return result.scalar_one_or_none() or 0


async def get_contributions_per_experiment(
    db: AsyncSession, org_id: UUID4
) -> List[Dict[str, Any]]:
    from reliably_app import experiment

    sub = (
        select(
            experiment.models.Experiment.org_id,
            func.jsonb_object_keys(
                experiment.models.Experiment.definition["contributions"]
            ).label("contrib"),
        )
        .where(experiment.models.Experiment.org_id == str(org_id))
        .subquery()
    )

    q = (
        select(
            sub.c.contrib,
            func.count(sub.c.contrib).label("count"),
        )
        .select_from(sub)
        .where(sub.c.org_id == str(org_id))
        .group_by("contrib")
    )

    result = await db.execute(q)
    return [
        {
            "name": r[0],
            "count": r[1],
        }
        for r in result.all()
    ]


async def get_contributions_per_execution(
    db: AsyncSession, org_id: UUID4
) -> List[Dict[str, Any]]:
    sub = (
        select(
            models.Execution.id.label("execution_id"),
            models.Execution.org_id,
            func.jsonb_object_keys(
                models.Execution.result["experiment"]["contributions"]
            ).label("contrib"),
        )
        .where(models.Execution.org_id == str(org_id))
        .subquery()
    )

    q = (
        select(
            sub.c.contrib,
            func.count(sub.c.contrib).label("count"),
        )
        .select_from(sub)
        .where(sub.c.org_id == str(org_id))
        .group_by("contrib")
    )

    result = await db.execute(q)
    return [
        {
            "name": r[0],
            "count": r[1],
        }
        for r in result.all()
    ]
