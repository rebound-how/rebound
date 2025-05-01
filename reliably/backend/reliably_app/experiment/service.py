import sys
from typing import Any, Dict, List, cast

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import execution, organization, plan, series
from reliably_app.database import SessionLocal
from reliably_app.dependencies.database import get_db
from reliably_app.dependencies.org import valid_org
from reliably_app.experiment import crud, models, schemas, validators
from reliably_app.observability import span

__all__ = ["extend_routers"]

router = APIRouter()


def extend_routers(web: APIRouter, api: APIRouter) -> None:
    web.include_router(router, prefix="/experiments", include_in_schema=False)
    api.include_router(router, prefix="/experiments")


@router.get(
    "",
    response_model=schemas.Experiments,
    status_code=status.HTTP_200_OK,
    description="Retrieve all organization's experiments",
    tags=["Experiment"],
    summary="Retrieve all organization's experiments",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Experiments,
            "description": "Ok Response",
        }
    },
)
async def index(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, int | List[models.Experiment]]:
    count = await crud.count_experiments(db, org.id)  # type: ignore

    if not count:
        return {"count": 0, "items": []}

    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    if (limit * page) > count:
        return {"count": count, "items": []}

    experiments = await crud.get_experiments(
        db,
        org.id,  # type: ignore
        page=limit * page,
        limit=limit,
    )

    return {"count": count, "items": experiments}


@router.post(
    "",
    response_model=schemas.Experiment,
    status_code=status.HTTP_201_CREATED,
    description="Add a new experiment",
    tags=["Experiment"],
    summary="Add a new experiment",
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.Experiment,
            "description": "Created",
        },
        status.HTTP_409_CONFLICT: {
            "model": str,
            "description": "Name already used",
        },
    },
)
async def create(
    exp: schemas.ExperimentCreate,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Experiment:
    x = await crud.create_experiment(db, org.id, exp)  # type: ignore

    async with SessionLocal() as d:
        await organization.crud.update_experiments_count(
            d,
            org.id,  # type: ignore
        )

    await series.crud.experiment.initialize_experiment_series(
        org.id,  # type: ignore
        x.id,  # type: ignore
        exp.definition,
    )

    await series.crud.experiment.consume_experiment(
        org.id,  # type: ignore
        exp.definition,
    )

    await series.crud.org.consume_experiment(
        org.id,  # type: ignore
        exp.definition,
    )

    return x


@router.get(
    "/all",
    response_model=schemas.ExperimentsBasic,
    status_code=status.HTTP_200_OK,
    description="All experiments at once",
    tags=["Experiment"],
    summary="All experiments at once",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ExperimentsBasic,
            "description": "Ok Response",
        },
    },
)
async def all_experiments(
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, int | List[Dict[str, str]]]:
    result = await crud.get_all_experiments(db, org.id)  # type: ignore

    return {"count": len(result), "items": result}


@router.get(
    "/summary",
    response_model=schemas.ExperimentsSummary,
    status_code=status.HTTP_200_OK,
    description="Experiments with their last execution results",
    tags=["Experiment"],
    summary="Experiments with their last execution results",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ExperimentsSummary,
            "description": "Ok Response",
        },
    },
)
async def summary_experiments(
    pattern: str | None = Query(None, min_length=1),
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, int | List[Dict[str, str]]]:
    count = int(org.experiments_count)

    if not count:
        return {"count": 0, "items": []}

    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    if (limit * page) > count:
        return {"count": count, "items": []}

    if pattern:
        count = await crud.count_experiments_summary_by_title(
            db,
            org.id,  # type: ignore
            pattern,
        )
        experiments = await crud.search_experiments_summary_by_title(
            db,
            org.id,  # type: ignore
            pattern,
            page=limit * page,
            limit=limit,
        )
    else:
        experiments = await crud.get_experiments_summary(
            db,
            org.id,  # type: ignore
            page=limit * page,
            limit=limit,
        )
    return {"count": count, "items": experiments}


@router.post(
    "/import",
    response_model=schemas.Experiment,
    status_code=status.HTTP_201_CREATED,
    description="Import an experiment",
    tags=["Experiment"],
    summary="Import an experiment",
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.Experiment,
            "description": "Ok Response",
        },
    },
)
async def import_experiment(
    experiment: schemas.ExperimentImport = Body(),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Experiment:
    x = schemas.ExperimentCreate(definition=experiment.experiment)
    xp = await crud.create_experiment(db, org.id, x)  # type: ignore

    await series.crud.experiment.initialize_experiment_series(
        org.id,  # type: ignore
        xp.id,  # type: ignore
        experiment.experiment,
    )

    await series.crud.experiment.consume_experiment(
        org.id,  # type: ignore
        experiment.experiment,
    )

    await series.crud.org.consume_experiment(
        org.id,  # type: ignore
        experiment.experiment,
    )

    async with SessionLocal() as d:
        await organization.crud.update_experiments_count(
            d,
            org.id,  # type: ignore
        )

    return xp


@router.get(
    "/search",
    response_model=schemas.Experiments,
    status_code=status.HTTP_200_OK,
    description="Search experiment by title",
    tags=["Experiment"],
    summary="Search experiment by title",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Experiments,
            "description": "Ok Response",
        },
    },
)
async def search_experiments_by_title(
    pattern: str = Query(min_length=1),
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, int | List[models.Experiment]]:
    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    experiments = await crud.search_experiments_by_title(
        db,
        org.id,  # type: ignore
        pattern,
        page=limit * page,
        limit=limit,
    )

    return {"count": len(experiments), "items": experiments}


@router.get(
    "/{exp_id}",
    response_model=schemas.Experiment,
    status_code=status.HTTP_200_OK,
    description="Retrieve an experiment in an organinzation",
    tags=["Experiment"],
    summary="Retrieve an experiment",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Experiment,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Experiment was not found",
        },
    },
)
async def get(
    exp_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Experiment:
    if not await crud.does_experiment_belong_to_org(
        db,
        org.id,  # type: ignore
        exp_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    exp = await crud.get_experiment(db, exp_id)
    if not exp:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return exp


@router.put(
    "/{exp_id}",
    response_model=schemas.Experiment,
    status_code=status.HTTP_200_OK,
    description="Replace an experiment in an organinzation",
    tags=["Experiment"],
    summary="Replace an experiment",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Experiment,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Experiment was not found",
        },
    },
)
async def replace(
    exp_id: UUID4,
    new_exp: schemas.ExperimentEdit,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Experiment:
    if not await crud.does_experiment_belong_to_org(
        db,
        org.id,  # type: ignore
        exp_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    exp = await crud.get_experiment(db, exp_id)
    if not exp:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await crud.replace_experiment(db, exp, new_exp)

    return exp


@router.delete(
    "/{exp_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Delete the given experiment",
    tags=["Experiment"],
    summary="Delete the given experiment",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
    },
)
async def delete(
    experiment: schemas.Experiment = Depends(validators.valid_experiment),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse | None:
    exp_id = experiment.id

    if await plan.crud.is_experiment_used_by_any_plans(
        db,
        org.id,  # type: ignore
        exp_id,
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "title": "experiment is used by at least one plan",
                "status": status.HTTP_400_BAD_REQUEST,
                "detail": "cannot delete this experiment has it is used "
                "by at least one plan or its plan is still being deleted",
            },
        )

    attrs = {"org_id": str(org.id), "exp_id": str(experiment.id)}

    execs = await execution.crud.get_executions_summary(
        db,
        org.id,  # type: ignore
        experiment.id,
    )

    # delete executions
    with span("delete-experiment-executions", attributes=attrs):
        async with SessionLocal() as session:
            await execution.crud.delete_experiment_executions(session, exp_id)

    # delete experiment itself
    with span("delete-experiment", attributes=attrs):
        await crud.delete_experiment(db, exp_id)

    # delete series
    with span("delete-experiment-series", attributes=attrs):
        for x in execs:
            await series.crud.org.drop_execution(
                org.id,  # type: ignore
                experiment.id,
                None,
                x,
            )

        await series.crud.experiment.delete_experiment_series(
            org.id,  # type: ignore
            exp_id,
        )

        await series.crud.org.drop_experiment(
            org.id,  # type: ignore
            exp_id,
            experiment.definition,
        )

    # update org stats
    with span("delete-org-stats", attributes=attrs):
        async with SessionLocal() as d:
            await organization.crud.update_counts(d, org.id)  # type: ignore

    return None


@router.get(
    "/{exp_id}/raw",
    name="get_raw_experiment",
    response_model=schemas.ChaosToolkitExperiment,
    status_code=status.HTTP_200_OK,
    description="Retrieve the raw Chaos Toolkit experiment",
    tags=["Experiment"],
    summary="Retrieve the raw Chaos Toolkit experiment",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ChaosToolkitExperiment,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Experiment was not found",
        },
    },
)
async def get_raw(
    exp_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    if not await crud.does_experiment_belong_to_org(
        db,
        org.id,  # type: ignore
        exp_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    exp = await crud.get_experiment(db, exp_id)
    if not exp:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return cast(Dict, exp.definition)


@router.get(
    "/{exp_id}/plans",
    response_model=schemas.ExperimentIds,
    status_code=status.HTTP_200_OK,
    description="Retrieve all plans using an experiment",
    tags=["Experiment", "Plan"],
    summary="Retrieve the experiment's plans",
    responses={
        status.HTTP_200_OK: {
            "content": {"application/json": {}},
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Experiment was not found",
        },
    },
)
async def get_plans(
    exp_id: UUID4,
    pattern: str | None = Query(None, min_length=1),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> List[UUID4]:
    if pattern:
        return await plan.crud.search_plan_ids_by_title(
            db,
            org.id,  # type: ignore
            pattern,
            experiment_id=exp_id,
        )
    else:
        return await plan.crud.get_plans_using_experiment(
            db,
            org.id,  # type: ignore
            exp_id,
        )
