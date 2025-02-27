from typing import Any, Dict, List, cast

from pydantic import UUID4
from sqlalchemy import asc, delete, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app.database import DictBundle
from reliably_app.environment import models, schemas

__all__ = [
    "does_environment_belong_to_org",
    "create_environment",
    "get_environment",
    "get_environments",
    "delete_environment",
    "count_environments",
    "search_environments_by_title",
]


async def create_environment(
    db: AsyncSession,
    org_id: UUID4,
    env: schemas.EnvironmentCreate,
    used_for: str = "plan",
) -> models.Environment:
    d = schemas.dump_environment_in_clear(env)
    db_env = models.Environment(
        name=env.name,
        org_id=org_id,
        envvars=d["envvars"],
        secrets=d["secrets"],
        used_for=used_for,
    )
    db.add(db_env)
    await db.commit()

    return cast(models.Environment, db_env)


async def count_environments(
    db: AsyncSession, org_id: UUID4, used_for: str = "plan"
) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.Environment.id))
                .where(models.Environment.org_id == str(org_id))
                .where(models.Environment.used_for == used_for)
            )
        ).scalar_one(),
    )


async def get_environment(
    db: AsyncSession, env_id: UUID4
) -> models.Environment | None:
    return cast(
        models.Environment, await db.get(models.Environment, str(env_id))
    )


async def get_environments(
    db: AsyncSession,
    org_id: UUID4,
    page: int = 0,
    limit: int = 10,
    used_for: str = "plan",
) -> List[models.Environment]:
    results = await db.execute(
        select(models.Environment)
        .where(models.Environment.org_id == str(org_id))
        .where(models.Environment.used_for == used_for)
        .order_by(asc(models.Environment.name))
        .offset(page)
        .limit(limit)
    )
    return results.scalars().all()


async def get_environments_from_integrations(
    db: AsyncSession,
    org_id: UUID4,
    environment_ids: list[str],
    used_for: str = "plan",
) -> List[models.Environment]:
    results = await db.execute(
        select(models.Environment)
        .where(models.Environment.org_id == str(org_id))
        .where(models.Environment.used_for == used_for)
        .where(models.Environment.id.in_(environment_ids))
        .order_by(desc(models.Environment.created_date))
    )
    return results.scalars().all()


async def delete_environment(db: AsyncSession, env_id: UUID4) -> None:
    await db.execute(
        delete(models.Environment).where(models.Environment.id == str(env_id))
    )
    await db.commit()


async def does_environment_belong_to_org(
    db: AsyncSession,
    org_id: UUID4,
    env_id: UUID4,
) -> bool:
    result = await db.execute(
        select(models.Environment)
        .where(models.Environment.id == str(env_id))
        .where(models.Environment.org_id == str(org_id))
    )
    return result.scalar() is not None


async def set_environment(
    db: AsyncSession,
    env_id: UUID4,
    new_env: schemas.Environment,
) -> None:
    d = schemas.dump_environment_in_clear(new_env)

    await db.execute(
        update(models.Environment)
        .where(models.Environment.id == str(env_id))
        .values(
            envvars=d["envvars"],
            secrets=d["secrets"],
        )
    )
    await db.commit()


async def get_simple_environments(
    db: AsyncSession, org_id: UUID4
) -> List[Dict[str, Any]]:
    results = await db.execute(
        select(
            DictBundle(
                "x",
                models.Environment.id.label("id"),
                models.Environment.name.label("name"),
            )
        )
        .where(models.Environment.org_id == str(org_id))
        .order_by(asc(models.Environment.name))
    )
    return results.scalars().all()


async def search_environments_by_title(
    db: AsyncSession, org_id: UUID4, term: str, page: int = 0, limit: int = 10
) -> List[models.Environment]:
    result = await db.execute(
        select(models.Environment)
        .where(models.Environment.org_id == str(org_id))
        .where(models.Environment.name.ilike(f"%{term}%"))
        .order_by(desc(models.Environment.created_date))
        .offset(page)
        .limit(limit)
    )
    return result.scalars().all()


async def count_environments_by_title(
    db: AsyncSession, org_id: UUID4, term: str
) -> int:
    result = await db.execute(
        select(func.count(models.Environment.id))
        .where(models.Environment.org_id == str(org_id))
        .where(models.Environment.name.ilike(f"%{term}%"))
    )
    return cast(int, result.scalar())
