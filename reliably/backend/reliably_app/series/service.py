import sys
from typing import Any, Dict, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import execution, experiment, organization
from reliably_app.dependencies.database import get_db
from reliably_app.dependencies.org import valid_org
from reliably_app.series import crud, schemas

__all__ = ["extend_routers"]

router = APIRouter()


def extend_routers(web: APIRouter, api: APIRouter) -> None:
    web.include_router(router, prefix="/series", include_in_schema=False)
    api.include_router(router, prefix="/series")


@router.get(
    "/executions/per/experiment",
    response_model=schemas.ExecutionBreakdownSeries,
    status_code=status.HTTP_200_OK,
    description="Get experiment's executions breakdown",
    tags=["Series", "Experiment"],
    summary="Get experiment's executions breakdown",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ExecutionBreakdownSeries,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Series for experiment was not found",
        },
    },
)
async def executions_per_experiment(
    exp_id: UUID4 = Query(),
    page: int | None = Query(None, ge=1, le=sys.maxsize),
    limit: int | None = Query(None, gt=0, le=2000),
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, Any]:
    result = await crud.get_series_by_kind(
        db,
        org.id,  # type: ignore
        "exp-executions-as-series",
        exp_id=exp_id,
    )
    if not result:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return crud.transform_series(result, 0, 30)


@router.get(
    "/contributions/for/experiments",
    response_model=schemas.ExecutionBreakdownSeries,
    status_code=status.HTTP_200_OK,
    description="Get experiment's contributions breakdown",
    tags=["Series", "Experiment"],
    summary="Get experiment's contributions breakdown",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ExecutionBreakdownSeries,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Series for experiment was not found",
        },
    },
)
async def contributions_for_experiments_in_org(
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, Any]:
    result = await crud.get_series_by_kind(
        db,
        org.id,  # type: ignore
        "org-contributions-for-experiments",
    )
    if not result:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return crud.transform_contributions_series(result)


@router.get(
    "/contributions/for/executions",
    response_model=schemas.ExecutionsContributionsOrgDistribution,
    status_code=status.HTTP_200_OK,
    description="Get execution's contributions breakdown",
    tags=["Series", "Experiment"],
    summary="Get execution's contributions breakdown",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ExecutionsContributionsOrgDistribution,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Series for execution was not found",
        },
    },
)
async def contributions_for_executions_in_org(
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, Any]:
    result = await crud.get_series_by_kind(
        db,
        org.id,  # type: ignore
        "org-contributions-for-executions",
    )
    if not result:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return cast(Dict, result.data)


@router.get(
    "/executions/calendar",
    response_model=schemas.OrgExecutionCalendar,
    status_code=status.HTTP_200_OK,
    description="Get organization's calendar of all its executions",
    tags=["Series", "Experiment"],
    summary="Get organization's calendar of all its executions",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.OrgExecutionCalendar,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Series for execution was not found",
        },
    },
)
async def org_executions_calendar(
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, Dict[str, int]]:
    result = await crud.get_series_by_kind(
        db,
        org.id,  # type: ignore
        "org-executions-dist-per-day",
    )
    if not result:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return cast(Dict, result.data)


@router.get(
    "/scores/experiment/{exp_id}",
    response_model=schemas.ExperimentScoreTrend,
    status_code=status.HTTP_200_OK,
    description="Get an experiment score trend for its last executions status",
    tags=["Series", "Experiment", "Score"],
    summary="Get an experiment score trend for its last executions status",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ExperimentScoreTrend,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Experiment was not found",
        },
    },
)
async def experiment_score(
    db: AsyncSession = Depends(get_db),
    exp: experiment.schemas.Experiment = Depends(
        experiment.validators.valid_experiment
    ),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, float | None]:
    result = await crud.get_series_by_kind(
        db,
        org.id,  # type: ignore
        "exp-scores",
        exp.id,
    )
    if not result:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    data = cast(Dict, result.data) or {}
    return {
        "score": data.get("score"),
        "trend": data.get("lasts", []),
    }


@router.get(
    "/executions/metrics",
    response_model=schemas.ExecutionMetrics,
    status_code=status.HTTP_200_OK,
    description="Get executions metrics",
    tags=["Series", "Execution"],
    summary="Get executions metrics",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ExecutionMetrics,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Series for execution was not found",
        },
    },
)
async def executions_metrics(
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, Dict[str, int]]:
    result = await execution.crud.compute_metrics(
        db,
        org.id,  # type: ignore
    )

    return cast(Dict, {"distributions": result})
