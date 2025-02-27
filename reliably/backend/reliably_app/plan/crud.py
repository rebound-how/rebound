import secrets
from typing import List, Literal, cast

import orjson
from pydantic import UUID4
from sqlalchemy import (
    String,
    asc,
    cast as sa_cast,
    delete,
    desc,
    func,
    literal_column,
    select,
    text,
    update,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import bindparam

from reliably_app import execution
from reliably_app.database import SessionLocal
from reliably_app.plan import models, schemas

__all__ = [
    "does_plan_belong_to_org",
    "create_plan",
    "get_plan",
    "get_plan_by_ref",
    "get_plans",
    "delete_plan",
    "count_plans",
    "mark_schedulable",
    "get_next_schedulable_plan",
    "get_plans_using_deployment",
    "get_plans_using_environment",
    "is_environment_used_by_any_plan",
    "update_executions_count",
    "update_plan",
    "search_plans_by_title",
]


async def create_plan(
    db: AsyncSession, org_id: UUID4, plan: schemas.PlanCreate
) -> models.Plan:
    # pydantic doesn't deal well with nested dicts containing UUID
    plan_dict = orjson.loads(plan.model_dump_json())
    db_env = models.Plan(
        org_id=org_id,
        definition=plan_dict,
        ref=secrets.token_hex(16),
        status=schemas.PlanStatus.creating,
        last_executions_info={"running": None, "terminated": None},
    )
    db.add(db_env)
    await db.commit()

    return cast(models.Plan, db_env)


async def update_plan(
    db: AsyncSession,
    org_id: UUID4,
    plan: schemas.Plan,
    new_plan: schemas.PlanUpdate,
) -> None:
    # pydantic doesn't deal well with nested dicts containing UUID
    plan_dict = orjson.loads(new_plan.model_dump_json())

    await db.execute(
        update(models.Plan)
        .where(models.Plan.id == plan.id)
        .where(models.Plan.org_id == plan.org_id)
        .values(definition=plan_dict)
    )

    await db.commit()


async def get_plan(
    db: AsyncSession,
    plan_id: UUID4 | str,
    status: schemas.PlanStatus | None = schemas.PlanStatus.deleted,
) -> models.Plan | None:
    q = select(models.Plan).where(models.Plan.id == str(plan_id))

    if status is not None:
        q = q.where(models.Plan.status != status.value)

    q = q.limit(1)

    result = await db.execute(q)

    return result.scalars().first()


async def get_plan_by_ref(
    db: AsyncSession, org_id: UUID4, ref: str
) -> models.Plan | None:
    result = await db.execute(
        select(models.Plan)
        .where(models.Plan.org_id == str(org_id))
        .where(models.Plan.ref == str(ref))
        .where(models.Plan.status != schemas.PlanStatus.deleted.value)
        .order_by(desc(models.Plan.created_date))
    )
    return result.scalar()


async def get_plans(
    db: AsyncSession,
    org_id: UUID4,
    page: int = 0,
    limit: int = 10,
    sort: Literal["creation", "title", "next", "last"] | None = None,
) -> List[models.Plan]:
    q = (
        select(models.Plan)
        .where(models.Plan.org_id == str(org_id))
        .where(models.Plan.status != schemas.PlanStatus.deleted.value)
    )

    if sort == "creation":
        q = q.order_by(desc(models.Plan.created_date))
    elif sort == "title":
        q = q.order_by(asc(models.Plan.definition["title"].astext))
    elif sort == "last":
        q = q.order_by(desc(models.Plan.last_executions_info["terminated"]))
    else:
        q = q.order_by(desc(models.Plan.created_date))

    q = q.offset(page).limit(limit)

    results = await db.execute(q)
    return results.scalars().all()


async def count_plans(db: AsyncSession, org_id: UUID4) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.Plan.id))
                .where(models.Plan.org_id == str(org_id))
                .where(models.Plan.status != schemas.PlanStatus.deleted.value)
            )
        ).scalar_one(),
    )


async def delete_plan(db: AsyncSession, plan_id: UUID4) -> None:
    await db.execute(delete(models.Plan).where(models.Plan.id == str(plan_id)))
    await db.commit()


async def does_plan_belong_to_org(
    db: AsyncSession,
    org_id: UUID4,
    plan_id: UUID4,
) -> bool:
    result = await db.execute(
        select(models.Plan.id)
        .where(models.Plan.id == str(plan_id))
        .where(models.Plan.org_id == str(org_id))
    )
    return result.scalar() is not None


async def set_status(
    db: AsyncSession,
    plan_id: UUID4 | str,
    status: schemas.PlanStatus,
    error: str | None = None,
) -> None:
    q = (
        update(models.Plan)
        .where(models.Plan.id == str(plan_id))
        .values(status=status.value, error=error)
    )

    await db.execute(q)
    await db.commit()


async def mark_schedulable(
    db: AsyncSession,
    org_id: str | UUID4,
    plan_id: str | UUID4,
    deployment_type: str,
) -> None:
    sched = models.Schedulable(
        org_id=str(org_id),
        plan_id=str(plan_id),
        deployment_type=deployment_type,
    )
    db.add(sched)
    await db.commit()


async def get_next_schedulable_plan(
    db: AsyncSession, org_id: UUID4, agent_id: UUID4, deployment_type: str
) -> models.Plan | None:
    async with SessionLocal() as session:
        results = await session.execute(
            select(models.Schedulable)
            .where(models.Schedulable.org_id == str(org_id))
            .where(models.Schedulable.deployment_type == deployment_type)
            .where(models.Schedulable.agent_id == None)  # noqa
            .order_by(asc(models.Schedulable.created_date))
            .limit(1)
            .with_for_update()
        )
        sched = results.scalars().first()
        if not sched:
            return None

        sched_plan_id = sched.plan_id
        await session.execute(
            update(models.Schedulable)
            .where(models.Schedulable.org_id == str(org_id))
            .where(models.Schedulable.id == sched.id)
            .values(agent_id=str(agent_id))
        )

        await session.commit()

    return await get_plan(db, sched_plan_id)


async def get_schedulable_plan(
    db: AsyncSession,
    sched_id: UUID4 | str,
) -> models.Schedulable | None:
    async with SessionLocal() as session:
        results = await session.execute(
            select(models.Schedulable).where(
                models.Schedulable.id == str(sched_id)
            )
        )
        return results.scalars().first()


async def get_plans_using_deployment(
    db: AsyncSession, org_id: UUID4, dep_id: UUID4
) -> List[UUID4]:
    result = await db.execute(
        select(models.Plan.id)
        .where(models.Plan.org_id == str(org_id))
        .where(models.Plan.status != schemas.PlanStatus.deleted.value)
        .where(
            models.Plan.definition["deployment"]["deployment_id"].astext
            == str(dep_id)
        )
        .order_by(desc(models.Plan.created_date))
    )
    return result.scalars().all()


async def is_deployment_used_by_any_plan(
    db: AsyncSession, org_id: UUID4, dep_id: UUID4
) -> bool:
    result = await db.execute(
        select(models.Plan.id)
        .where(models.Plan.org_id == str(org_id))
        .where(models.Plan.status != schemas.PlanStatus.deleted.value)
        .where(
            models.Plan.definition["deployment"]["deployment_id"].astext
            == str(dep_id)
        )
        .limit(1)
    )
    return result.scalars().first() is not None


async def get_plans_using_experiment(
    db: AsyncSession, org_id: UUID4, exp_id: UUID4
) -> List[UUID4]:
    result = await db.execute(
        select(models.Plan.id)
        .where(models.Plan.org_id == str(org_id))
        .where(models.Plan.status != schemas.PlanStatus.deleted.value)
        .where(models.Plan.definition.contains({"experiments": [str(exp_id)]}))
        .order_by(desc(models.Plan.created_date))
    )
    return result.scalars().all()


async def is_experiment_used_by_any_plans(
    db: AsyncSession, org_id: UUID4, exp_id: UUID4
) -> bool:
    result = await db.execute(
        select(models.Plan.id)
        .where(models.Plan.org_id == str(org_id))
        .where(models.Plan.status != schemas.PlanStatus.deleted.value)
        .where(models.Plan.definition.contains({"experiments": [str(exp_id)]}))
        .limit(1)
    )
    return result.scalars().first() is not None


async def get_plans_using_environment(
    db: AsyncSession, org_id: UUID4, dep_id: UUID4
) -> List[UUID4]:
    result = await db.execute(
        select(models.Plan.id)
        .where(models.Plan.org_id == str(org_id))
        .where(models.Plan.status != schemas.PlanStatus.deleted.value)
        .where(
            models.Plan.definition["environment"]["id"].astext == str(dep_id)
        )
        .order_by(desc(models.Plan.created_date))
    )
    return result.scalars().all()


async def is_environment_used_by_any_plan(
    db: AsyncSession, org_id: UUID4, env_id: UUID4
) -> bool:
    result = await db.execute(
        select(models.Plan.id)
        .where(models.Plan.org_id == str(org_id))
        .where(models.Plan.status != schemas.PlanStatus.deleted.value)
        .where(
            models.Plan.definition["environment"]["id"].astext == str(env_id)
        )
        .limit(1)
    )
    return result.scalars().first() is not None


async def update_executions_count(
    db: AsyncSession, org_id: UUID4, plan_id: UUID4
) -> None:
    await db.execute(
        update(models.Plan)
        .where(models.Plan.id == str(plan_id))
        .where(models.Plan.org_id == str(org_id))
        .values(
            executions_count=select(func.count(execution.models.Execution.id))
            .where(execution.models.Execution.org_id == str(org_id))
            .where(execution.models.Execution.plan_id == str(plan_id))
            .scalar_subquery()
        )
    )
    await db.commit()


async def update_last_completed_execution_info(
    db: AsyncSession,
    org_id: UUID4,
    plan_id: UUID4,
    execution_id: UUID4,
    timestamp: str,
) -> None:
    await db.execute(
        update(models.Plan)
        .where(models.Plan.id == str(plan_id))
        .where(models.Plan.org_id == str(org_id))
        .values(
            last_executions_info=select(
                func.jsonb_set(
                    sa_cast(models.Plan.last_executions_info, JSONB),
                    literal_column("'{terminated}'"),
                    sa_cast(  # type: ignore
                        {
                            "id": str(execution_id),  # noqa
                            "timestamp": timestamp,  # noqa
                        },
                        JSONB,
                    ),
                )
            )
            .where(models.Plan.id == str(plan_id))
            .where(models.Plan.org_id == str(org_id))
            .scalar_subquery()
        )
    )

    await db.commit()


async def update_last_running_execution_info(
    db: AsyncSession,
    org_id: UUID4,
    plan_id: UUID4,
    execution_id: UUID4,
    timestamp: str,
) -> None:
    await db.execute(
        update(models.Plan)
        .where(models.Plan.id == str(plan_id))
        .where(models.Plan.org_id == str(org_id))
        .values(
            last_executions_info=select(
                func.jsonb_set(
                    sa_cast(models.Plan.last_executions_info, JSONB),
                    literal_column("'{running}'"),
                    sa_cast(  # type: ignore
                        {
                            "id": str(execution_id),  # noqa
                            "timestamp": timestamp,  # noqa
                        },
                        JSONB,
                    ),
                )
            )
            .where(models.Plan.id == str(plan_id))
            .where(models.Plan.org_id == str(org_id))
            .scalar_subquery()
        )
    )

    await db.commit()


async def get_plans_using_integration(
    db: AsyncSession, org_id: UUID4, integration_id: UUID4
) -> List[UUID4]:
    result = await db.execute(
        select(models.Plan.id)
        .where(models.Plan.org_id == str(org_id))
        .where(models.Plan.status != schemas.PlanStatus.deleted.value)
        .where(
            models.Plan.definition["integrations"].comparator.contains(
                [str(integration_id)]
            )
        )
        .order_by(desc(models.Plan.created_date))
    )
    return result.scalars().all()


async def is_integration_used_by_any_plan(
    db: AsyncSession, org_id: UUID4, integration_id: UUID4
) -> bool:
    result = await db.execute(
        select(models.Plan.id)
        .where(models.Plan.org_id == str(org_id))
        .where(models.Plan.status != schemas.PlanStatus.deleted.value)
        .where(
            models.Plan.definition["integrations"].comparator.contains(
                [str(integration_id)]
            )
        )
        .limit(1)
    )
    return result.scalars().first() is not None


async def search_plans_by_title(
    db: AsyncSession, org_id: UUID4, term: str, page: int = 0, limit: int = 10
) -> List[models.Plan]:
    result = await db.execute(
        select(models.Plan)
        .where(models.Plan.org_id == str(org_id))
        .where(models.Plan.status != schemas.PlanStatus.deleted.value)
        .where(
            text(
                f"COALESCE({models.Plan.__tablename__}.definition ->> 'title', '') ilike :search_text"  # noqa
            ).bindparams(bindparam("search_text", f"%{term}%", String))
        )
        .order_by(desc(models.Plan.created_date))
        .offset(page)
        .limit(limit)
    )
    return result.scalars().all()


async def count_plans_by_title(
    db: AsyncSession, org_id: UUID4, term: str
) -> int:
    result = await db.execute(
        select(func.count(models.Plan.id))
        .where(models.Plan.org_id == str(org_id))
        .where(
            text(
                f"COALESCE({models.Plan.__tablename__}.definition ->> 'title', '') ilike :search_text"  # noqa
            ).bindparams(bindparam("search_text", f"%{term}%", String))
        )
    )
    return cast(int, result.scalar())


async def search_plan_ids_by_title(
    db: AsyncSession,
    org_id: UUID4,
    term: str,
    experiment_id: UUID4 | None = None,
) -> List[UUID4]:
    result = await db.execute(
        select(models.Plan.id)
        .where(models.Plan.org_id == str(org_id))
        .where(models.Plan.status != schemas.PlanStatus.deleted.value)
        .where(
            models.Plan.id.in_(
                select(execution.models.Execution.plan_id)
                .where(execution.models.Execution.org_id == str(org_id))
                .where(
                    execution.models.Execution.experiment_id
                    == str(experiment_id)
                )
                .scalar_subquery()
            )
        )
        .where(
            text(
                f"COALESCE({models.Plan.__tablename__}.definition ->> 'title', '') ilike :search_text"  # noqa
            ).bindparams(bindparam("search_text", f"%{term}%", String))
        )
        .order_by(desc(models.Plan.created_date))
    )
    return result.scalars().all()
