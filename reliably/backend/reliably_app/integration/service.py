import logging
import sys
from typing import Any, Dict, List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import JSONResponse
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import environment, organization, plan
from reliably_app.database import SessionLocal
from reliably_app.dependencies.database import get_db
from reliably_app.dependencies.org import valid_org
from reliably_app.integration import (
    crud,
    errors,
    models,
    schemas,
    tasks,
    validators,
)

__all__ = ["extend_routers"]

logger = logging.getLogger("reliably_app")
router = APIRouter()


def extend_routers(web: APIRouter, api: APIRouter) -> None:
    web.include_router(router, prefix="/integrations", include_in_schema=False)
    api.include_router(router, prefix="/integrations")


@router.get(
    "",
    response_model=schemas.Integrations,
    status_code=status.HTTP_200_OK,
    description="Retrieve all organization's integrations",
    tags=["Integration"],
    summary="Retrieve all organization's integrations",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Integrations,
            "description": "Ok Response",
        }
    },
)
async def index(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, int | List[models.Integration]]:
    count = await crud.count_integrations(db, org.id)  # type: ignore

    if not count:
        return {"count": 0, "items": []}

    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    if (limit * page) > count:
        return {"count": count, "items": []}

    integrations = await crud.get_integrations(
        db,
        org.id,  # type: ignore
        page=limit * page,
        limit=limit,
    )

    return {"count": count, "items": integrations}


@router.post(
    "",
    response_model=schemas.Integration,
    status_code=status.HTTP_201_CREATED,
    description="Add a new integration",
    tags=["Integration"],
    summary="Add a new integration",
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.Integration,
            "description": "Created",
        },
        status.HTTP_409_CONFLICT: {
            "model": str,
            "description": "Name already used",
        },
    },
)
async def create(
    intg: schemas.IntegrationCreate,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Integration:
    try:
        async with SessionLocal() as s:
            env = await environment.crud.create_environment(
                s,
                org.id,  # type: ignore
                intg.environment,
                intg.environment.used_for or "integration",
            )

        integ = await crud.create_integration(
            db,
            org.id,  # type: ignore
            intg,
            env.id,  # type: ignore
        )

        itg = schemas.IntegrationFull(
            id=integ.id,
            org_id=org.id,
            name=integ.name,
            provider=integ.provider,
            environment=environment.schemas.Environment.model_validate(
                env, from_attributes=True
            ),
        )
        await tasks.store_integration_secrets(itg)

        return integ

    except errors.IntegrationSecretCreationError as x:
        logger.error(
            f"Failed to create integration '{x.integration_id}' "
            f"secret: {x.message}"
        )
        async with SessionLocal() as s:
            await environment.crud.delete_environment(s, env.id)  # type: ignore

        async with SessionLocal() as s:
            await crud.delete_integration(s, integ.id)  # type: ignore

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except errors.IntegrationAlreadyExistsError:
        async with SessionLocal() as s:
            await environment.crud.delete_environment(s, env.id)  # type: ignore

        raise HTTPException(status.HTTP_409_CONFLICT)


@router.get(
    "/{integration_id}",
    response_model=schemas.Integration,
    status_code=status.HTTP_200_OK,
    description="Retrieve an integration in an organinzation",
    tags=["Integration"],
    summary="Retrieve an integration",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Integration,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Integration was not found",
        },
    },
)
async def get(
    integration_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Integration:
    if not await crud.does_integration_belong_to_org(
        db,
        org.id,  # type: ignore
        integration_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    intg = await crud.get_integration(db, integration_id)
    if not intg:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return intg


@router.get(
    "/{integration_id}/plans",
    response_model=schemas.IntegrationIds,
    status_code=status.HTTP_200_OK,
    description="Retrieve all plans using a integration",
    tags=["Integration", "Plan"],
    summary="Retrieve the integration's plans",
    responses={
        status.HTTP_200_OK: {
            "content": {"application/json": {}},
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Integration was not found",
        },
    },
)
async def get_plans(
    integration_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> List[UUID4]:
    return await plan.crud.get_plans_using_integration(
        db,
        org.id,  # type: ignore
        integration_id,
    )


@router.delete(
    "/{integration_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Delete the given integration",
    tags=["Integration"],
    summary="Delete the given integration",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "integration used by at least a plan",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "integration not found",
        },
    },
)
async def delete(
    integration_id: UUID4,
    background_tasks: BackgroundTasks,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse | None:
    if not await crud.does_integration_belong_to_org(
        db,
        org.id,  # type: ignore
        integration_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if await plan.crud.is_integration_used_by_any_plan(
        db,
        org.id,  # type: ignore
        integration_id,
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "title": "integration is used by at least another plan",
                "status": status.HTTP_400_BAD_REQUEST,
                "detail": "cannot delete this integration has it is used "
                "by at least one plan or its plan is being deleted still",
            },
        )

    intg = await crud.get_integration(db, integration_id)
    if not intg:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    try:
        await crud.delete_integration(db, integration_id)
    finally:
        full: schemas.IntegrationFull | None = None
        try:
            async with SessionLocal() as s:
                env = await environment.crud.get_environment(
                    s,
                    intg.environment_id,  # type: ignore
                )
                if env:
                    e = environment.schemas.Environment.model_validate(
                        env, from_attributes=True
                    )
                    full = schemas.IntegrationFull(
                        id=intg.id,
                        org_id=org.id,
                        name=intg.name,
                        provider=intg.provider,
                        environment=e,
                    )
                    await environment.crud.delete_environment(s, e.id)
        finally:
            if full is not None:
                background_tasks.add_task(
                    tasks.delete_integration_secrets, full
                )

    return None


@router.get(
    "/{integration_id}/control",
    response_model=schemas.IntegrationControl,
    response_model_exclude_unset=True,
    status_code=status.HTTP_200_OK,
    description="Retrieve the control representation of an integration",
    tags=["Integration"],
    summary="Retrieve the control representation of an integration",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.IntegrationControl,
            "description": "Ok Response",
        }
    },
)
async def get_control(
    integration: models.Integration = Depends(validators.valid_integration),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any] | None:
    intg = schemas.Integration.model_validate(integration, from_attributes=True)
    env = await environment.crud.get_environment(db, intg.environment_id)
    e = environment.schemas.Environment.model_validate(
        env, from_attributes=True
    )
    return tasks.get_control_from_integration(intg, e)
