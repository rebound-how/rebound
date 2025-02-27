from fastapi import Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app.account import crud, models, schemas
from reliably_app.dependencies.database import get_db

__all__ = ["valid_user"]


async def valid_user(
    db: AsyncSession = Depends(get_db),
    user_id: UUID4 | None = None,
    user: schemas.UserIdentifier | None = None,
) -> models.User:
    user_id = user_id or user.user_id  # type: ignore
    db_user = await crud.get_user(db, user_id)

    if not db_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return db_user
