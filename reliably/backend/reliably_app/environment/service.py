import sys
from typing import Annotated, Dict, List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import organization, plan
from reliably_app.database import SessionLocal
from reliably_app.dependencies.database import get_db
from reliably_app.dependencies.org import valid_org
from reliably_app.environment import crud, errors, models, schemas, tasks

__all__ = ["extend_routers"]

router = APIRouter()


def extend_routers(web: APIRouter, api: APIRouter) -> None:
    web.include_router(router, prefix="/environments", include_in_schema=False)
    api.include_router(router, prefix="/environments")


@router.get(
    "",
    response_model=schemas.Environments,
    status_code=status.HTTP_200_OK,
    description="Retrieve all organization's environments",
    tags=["Environment"],
    summary="Retrieve all organization's environments",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Environments,
            "description": "Ok Response",
        }
    },
)
async def index(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, int | List[models.Environment]]:
    count = await crud.count_environments(db, org.id)  # type: ignore

    if not count:
        return {"count": 0, "items": []}

    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    if (limit * page) > count:
        return {"count": count, "items": []}

    environments = await crud.get_environments(
        db,
        org.id,  # type: ignore
        page=limit * page,
        limit=limit,
    )

    return {"count": count, "items": environments}


@router.get(
    "/simple",
    response_model=schemas.SimpleEnvironments,
    status_code=status.HTTP_200_OK,
    description="Retrieve a simplified version of an environment",
    tags=["Environment"],
    summary="Retrieve a simplified version of an organization's environments",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.SimpleEnvironments,
            "description": "Ok Response",
        }
    },
)
async def simple(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> List[Dict[str, str]]:
    return await crud.get_simple_environments(db, org.id)  # type: ignore


@router.post(
    "",
    response_model=schemas.Environment,
    status_code=status.HTTP_201_CREATED,
    description="Add a new environment",
    tags=["Environment"],
    summary="Add a new environment",
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.Environment,
            "description": "Created",
        },
        status.HTTP_409_CONFLICT: {
            "model": str,
            "description": "Name already used",
        },
    },
)
async def create(
    env: schemas.EnvironmentCreate,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Environment:
    e = await crud.create_environment(
        db,
        org.id,  # type: ignore
        env,
        used_for=env.used_for,  # type: ignore
    )

    try:
        await tasks.store_environment_secrets(
            schemas.Environment.model_validate(e, from_attributes=True)
        )
    except errors.EnvironmentSecretCreationError:
        async with SessionLocal() as s:
            await crud.delete_environment(s, e.id)  # type: ignore
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return e


@router.get(
    "/search",
    response_model=schemas.Environments,
    status_code=status.HTTP_200_OK,
    description="Search environments by name",
    tags=["Environment"],
    summary="Search environments by name",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Environments,
            "description": "Ok Response",
        },
    },
)
async def search_environments_by_title(
    pattern: str = Query(min_length=1),
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, int | List[models.Environment]]:
    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    count = await crud.count_environments_by_title(
        db,
        org.id,  # type: ignore
        pattern,
    )
    envs = await crud.search_environments_by_title(
        db,
        org.id,  # type: ignore
        pattern,
        page=limit * page,
        limit=limit,
    )

    return {"count": count, "items": envs}


@router.get(
    "/{env_id}",
    response_model=schemas.Environment,
    status_code=status.HTTP_200_OK,
    description="Retrieve an environment in an organinzation",
    tags=["Environment"],
    summary="Retrieve an environment",
    responses={
        status.HTTP_200_OK: {
            "content": {"application/json": {}},
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Environment was not found",
        },
    },
)
async def get(
    env_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    if not await crud.does_environment_belong_to_org(
        db,
        org.id,  # type: ignore
        env_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    env = await crud.get_environment(db, env_id)
    if not env:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return JSONResponse(
        jsonable_encoder(
            schemas.Environment.model_validate(env, from_attributes=True)
        )
    )


@router.get(
    "/{env_id}/clear",
    response_model=schemas.Environment,
    status_code=status.HTTP_200_OK,
    description="Retrieve an environment with cleared secrets",
    tags=["Environment"],
    summary="Retrieve an environment with cleared secrets",
    responses={
        status.HTTP_200_OK: {
            "content": {"application/json": {}},
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Environment was not found",
        },
    },
)
async def get_clear(
    env_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    if not await crud.does_environment_belong_to_org(
        db,
        org.id,  # type: ignore
        env_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    env = await crud.get_environment(db, env_id)
    if not env:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return JSONResponse(
        jsonable_encoder(
            schemas.dump_environment_in_clear(
                schemas.EnvironmentClear.model_validate(
                    env, from_attributes=True
                )
            )
        )
    )


@router.get(
    "/{env_id}/plans",
    response_model=schemas.PlanIds,
    status_code=status.HTTP_200_OK,
    description="Retrieve all plans using a environment",
    tags=["Environment", "Plan"],
    summary="Retrieve the environment's plans",
    responses={
        status.HTTP_200_OK: {
            "content": {"application/json": {}},
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Environment was not found",
        },
    },
)
async def get_plans(
    env_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> List[UUID4]:
    return await plan.crud.get_plans_using_environment(
        db,
        org.id,  # type: ignore
        env_id,
    )


@router.delete(
    "/{env_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Delete the given environment",
    tags=["Environment"],
    summary="Delete the given environment",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "environment used by at least a plan",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "environment not found",
        },
    },
)
async def delete(
    env_id: UUID4,
    background_tasks: BackgroundTasks,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse | None:
    if not await crud.does_environment_belong_to_org(
        db,
        org.id,  # type: ignore
        env_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if await plan.crud.is_environment_used_by_any_plan(
        db,
        org.id,  # type: ignore
        env_id,
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "title": "environment is used by at least another plan",
                "status": status.HTTP_400_BAD_REQUEST,
                "detail": "cannot delete this environment has it is used "
                "by at least one plan or its plan is being deleted still",
            },
        )

    env = await crud.get_environment(db, env_id)
    if not env:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    try:
        await crud.delete_environment(db, env_id)
    finally:
        background_tasks.add_task(
            tasks.delete_environment_secrets,
            schemas.Environment.model_validate(env, from_attributes=True),
        )

    return None


@router.put(
    "/{env_id}/set",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Set a new value for an environment variable",
    tags=["Environment"],
    summary="Set a new value for an environment variable",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "environment not found",
        },
    },
)
async def set_new_env_value(
    env_id: UUID4,
    target: Annotated[
        schemas.EnvironmentSecretAsFile
        | schemas.EnvironmentSecret
        | schemas.EnvironmentVar,
        Body(),
    ],
    background_tasks: BackgroundTasks,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse | None:
    if not await crud.does_environment_belong_to_org(
        db,
        org.id,  # type: ignore
        env_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    env = await crud.get_environment(db, env_id)
    if not env:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    current = schemas.Environment.model_validate(env, from_attributes=True)
    modified = False
    modified_secrets = False

    if isinstance(target, schemas.EnvironmentVar):
        for ev in current.envvars:
            if ev.var_name == target.var_name:
                ev.value = target.value
                modified = True
                break

    if not modified and not isinstance(target, schemas.EnvironmentVar):
        for sv in current.secrets:
            if sv.key == target.key:
                sv.value = target.value
                modified = True
                modified_secrets = True
                break

    # we got a new key to add into the environment
    if not modified:
        if isinstance(target, schemas.EnvironmentVar):
            current.envvars.root.append(target)
            modified = True
        else:
            current.secrets.root.append(target)
            modified = True
            modified_secrets = True

    await crud.set_environment(db, env_id, current)

    if modified_secrets:
        background_tasks.add_task(
            tasks.update_environment_secret,
            current,
            sv,
        )

    return None


@router.delete(
    "/{env_id}/remove/{key}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Remove a key for an environment variable",
    tags=["Environment"],
    summary="Remove a key for an environment variable",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "environment not found",
        },
    },
)
async def remove_env_key(
    env_id: UUID4,
    key: str,
    background_tasks: BackgroundTasks,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse | None:
    if not await crud.does_environment_belong_to_org(
        db,
        org.id,  # type: ignore
        env_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    env = await crud.get_environment(db, env_id)
    if not env:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    current = schemas.Environment.model_validate(env, from_attributes=True)
    modified = False
    modified_secrets = False

    for ev in current.envvars:
        if ev.var_name == key:
            current.envvars.root.remove(ev)
            modified = True
            break

    if not modified:
        for sv in current.secrets:
            if sv.key == key:
                current.secrets.root.remove(sv)
                modified = True
                modified_secrets = True
                break

    if modified:
        await crud.set_environment(db, env_id, current)

        if modified_secrets:
            background_tasks.add_task(
                tasks.remove_environment_secret, current, key
            )

    return None


@router.post(
    "/{env_id}/clone",
    response_model=schemas.Environment,
    status_code=status.HTTP_201_CREATED,
    description="Clone an environment",
    tags=["Environment"],
    summary="Clone an environments",
    responses={
        status.HTTP_201_CREATED: {
            "content": {"application/json": {}},
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Environment was not found",
        },
    },
)
async def clone(
    env_id: UUID4,
    name: Annotated[str, Body(min_length=1, embed=True)],
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Environment:
    if not await crud.does_environment_belong_to_org(
        db,
        org.id,  # type: ignore
        env_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    env = await crud.get_environment(db, env_id)
    if not env:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    ec = schemas.EnvironmentCreate.model_validate(
        schemas.dump_environment_in_clear(
            schemas.EnvironmentClear.model_validate(env, from_attributes=True)
        )
    )

    ec.name = name

    e = await crud.create_environment(
        db,
        org.id,  # type: ignore
        ec,
        used_for="plan",
    )

    try:
        await tasks.store_environment_secrets(
            schemas.Environment.model_validate(e, from_attributes=True)
        )
    except errors.EnvironmentSecretCreationError:
        async with SessionLocal() as s:
            await crud.delete_environment(s, e.id)  # type: ignore
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return e
