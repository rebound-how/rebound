import sys
from typing import Annotated, Dict, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import organization, plan
from reliably_app.dependencies.database import get_db
from reliably_app.dependencies.org import valid_org
from reliably_app.deployment import crud, errors, models, schemas
from reliably_app.flags import bail_if_feature_not_enabled

__all__ = ["router", "extend_routers"]

router = APIRouter()


def extend_routers(web: APIRouter, api: APIRouter) -> None:
    web.include_router(router, prefix="/deployments", include_in_schema=False)
    api.include_router(router, prefix="/deployments")


@router.get(
    "",
    response_model=schemas.Deployments,
    status_code=status.HTTP_200_OK,
    description="Retrieve all organization's deployments",
    tags=["Deployment"],
    summary="Retrieve all organization's deployments",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Deployments,
            "description": "Ok Response",
        }
    },
)
async def index(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, int | List[models.Deployment]]:
    count = await crud.count_deployments(db, org.id)  # type: ignore

    if not count:
        return {"count": 0, "items": []}

    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    if (limit * page) > count:
        return {"count": count, "items": []}

    deployments = await crud.get_deployments(
        db,
        org.id,  # type: ignore
        page=limit * page,
        limit=limit,
    )

    return {"count": count, "items": deployments}


@router.post(
    "",
    response_model=schemas.Deployment,
    status_code=status.HTTP_201_CREATED,
    description="Add a new deployment",
    tags=["Deployment"],
    summary="Add a new deployment",
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.Deployment,
            "description": "Created",
        },
        status.HTTP_409_CONFLICT: {
            "model": str,
            "description": "Name already used",
        },
    },
)
async def create(
    dep: schemas.DeploymentCreate,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Deployment:
    bail_if_feature_not_enabled(
        "create-deployment", dep.definition.type, status.HTTP_400_BAD_REQUEST
    )

    try:
        return await crud.create_deployment(db, org.id, dep)  # type: ignore
    except errors.DeploymentAlreadyExistsError:
        raise HTTPException(status.HTTP_409_CONFLICT)


@router.get(
    "/search",
    response_model=schemas.Deployments,
    status_code=status.HTTP_200_OK,
    description="Search deployments by name",
    tags=["Deployment"],
    summary="Search deployments by name",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Deployments,
            "description": "Ok Response",
        },
    },
)
async def search_deployments_by_title(
    pattern: str = Query(min_length=1),
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, int | List[models.Deployment]]:
    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    count = await crud.count_deployments_by_title(
        db,
        org.id,  # type: ignore
        pattern,
    )
    deps = await crud.search_deployments_by_title(
        db,
        org.id,  # type: ignore
        pattern,
        page=limit * page,
        limit=limit,
    )

    return {"count": count, "items": deps}


@router.get(
    "/{dep_id}",
    response_model=schemas.Deployment,
    status_code=status.HTTP_200_OK,
    description="Retrieve an deployment in an organinzation",
    tags=["Deployment"],
    summary="Retrieve an deployment",
    responses={
        status.HTTP_200_OK: {
            "content": {"application/json": {}},
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Deployment was not found",
        },
    },
)
async def get(
    dep_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    if not await crud.does_deployment_belong_to_org(
        db,
        org.id,  # type: ignore
        dep_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    dep = await crud.get_deployment(db, dep_id)
    if not dep:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return JSONResponse(
        jsonable_encoder(
            schemas.Deployment.model_validate(dep, from_attributes=True)
        )
    )


@router.get(
    "/{dep_id}/plans",
    response_model=schemas.DeploymentIds,
    status_code=status.HTTP_200_OK,
    description="Retrieve all plans using a deployment",
    tags=["Deployment", "Plan"],
    summary="Retrieve the deployment's plans",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.DeploymentIds,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Deployment was not found",
        },
    },
)
async def get_plans(
    dep_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> list[UUID4]:
    return await plan.crud.get_plans_using_deployment(
        db,
        org.id,  # type: ignore
        dep_id,
    )


@router.delete(
    "/{dep_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Delete the given deployment",
    tags=["Deployment"],
    summary="Delete the given deployment",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "deployment used by at least a plan",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "deployment not found",
        },
    },
)
async def delete(
    dep_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse | None:
    if not await crud.does_deployment_belong_to_org(
        db,
        org.id,  # type: ignore
        dep_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if await plan.crud.is_deployment_used_by_any_plan(
        db,
        org.id,  # type: ignore
        dep_id,
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "title": "deployment is used by at least another plan",
                "status": status.HTTP_400_BAD_REQUEST,
                "detail": "cannot delete this deployment has it is used "
                "by at least another plan",
            },
        )

    await crud.delete_deployment(db, dep_id)

    return None


@router.put(
    "/{dep_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Set an updated deployment",
    tags=["Deployment"],
    summary="Set an updated deployment",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "deployment not found",
        },
    },
)
async def update(
    dep_id: UUID4,
    new_deployment: Annotated[schemas.DeploymentCreate, Body()],
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    if not await crud.does_deployment_belong_to_org(
        db,
        org.id,  # type: ignore
        dep_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    dep = await crud.get_deployment(db, dep_id)
    if not dep:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await crud.update_deployment(db, dep, new_deployment)

    return None


@router.post(
    "/{dep_id}/clone",
    response_model=schemas.Deployment,
    status_code=status.HTTP_201_CREATED,
    description="Clone a deployment",
    tags=["Deployment"],
    summary="Clone a deployment",
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.Deployment,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Deployment was not found",
        },
        status.HTTP_409_CONFLICT: {
            "model": str,
            "description": "Name already used",
        },
    },
)
async def clone(
    dep_id: UUID4,
    name: Annotated[str, Body(min_length=1, embed=True)],
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Deployment:
    if not await crud.does_deployment_belong_to_org(
        db,
        org.id,  # type: ignore
        dep_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    dep = await crud.get_deployment(db, dep_id)
    if not dep:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    dc = schemas.DeploymentCreate.model_validate(
        schemas.dump_to_dict(
            schemas.Deployment.model_validate(dep, from_attributes=True)
        )
    )

    dc.name = name

    try:
        d = await crud.create_deployment(
            db,
            org.id,  # type: ignore
            dc,
        )
    except errors.DeploymentAlreadyExistsError:
        raise HTTPException(status.HTTP_409_CONFLICT)

    return d
