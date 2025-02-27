import sys
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app.account import crud, errors, models, schemas
from reliably_app.dependencies.database import get_db

__all__ = ["extend_routers"]

router = APIRouter()


def extend_routers(web: APIRouter, api: APIRouter) -> None:
    web.include_router(router, prefix="/user", include_in_schema=False)
    api.include_router(router, prefix="/user")


@router.get(
    "",
    response_model=schemas.Users,
    status_code=status.HTTP_200_OK,
    description="Retrieve all users",
    tags=["User"],
    summary="Retrieve all users",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Users,
            "description": "Ok Response",
        }
    },
)
async def index(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, int | List[models.User]]:
    count = await crud.count_users(db)
    users = await crud.get_users(db, page=page - 1, limit=limit)  # type: ignore
    return {"count": count, "items": users}


@router.get(
    "/{user_id}",
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
    description="Retrieve one user by its identifier",
    tags=["User"],
    summary="Retrieve one user by its identifier",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.User,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User was not found",
        },
    },
)
async def get(
    user_id: UUID4, db: AsyncSession = Depends(get_db)
) -> models.User:
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return user


@router.post(
    "",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    description="Add a new user user",
    tags=["User"],
    summary="Add a new user user",
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.User,
            "description": "Created",
        },
        status.HTTP_409_CONFLICT: {
            "model": str,
            "description": "Username and/or password already used",
        },
    },
)
async def create(
    user: schemas.UserCreate, db: AsyncSession = Depends(get_db)
) -> models.User:
    try:
        return await crud.create_user(db=db, user=user)
    except errors.UserAlreadyExistError:
        raise HTTPException(status.HTTP_409_CONFLICT)
