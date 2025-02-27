from typing import List, cast

from authlib.oidc.core import UserInfo
from pydantic import UUID4
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app.account import errors, models, schemas

__all__ = [
    "create_user",
    "get_user",
    "get_users",
    "get_user_by_openid",
    "count_users",
]


async def create_user(
    db: AsyncSession, user: schemas.UserCreate
) -> models.User:
    db_user = models.User(
        email=user.email,
        username=user.username,
        openid_profile=user.openid,
        as_agent=user.as_agent,
    )
    try:
        db.add(db_user)
        await db.commit()
    except IntegrityError:
        raise errors.UserAlreadyExistError()

    return cast(models.User, db_user)


async def get_user(db: AsyncSession, user_id: UUID4) -> models.User | None:
    return cast(models.User, await db.get(models.User, str(user_id)))


async def get_users(
    db: AsyncSession, page: int = 0, limit: int = 10
) -> List[models.User]:
    results = await db.execute(
        select(models.User)
        .where(models.User.as_agent == False)  # noqa
        .offset(page)
        .limit(limit)
    )
    return results.scalars().all()


async def count_users(db: AsyncSession) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.User.id)).where(
                    models.User.as_agent == False  # noqa
                )
            )
        ).scalar_one(),
    )


async def get_user_by_openid(
    db: AsyncSession, openid_info: UserInfo
) -> models.User | None:
    results = await db.execute(
        select(models.User).where(
            models.User.openid_profile["sub"].astext == openid_info.sub
        )
    )

    return results.scalar()


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> models.User | None:
    results = await db.execute(
        select(models.User).where(models.User.email == email)
    )

    return results.scalar()


async def get_user_by_email_and_password(
    db: AsyncSession,
    email: str,
    password: bytes,
) -> models.User | None:
    results = await db.execute(
        select(models.User)
        .where(models.User.email == email)
        .where(models.User.password == password)
    )

    return results.scalar()


async def reset_password(db: AsyncSession, email: str, password: str) -> None:
    await db.execute(
        update(models.User)
        .where(models.User.email == email)
        .values(password=password)
    )

    await db.commit()
