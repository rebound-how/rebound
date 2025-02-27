import secrets
from typing import List, cast

from pydantic import UUID4
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app.token import errors, models, schemas

__all__ = [
    "create_token",
    "get_token",
    "get_tokens",
    "delete_token",
    "get_by_token_value",
    "revoke_token",
    "count_tokens",
]


async def create_token(
    db: AsyncSession, org_id: UUID4, user_id: UUID4, token: schemas.TokenCreate
) -> models.Token:
    db_token = models.Token(
        name=token.name,
        org_id=str(org_id),
        user_id=str(user_id),
        token=secrets.token_hex(16).encode("utf-8"),
    )
    try:
        db.add(db_token)
        await db.commit()
    except IntegrityError:
        raise errors.TokenNameAlreadyExistError()

    return cast(models.Token, db_token)


async def get_token(db: AsyncSession, token_id: UUID4) -> models.Token:
    return cast(models.Token, await db.get(models.Token, str(token_id)))


async def get_by_token_value(db: AsyncSession, token: bytes) -> models.Token:
    results = await db.execute(
        select(models.Token).where(models.Token.token == token)
    )

    return cast(models.Token, results.scalar())


async def get_by_token_name(db: AsyncSession, name: str) -> models.Token | None:
    results = await db.execute(
        select(models.Token).where(models.Token.name == name)
    )

    return results.scalars().first()


async def get_tokens(
    db: AsyncSession,
    org_id: UUID4,
    user_id: UUID4,
    page: int = 0,
    limit: int = 10,
) -> List[models.Token]:
    results = await db.execute(
        select(models.Token)
        .where(models.Token.org_id == str(org_id))
        .where(models.Token.user_id == str(user_id))
        .offset(page)
        .limit(limit)
    )

    return results.scalars().all()


async def delete_token(db: AsyncSession, token_id: UUID4) -> None:
    await db.execute(
        delete(models.Token).where(models.Token.id == str(token_id))
    )
    await db.commit()


async def revoke_token(db: AsyncSession, token_id: UUID4) -> None:
    await db.execute(
        update(models.Token)
        .where(models.Token.id == str(token_id))
        .values(revoked=True)
    )
    await db.commit()


async def does_token_belong_to_user(
    db: AsyncSession,
    token_id: UUID4,
    user_id: UUID4,
) -> bool:
    result = await db.execute(
        select(models.Token.id)
        .where(models.Token.id == str(token_id))
        .where(models.Token.user_id == str(user_id))
    )
    return result.scalar() is not None


async def count_tokens(db: AsyncSession, user_id: UUID4) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.Token.user_id)).where(
                    models.Token.user_id == str(user_id)
                )
            )
        ).scalar_one(),
    )
