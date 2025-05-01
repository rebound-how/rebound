import logging
import sys
from typing import Dict, List, Literal

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from reliably_app import account, agent, execution, organization
from reliably_app.dependencies.auth import with_user_in_org
from reliably_app.dependencies.database import get_db
from reliably_app.dependencies.org import valid_org
from reliably_app.observability import span
from reliably_app.plan import crud, models, schemas, validators
from reliably_app.plan.providers import (
    delete_plan,
    resume_plan,
    schedule_plan,
    suspend_plan,
)

__all__ = ["extend_routers"]

logger = logging.getLogger("reliably_app")
router = APIRouter()
shedulable_router = APIRouter()


def extend_routers(web: APIRouter, api: APIRouter) -> None:
    web.include_router(router, prefix="/plans", include_in_schema=False)
    api.include_router(router, prefix="/plans")

    web.include_router(
        shedulable_router, prefix="/plans/schedulables", include_in_schema=False
    )
    api.include_router(shedulable_router, prefix="/plans/schedulables")


@router.get(
    "",
    response_model=schemas.Plans,
    status_code=status.HTTP_200_OK,
    description="Retrieve all organization's plans",
    tags=["Plan"],
    summary="Retrieve all organization's plans",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Plans,
            "description": "Ok Response",
        }
    },
)
async def index(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    sort: Literal["creation", "title", "next", "last"] | None = None,
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, int | List[models.Plan]]:
    count = await crud.count_plans(db, org.id)  # type: ignore

    if not count:
        return {"count": 0, "items": []}

    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    if (limit * page) > count:
        return {"count": count, "items": []}

    plans = await crud.get_plans(
        db,
        org.id,  # type: ignore
        page=limit * page,
        limit=limit,
        sort=sort,
    )

    return {"count": count, "items": plans}


@router.post(
    "",
    response_model=schemas.Plan,
    status_code=status.HTTP_201_CREATED,
    description="Add a new plan",
    tags=["Plan"],
    summary="Add a new plan",
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.Plan,
            "description": "Created",
        },
        status.HTTP_409_CONFLICT: {
            "model": str,
            "description": "Name already used",
        },
    },
)
async def create(
    request: Request,
    plan: schemas.PlanCreate,
    background_tasks: BackgroundTasks,
    user: account.models.User = Depends(with_user_in_org),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Plan:
    attrs = {
        "org_id": str(org.id),
        "user_id": str(user.id),
    }
    with span("create-plan", attributes=attrs):
        p = await crud.create_plan(db, org.id, plan)  # type: ignore
        background_tasks.add_task(
            schedule_plan,
            schemas.Plan.model_validate(p, from_attributes=True),
            org_id=str(org.id),
            user_id=str(user.id),
            request=request,
        )
        return p


@router.get(
    "/search",
    response_model=schemas.Plans,
    status_code=status.HTTP_200_OK,
    description="Search plan by title",
    tags=["Plan"],
    summary="Search plan by title",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Plans,
            "description": "Ok Response",
        },
    },
)
async def search_plans_by_title(
    pattern: str = Query(min_length=1),
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, int | List[models.Plan]]:
    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    count = await crud.count_plans_by_title(db, org.id, pattern)  # type: ignore
    plans = await crud.search_plans_by_title(
        db,
        org.id,  # type: ignore
        pattern,
        page=limit * page,
        limit=limit,
    )

    return {"count": count, "items": plans}


@router.get(
    "/{plan_id}",
    response_model=schemas.Plan,
    status_code=status.HTTP_200_OK,
    description="Retrieve an plan in an organinzation",
    tags=["Plan"],
    summary="Retrieve an plan",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Plan,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Plan was not found",
        },
    },
)
async def get(
    plan: models.Plan = Depends(validators.valid_plan),
) -> models.Plan:
    return plan


@router.delete(
    "/{plan_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Delete the given plan",
    tags=["Plan"],
    summary="Delete the given plan",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
    },
)
async def delete(
    background_tasks: BackgroundTasks,
    plan: models.Plan = Depends(validators.valid_plan),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    with span("delete-plan", attributes={"plan_id": str(plan.id)}):
        await crud.set_status(
            db,
            plan.id,  # type: ignore
            schemas.PlanStatus.deleting,
        )
        background_tasks.add_task(
            delete_plan,
            schemas.Plan.model_validate(plan, from_attributes=True),
            org_id=str(org.id),
        )


@router.put(
    "/{plan_id}/status",
    response_model=schemas.PlanStatusResponse,
    status_code=status.HTTP_200_OK,
    description="Set the status of the plan",
    tags=["Plan"],
    summary="Set the status of the plan",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.PlanStatusResponse,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Plan was not found",
        },
    },
)
async def set_status(
    status: schemas.PlanNewStatus,
    request: Request,
    plan: models.Plan = Depends(validators.valid_plan),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, bool]:
    attrs = {
        "plan_id": str(plan.id),
        "status": status.status.value,
        "error": status.error or "",
    }
    logger.debug(f"Received {attrs}")
    with span("set-plan-status", attributes=attrs):
        await crud.set_status(
            db,
            plan.id,  # type: ignore
            status.status,
            status.error,
        )
    return {"ok": True}


@shedulable_router.get(
    "/next",
    response_model=schemas.Plan | None,
    status_code=status.HTTP_200_OK,
    description="Get the next schedulable plan by an agent",
    tags=["Plan", "Agent"],
    summary="Get the next schedulable plan by an agent",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Plan | None,
            "description": "Ok Response",
        },
    },
)
async def get_next_schedulable(
    deployment_type: Literal["noop", "github"] = Query(),
    user: account.models.User = Depends(with_user_in_org),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Plan | None:
    agt = await agent.crud.get_agent_from_user(
        db,
        org.id,  # type: ignore
        user.id,  # type: ignore
    )
    if not agt:  # noqa
        raise HTTPException(status.HTTP_404_NOT_FOUND)  # pragma: nocover

    return await crud.get_next_schedulable_plan(
        db,
        org.id,  # type: ignore
        agt.id,  # type: ignore
        deployment_type,
    )


@router.post(
    "/{plan_id}/run",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Run a plan again in an organinzation",
    tags=["Plan"],
    summary="Run a plan again",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Plan was not found",
        },
    },
)
async def rerun(
    request: Request,
    background_tasks: BackgroundTasks,
    plan: models.Plan = Depends(validators.valid_plan),
    user: account.models.User = Depends(with_user_in_org),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    if plan.definition["schedule"]["type"] == "cron":
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    attrs = {
        "org_id": str(org.id),
        "plan_id": str(plan.id),
        "user_id": str(user.id),
    }
    with span("run-plan", attributes=attrs):
        background_tasks.add_task(
            schedule_plan,
            schemas.Plan.model_validate(plan, from_attributes=True),
            org_id=str(org.id),
            user_id=str(user.id),
            request=request,
        )


@router.post(
    "/{plan_id}/suspend",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Suspend a plan again in an organinzation",
    tags=["Plan"],
    summary="Suspend a plan again",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Plan was not found",
        },
    },
)
async def suspend(
    background_tasks: BackgroundTasks,
    plan: models.Plan = Depends(validators.valid_plan),
    user: account.models.User = Depends(with_user_in_org),
    org: organization.models.Organization = Depends(valid_org),
) -> None:
    if plan.definition["schedule"]["type"] != "cron":
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    attrs = {
        "org_id": str(org.id),
        "plan_id": str(plan.id),
        "user_id": str(user.id),
    }
    with span("suspend-plan", attributes=attrs):
        background_tasks.add_task(
            suspend_plan,
            schemas.Plan.model_validate(plan, from_attributes=True),
            str(org.id),
            str(user.id),
        )


@router.post(
    "/{plan_id}/resume",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Resume a plan again in an organinzation",
    tags=["Plan"],
    summary="Resume a plan again",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Plan was not found",
        },
    },
)
async def resume(
    background_tasks: BackgroundTasks,
    plan: models.Plan = Depends(validators.valid_plan),
    user: account.models.User = Depends(with_user_in_org),
    org: organization.models.Organization = Depends(valid_org),
) -> None:
    if plan.definition["schedule"]["type"] != "cron":
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    attrs = {
        "org_id": str(org.id),
        "plan_id": str(plan.id),
        "user_id": str(user.id),
    }
    with span("suspend-plan", attributes=attrs):
        background_tasks.add_task(
            resume_plan,
            schemas.Plan.model_validate(plan, from_attributes=True),
            str(org.id),
            str(user.id),
        )


@router.get(
    "/{plan_id}/executions",
    response_model=execution.schemas.Executions,
    status_code=status.HTTP_200_OK,
    description="Get plan executions",
    tags=["Plan"],
    summary="Get plan executions",
    responses={
        status.HTTP_200_OK: {
            "model": execution.schemas.Executions,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Plan was not found",
        },
    },
)
async def get_executions(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    db: AsyncSession = Depends(get_db),
    plan: models.Plan = Depends(validators.valid_plan),
) -> Dict[str, int | List[execution.models.Execution]]:
    count = int(plan.executions_count or 0)

    if not count:
        return {"count": 0, "items": []}

    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    if (limit * page) > count:
        return {"count": count, "items": []}

    executions = await execution.crud.get_executions_by_plan(
        db,
        plan.id,  # type: ignore
        page=limit * page,
        limit=limit,
    )

    return {"count": count, "items": executions}


@router.put(
    "/{plan_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Update a plan",
    tags=["Plan"],
    summary="Add a new plan",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Updated",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Plan was not found",
        },
    },
)
async def update(
    new_plan: schemas.PlanUpdate,
    plan: models.Plan = Depends(validators.valid_plan),
    user: account.models.User = Depends(with_user_in_org),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    attrs = {
        "org_id": str(org.id),
        "user_id": str(user.id),
    }
    with span("update-plan", attributes=attrs):
        if plan.definition["experiments"] != [
            str(i) for i in new_plan.experiments
        ]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        await crud.update_plan(db, org.id, plan, new_plan)  # type: ignore
