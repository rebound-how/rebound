import sys
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import account, organization
from reliably_app.dependencies.auth import with_user_in_org
from reliably_app.dependencies.database import get_db
from reliably_app.dependencies.org import valid_org
from reliably_app.token import crud, errors, models, schemas

__all__ = ["extend_routers"]

router = APIRouter()


def extend_routers(web: APIRouter, api: APIRouter) -> None:
    web.include_router(router, prefix="/tokens", include_in_schema=False)
    api.include_router(router, prefix="/tokens")


@router.get(
    "",
    response_model=schemas.Tokens,
    status_code=status.HTTP_200_OK,
    description="Retrieve all user's tokens in a given organization",
    tags=["Token"],
    summary="Retrieve all user's tokens",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Tokens,
            "description": "Ok Response",
        }
    },
)
async def index(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
    user: account.models.User = Depends(with_user_in_org),
) -> Dict[str, int | List[models.Token]]:
    count = await crud.count_tokens(db, user.id)  # type: ignore
    tokens = await crud.get_tokens(
        db,
        org.id,  # type: ignore
        user.id,  # type: ignore
        page=(page or 2) - 1,
        limit=limit or 10,
    )
    return {"count": count, "items": tokens}


@router.post(
    "",
    response_model=schemas.Token,
    status_code=status.HTTP_201_CREATED,
    description="Create a new token",
    tags=["Token"],
    summary="Create a new token",
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.Token,
            "description": "Created",
        },
        status.HTTP_409_CONFLICT: {
            "model": str,
            "description": "Name already used",
        },
    },
)
async def create(
    token: schemas.TokenCreate,
    user: account.models.User = Depends(with_user_in_org),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Token:
    try:
        return await crud.create_token(
            db,
            org.id,  # type: ignore
            user.id,  # type: ignore
            token,
        )
    except errors.TokenNameAlreadyExistError:
        raise HTTPException(status.HTTP_409_CONFLICT)


@router.get(
    "/{token_id}",
    response_model=schemas.Token,
    status_code=status.HTTP_200_OK,
    description="Retrieve one token by its identifier",
    tags=["Token"],
    summary="Retrieve one token by its identifier",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Token,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Token was not found",
        },
    },
)
async def get(
    token_id: UUID4,
    user: account.models.User = Depends(with_user_in_org),
    db: AsyncSession = Depends(get_db),
) -> models.Token:
    if not await crud.does_token_belong_to_user(
        db,
        token_id,
        user.id,  # type: ignore
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    token = await crud.get_token(db, token_id)
    if not token:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return token


@router.delete(
    "/{token_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Delete the given token",
    tags=["Token"],
    summary="Delete the given token",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
    },
)
async def delete(
    token_id: UUID4,
    user: account.models.User = Depends(with_user_in_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    if not await crud.does_token_belong_to_user(
        db,
        token_id,
        user.id,  # type: ignore
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await crud.delete_token(db, token_id)
