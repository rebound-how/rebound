import secrets
from typing import Dict, cast

from pydantic import UUID4
from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import concat

from reliably_app.login import models

__all__ = [
    "create_auth_flow",
    "disable_auth_flow",
    "get_auth_flow",
]


async def create_auth_flow(
    db: AsyncSession, provider: str, state: Dict[str, str]
) -> models.AuthFlow:
    db_auth_flow = models.AuthFlow(
        nonce=secrets.token_hex(),
        provider=provider,
        state=state,
        active=True,
    )
    db.add(db_auth_flow)
    await db.commit()
    return cast(models.AuthFlow, db_auth_flow)


async def get_auth_flow(
    db: AsyncSession, provider: str, nonce: str
) -> models.AuthFlow | None:
    result = await db.execute(
        select(models.AuthFlow)
        .where(models.AuthFlow.provider == provider)
        .where(models.AuthFlow.nonce == nonce)
        .where(models.AuthFlow.active.is_(True))
        .where(
            func.now()
            <= (
                models.AuthFlow.created_date
                + func.cast(concat(5, " MINUTES"), INTERVAL)
            )
        )
        .with_for_update()
    )
    return result.scalars().first()


async def disable_auth_flow(
    db: AsyncSession,
    auth_flow_id: UUID4,
) -> None:
    await db.execute(
        update(models.AuthFlow)
        .where(models.AuthFlow.id == str(auth_flow_id))
        .values(active=False)
    )
    await db.commit()
