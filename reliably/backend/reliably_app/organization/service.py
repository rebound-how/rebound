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

from reliably_app import account, agent, login
from reliably_app.database import SessionLocal
from reliably_app.dependencies.auth import with_admin_user, with_user_in_org
from reliably_app.dependencies.database import get_db
from reliably_app.organization import crud, errors, models, schemas, validators

__all__ = ["extend_routers", "top_level_router"]

top_level_router = APIRouter()
router = APIRouter()


def extend_routers(web: APIRouter, api: APIRouter) -> None:
    web.include_router(router, prefix="", include_in_schema=False)
    api.include_router(router, prefix="")


@top_level_router.post(
    "",
    response_model=schemas.Organization,
    status_code=status.HTTP_201_CREATED,
    description="Add a new organization",
    tags=["Organization"],
    summary="Add a new organization",
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.Organization,
            "description": "Created",
        },
        status.HTTP_409_CONFLICT: {
            "model": str,
            "description": "Name already used",
        },
    },
)
async def create(
    org: schemas.OrganizationCreate,
    background_tasks: BackgroundTasks,
    user: account.models.User = Depends(with_admin_user),
) -> models.Organization:
    try:
        new_org, _ = await login.tasks.new_org(
            org.name, background_tasks, owner=user
        )
    except errors.OrgAlreadyExistError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    return new_org


@top_level_router.get(
    "",
    response_model=schemas.Organizations,
    status_code=status.HTTP_200_OK,
    description="List the user's organizations",
    tags=["Organization"],
    summary="List the user's organizations",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Organizations,
            "description": "OK",
        },
    },
)
async def list_(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    user: account.models.User = Depends(with_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, int | List[models.Organization]]:
    count = await crud.count_user_organizations(db, user.id)  # type: ignore

    if not count:
        return {"count": 0, "items": []}

    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    if (limit * page) > count:
        return {"count": count, "items": []}

    orgs = await crud.get_user_orgs(
        db,
        user.id,  # type: ignore
        page=limit * page,
        limit=limit,
    )

    return {"count": count, "items": orgs}


@router.get(
    "/",
    response_model=schemas.Organization,
    status_code=status.HTTP_200_OK,
    description="Retrieve one organization by its identifier",
    tags=["Organization"],
    summary="Retrieve one organization by its identifier",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Organization,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Organization was not found",
        },
    },
)
async def get(
    org: models.Organization = Depends(validators.valid_org),
) -> models.Organization:
    return org


@router.delete(
    "/",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Mark an organization as deleted",
    tags=["Organization"],
    summary="Mark an organization as deleted",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not allowed to deleted this organization",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Organization was not found",
        },
    },
)
async def delete(
    org: models.Organization = Depends(validators.valid_org),
    user: account.models.User = Depends(with_user_in_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    if not crud.is_owner(db, org.id, user.id):  # type: ignore
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    await crud.mark_deleted(db, org.id)  # type: ignore


@router.post(
    "/try-name-candidate",
    response_model=schemas.OrganizationNameAvailable,
    status_code=status.HTTP_200_OK,
    description="Checks if the name is already taken or available",
    tags=["Organization"],
    summary="Checks if the name is already taken or available",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.OrganizationNameAvailable,
            "description": "Ok Response",
        },
    },
)
async def is_name_available(
    candidate: schemas.OrganizationNameCandidate,
    db: AsyncSession = Depends(get_db),
) -> Dict[Literal["available"], bool]:
    return {"available": await crud.is_name_available(db, candidate.name)}


@router.get(
    "/users",
    response_model=account.schemas.Users,
    status_code=status.HTTP_200_OK,
    description="Retrieve all users of the organization",
    tags=["User", "Organization"],
    summary="Retrieve organization's users",
    responses={
        status.HTTP_200_OK: {
            "model": account.schemas.Users,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Organization was not found",
        },
    },
)
async def get_users(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    org: models.Organization = Depends(validators.valid_org),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, int | List[account.models.User]]:
    count = await crud.count_users_in_org(db, org.id)  # type: ignore
    users = await crud.get_org_users(
        db,
        org.id,  # type: ignore
        page=(page or 2) - 1,
        limit=limit or 10,
    )
    return {"count": count, "items": users}


@router.post(
    "/users",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Add an user to an organization",
    tags=["User", "Organization"],
    summary="Add an user to an organization",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Organization or user was not found",
        },
    },
)
async def add_user(
    user: account.models.User = Depends(account.validators.valid_user),
    org: models.Organization = Depends(validators.valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    if not await crud.does_user_belong_to_org(
        db,
        org.id,  # type: ignore
        user.id,  # type: ignore
    ):
        try:
            await crud.add_user(db, org, user)
        finally:
            async with SessionLocal() as d:
                await crud.update_users_count(d, org.id)  # type: ignore

        async with SessionLocal() as db:
            agt = await agent.crud.get_user_internal_agent(
                db,
                org.id,  # type: ignore
                user.id,  # type: ignore
            )
            if not agt:
                await agent.crud.create_user_agent(
                    org,
                    user.id,  # type: ignore
                    True,
                )


@router.delete(
    "/users/{user_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Remove an user from an organization",
    tags=["User", "Organization"],
    summary="Remove an user from an organization",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Organization or user was not found",
        },
    },
)
async def remove_user(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    user: account.models.User = Depends(account.validators.valid_user),
    org: models.Organization = Depends(validators.valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await crud.remove_user(db, org, user)
    finally:
        async with SessionLocal() as d:
            await crud.update_users_count(d, org.id)  # type: ignore

    async with SessionLocal() as db:
        agt = await agent.crud.get_user_internal_agent(
            db,
            org.id,  # type: ignore
            user.id,  # type: ignore
        )
        if agt:
            await agent.crud.delete_agent(db, agt.id)  # type: ignore


@router.get(
    "/invite",
    response_model=schemas.OrganizationInvite,
    status_code=status.HTTP_200_OK,
    description="Create a unique invitation link to this organization",
    tags=["Invitation", "Organization"],
    summary="Create a unique invitation link to this organization",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.OrganizationInvite,
            "description": "Ok Response",
        },
    },
)
async def get_invite_link(
    org: models.Organization = Depends(validators.valid_org),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str | None]:
    invite = await crud.get_active_invitation(db, org.id)  # type: ignore
    return {"link": invite.link_hash.decode("utf-8") if invite else None}


@router.get(
    "/invite/generate",
    response_model=schemas.OrganizationInvite,
    status_code=status.HTTP_200_OK,
    description="Create a unique invitation link to this organization",
    tags=["Invitation", "Organization"],
    summary="Create a unique invitation link to this organization",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.OrganizationInvite,
            "description": "Ok Response",
        },
    },
)
async def generate_invite_link(
    org: models.Organization = Depends(validators.valid_org),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    invite = await crud.get_active_invitation(db, org.id)  # type: ignore
    if invite:
        await crud.disable_invitation(db, org.id, invite.id)  # type: ignore

    async with SessionLocal() as d:
        invite = await crud.create_invitation(d, org.id)  # type: ignore
        return {"link": invite.link_hash.decode("utf-8")}
