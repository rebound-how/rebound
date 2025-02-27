from typing import List, cast

from pydantic import UUID4
from sqlalchemy import asc, delete, desc, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app.integration import errors, models, schemas

__all__ = [
    "does_integration_belong_to_org",
    "create_integration",
    "get_integration",
    "get_integrations",
    "delete_integration",
    "count_integrations",
    "set_integration_name",
]


async def create_integration(
    db: AsyncSession,
    org_id: UUID4,
    intg: schemas.IntegrationCreate,
    env_id: UUID4,
) -> models.Integration:
    db_env = models.Integration(
        name=intg.name,
        org_id=org_id,
        environment_id=env_id,
        provider=intg.provider,
        vendor=intg.vendor,
    )
    try:
        db.add(db_env)
        await db.commit()
    except IntegrityError:
        raise errors.IntegrationAlreadyExistsError()

    return cast(models.Integration, db_env)


async def count_integrations(db: AsyncSession, org_id: UUID4) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.Integration.id)).where(
                    models.Integration.org_id == str(org_id)
                )
            )
        ).scalar_one(),
    )


async def get_integration(
    db: AsyncSession, env_id: UUID4
) -> models.Integration | None:
    return cast(
        models.Integration, await db.get(models.Integration, str(env_id))
    )


async def get_many_integrations(
    db: AsyncSession, org_id: UUID4, integration_ids: List[UUID4]
) -> List[models.Integration]:
    results = await db.execute(
        select(models.Integration)
        .where(models.Integration.org_id == str(org_id))
        .where(models.Integration.id.in_([str(id) for id in integration_ids]))
    )
    return results.scalars().all()


async def get_integrations(
    db: AsyncSession, org_id: UUID4, page: int = 0, limit: int = 10
) -> List[models.Integration]:
    results = await db.execute(
        select(models.Integration)
        .where(models.Integration.org_id == str(org_id))
        .order_by(asc(models.Integration.name))
        .offset(page)
        .limit(limit)
    )
    return results.scalars().all()


async def delete_integration(db: AsyncSession, env_id: UUID4) -> None:
    await db.execute(
        delete(models.Integration).where(models.Integration.id == str(env_id))
    )
    await db.commit()


async def does_integration_belong_to_org(
    db: AsyncSession,
    org_id: UUID4,
    env_id: UUID4,
) -> bool:
    result = await db.execute(
        select(models.Integration.id)
        .where(models.Integration.id == str(env_id))
        .where(models.Integration.org_id == str(org_id))
    )
    return result.scalar() is not None


async def set_integration_name(
    db: AsyncSession, org_id: UUID4, integration_id: UUID4, name: str
) -> None:
    await db.execute(
        update(models.Integration)
        .where(models.Integration.id == str(integration_id))
        .where(models.Integration.org_id == str(org_id))
        .values(name=name)
    )
    await db.commit()


async def get_integrations_by_provider_and_vendor(
    db: AsyncSession, org_id: UUID4, vendor: str, provider: str
) -> List[models.Integration]:
    results = await db.execute(
        select(models.Integration)
        .where(models.Integration.org_id == str(org_id))
        .where(models.Integration.vendor == vendor)
        .where(models.Integration.provider == provider)
        .order_by(desc(models.Integration.created_date))
    )
    return results.scalars().all()
