import logging
import sys
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import (
    account,
    environment,
    experiment,
    integration,
    organization,
    plan,
)
from reliably_app.assistant import crud, models, schemas, tasks, validators
from reliably_app.database import SessionLocal
from reliably_app.dependencies.auth import with_user_in_org
from reliably_app.dependencies.database import get_db
from reliably_app.dependencies.org import valid_org
from reliably_app.observability import span

__all__ = ["extend_routers"]

logger = logging.getLogger("reliably_app")
router = APIRouter()


def extend_routers(web: APIRouter, api: APIRouter) -> None:
    web.include_router(router, prefix="/assistant", include_in_schema=False)
    api.include_router(router, prefix="/assistant")


@router.post(
    "/scenario",
    response_model=schemas.Scenario,
    status_code=status.HTTP_200_OK,
    description="Generate a new scenario",
    tags=["Assistant"],
    summary="Generate a new scenario",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Scenario,
            "description": "OK",
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "model": str,
            "description": "Not allowed in your plan",
        },
    },
)
async def scenario_new(
    query: schemas.ScenarioQuery,
    user: account.models.User = Depends(with_user_in_org),
    org: organization.models.Organization = Depends(
        organization.validators.valid_org
    ),
    db: AsyncSession = Depends(get_db),
) -> models.AssistantScenario | None:
    api_key: str | None = None

    with span("new-scenario"):
        with span("lookup-openai-key-from-integration"):
            async with SessionLocal() as s:
                intg = await integration.crud.get_integration(
                    s, query.integration_id
                )

                if not intg:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
                    )

                env = await environment.crud.get_environment(
                    s,
                    intg.environment_id,  # type: ignore
                )

                if not env:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
                    )

                e = environment.schemas.Environment.model_validate(env)
                for sec in e.secrets:
                    if sec.key == "openai-key":
                        api_key = sec.value.get_secret_value()
                        break

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        scenario = await crud.store_scenario(
            db,
            org.id,  # type: ignore
            user.id,  # type: ignore
            query,
        )

        tasks.scenario.generate_scenario(
            scenario.id,  # type: ignore
            api_key,
            query.question,
            query.tags,
        )

        return scenario


@router.get(
    "/scenario/{scenario_id}",
    name="get_scenario",
    response_model=schemas.Scenario,
    status_code=status.HTTP_200_OK,
    description="Retrieve a scenario from an organization",
    tags=["Assistant"],
    summary="Retrieve a scenario from an organization",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Scenario,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Scenario was not found",
        },
    },
)
async def get(
    scenario: models.AssistantScenario = Depends(validators.valid_scenario),
) -> models.AssistantScenario:
    return scenario


@router.get(
    "/scenario",
    response_model=schemas.Scenarios,
    status_code=status.HTTP_200_OK,
    description="Retrieve all organization's assistant scenarios",
    tags=["Assistant"],
    summary="Retrieve all organization's assistant scenarios",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Scenarios,
            "description": "Ok Response",
        }
    },
)
async def index(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, int | List[models.AssistantScenario]]:
    count = await crud.count_scenarios(db, org.id)  # type: ignore

    if not count:
        return {"count": 0, "items": []}

    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    if (limit * page) > count:
        return {"count": count, "items": []}

    scenarios = await crud.get_scenarios(
        db,
        org.id,  # type: ignore
        page=limit * page,
        limit=limit,
    )
    return {"count": count, "items": scenarios}


@router.delete(
    "/scenario/{scenario_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Delete the given scenario",
    tags=["Assistant"],
    summary="Delete the given scenario",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
    },
)
async def delete(
    scenario_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    if not await crud.does_scenario_belong_to_org(
        db,
        org.id,  # type: ignore
        scenario_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await crud.delete_scenario(db, scenario_id)


@router.get(
    "/scenario/by/experiment/{experiment_id}",
    response_model=schemas.ScenarioLight | None,
    status_code=status.HTTP_200_OK,
    description="Get a scenario by experiment",
    tags=["Assistant"],
    summary="Get a scenario by experiment",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ScenarioLight | None,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Scenario was not found",
        },
    },
)
async def get_by_experiment_id(
    experiment_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.AssistantScenario | None:
    if not await experiment.crud.does_experiment_belong_to_org(
        db,
        org.id,  # type: ignore
        experiment_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return await crud.get_scenario_by_experiment(
        db,
        org.id,  # type: ignore
        experiment_id,
    )


@router.put(
    "/scenario/{scenario_id}/experiment/{experiment_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Set experiment id of the scenario",
    tags=["Assistant"],
    summary="Set experiment id of the scenario",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Scenario was not found",
        },
    },
)
async def set_experiment_id(
    scenario_id: UUID4,
    experiment_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    if not await crud.does_scenario_belong_to_org(
        db,
        org.id,  # type: ignore
        scenario_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if not await experiment.crud.does_experiment_belong_to_org(
        db,
        org.id,  # type: ignore
        experiment_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await crud.set_experiment_id(db, scenario_id, experiment_id)


@router.put(
    "/scenario/{scenario_id}/plan/{plan_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Set plan id of the scenario",
    tags=["Assistant"],
    summary="Set plan id of the scenario",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Scenario was not found",
        },
    },
)
async def set_plan_id(
    scenario_id: UUID4,
    plan_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    if not await crud.does_scenario_belong_to_org(
        db,
        org.id,  # type: ignore
        scenario_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if not await plan.crud.does_plan_belong_to_org(
        db,
        org.id,  # type: ignore
        plan_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await crud.set_plan_id(db, scenario_id, plan_id)


@router.post(
    "/scenario/{scenario_id}/experiment",
    response_model=schemas.ScenarioExperiment,
    status_code=status.HTTP_200_OK,
    description="Create an experiment from a scenario",
    tags=["Assistant"],
    summary="Create an experiment from a scenario",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ScenarioExperiment,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Scenario was not found",
        },
    },
)
async def add_experiment_from_scenario(
    scenario_id: UUID4,
    context: schemas.ScenarioExperimentCreate,
    user: account.models.User = Depends(with_user_in_org),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    if not await crud.does_scenario_belong_to_org(
        db,
        org.id,  # type: ignore
        scenario_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    x = await tasks.experiment.create_experiment_from_scenario(
        str(user.id), context
    )

    x_db = await experiment.crud.create_experiment(
        db,
        org.id,  # type: ignore
        experiment.schemas.ExperimentCreate(definition=x, template_id=None),
    )

    return {"experiment_id": str(x_db.id)}
