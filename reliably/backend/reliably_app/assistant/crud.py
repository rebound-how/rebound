import logging
from typing import List, cast

from pydantic import UUID4
from sqlalchemy import (
    cast as sa_cast,
    delete,
    desc,
    func,
    literal_column,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app.assistant import models, schemas

__all__ = [
    "count_scenarios",
    "delete_scenario",
    "get_scenario",
    "get_scenarios",
    "store_scenario",
    "store_scenario_experiment",
    "get_scenario_by_experiment",
]
logger = logging.getLogger("reliably_app")


async def store_scenario(
    db: AsyncSession,
    org_id: UUID4,
    user_id: UUID4,
    query: schemas.ScenarioQuery,
) -> models.AssistantScenario:
    scenario = models.AssistantScenario(
        org_id=org_id,
        user_id=user_id,
        integration_id=str(query.integration_id),
        query=query.model_dump(),
        suggestion={"items": []},
        completed=False,
        meta={"error": None},
    )
    db.add(scenario)
    await db.commit()

    return cast(models.AssistantScenario, scenario)


async def update_scenario_suggestion(
    db: AsyncSession,
    scenario_id: UUID4,
    item: schemas.ScenarioItem,
) -> None:
    # we force unsetting the default value when it's an empty string
    # to ensure the client triggers the user's input
    for p in item.parameters:
        if p.default == "":
            p.default = None

    q = (
        update(models.AssistantScenario)
        .where(models.AssistantScenario.id == str(scenario_id))
        .values(
            suggestion=func.jsonb_set(
                sa_cast(models.AssistantScenario.suggestion, JSONB),
                literal_column("'{items}'"),
                sa_cast(
                    models.AssistantScenario.suggestion["items"]
                    + sa_cast(item.model_dump(), JSONB),  # type: ignore
                    JSONB,
                ),
            )
        )
    )

    await db.execute(q)
    await db.commit()


async def mark_as_completed(
    db: AsyncSession,
    scenario_id: UUID4,
) -> None:
    q = (
        update(models.AssistantScenario)
        .where(models.AssistantScenario.id == str(scenario_id))
        .values(completed=True)
    )

    await db.execute(q)
    await db.commit()


async def store_error(
    db: AsyncSession, scenario_id: UUID4, message: str
) -> None:
    q = (
        update(models.AssistantScenario)
        .where(models.AssistantScenario.id == str(scenario_id))
        .values(
            meta=models.AssistantScenario.meta + {"error": {"message": message}}
        )
    )

    await db.execute(q)
    await db.commit()


async def set_experiment_id(
    db: AsyncSession,
    scenario_id: UUID4,
    experiment_id: UUID4,
) -> None:
    q = (
        update(models.AssistantScenario)
        .where(models.AssistantScenario.id == str(scenario_id))
        .values(experiment_id=str(experiment_id))
    )

    await db.execute(q)
    await db.commit()


async def set_plan_id(
    db: AsyncSession,
    scenario_id: UUID4,
    plan_id: UUID4,
) -> None:
    q = (
        update(models.AssistantScenario)
        .where(models.AssistantScenario.id == str(scenario_id))
        .values(plan_id=str(plan_id))
    )

    await db.execute(q)
    await db.commit()


async def store_scenario_experiment(
    db: AsyncSession,
    scenario: models.AssistantScenario,
    experiment_id: UUID4,
) -> None:
    scenario.experiment_id = experiment_id  # type: ignore
    await db.commit()


async def get_scenario(
    db: AsyncSession, scenario_id: UUID4
) -> models.AssistantScenario | None:
    return cast(
        models.AssistantScenario,
        await db.get(models.AssistantScenario, str(scenario_id)),
    )


async def count_scenarios(db: AsyncSession, org_id: UUID4) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.AssistantScenario.id)).where(
                    models.AssistantScenario.org_id == str(org_id)
                )
            )
        ).scalar_one(),
    )


async def get_scenario_by_experiment(
    db: AsyncSession, org_id: UUID4, experiment_id: UUID4
) -> models.AssistantScenario | None:
    results = await db.execute(
        select(models.AssistantScenario)
        .where(models.AssistantScenario.org_id == str(org_id))
        .where(models.AssistantScenario.experiment_id.is_not(None))
        .where(models.AssistantScenario.experiment_id == str(experiment_id))
    )
    return results.scalars().first()


async def get_scenarios(
    db: AsyncSession, org_id: UUID4, page: int = 0, limit: int = 10
) -> List[models.AssistantScenario]:
    results = await db.execute(
        select(models.AssistantScenario)
        .where(models.AssistantScenario.org_id == str(org_id))
        .order_by(desc(models.AssistantScenario.created_date))
        .offset(page)
        .limit(limit)
    )
    return results.scalars().all()


async def does_scenario_belong_to_org(
    db: AsyncSession,
    org_id: UUID4,
    scenario_id: UUID4,
) -> bool:
    result = await db.execute(
        select(models.AssistantScenario)
        .where(models.AssistantScenario.id == str(scenario_id))
        .where(models.AssistantScenario.org_id == str(org_id))
    )
    return result.scalar() is not None


async def delete_scenario(db: AsyncSession, scenario_id: UUID4) -> None:
    await db.execute(
        delete(models.AssistantScenario).where(
            models.AssistantScenario.id == str(scenario_id)
        )
    )
    await db.commit()
