from typing import List, cast

from pydantic import UUID4
from sqlalchemy import asc, delete, desc, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app.deployment import errors, models, schemas

__all__ = [
    "does_deployment_belong_to_org",
    "create_deployment",
    "get_deployment",
    "get_deployments",
    "delete_deployment",
    "count_deployments",
    "update_deployment",
]


async def create_deployment(
    db: AsyncSession, org_id: UUID4, dep: schemas.DeploymentCreate
) -> models.Deployment:
    df = schemas.dump_to_dict(dep)
    db_dep = models.Deployment(
        name=dep.name, org_id=org_id, definition=df["definition"]
    )
    try:
        db.add(db_dep)
        await db.commit()
    except IntegrityError:
        raise errors.DeploymentAlreadyExistsError()

    return cast(models.Deployment, db_dep)


async def count_deployments(db: AsyncSession, org_id: UUID4) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.Deployment.id)).where(
                    models.Deployment.org_id == str(org_id)
                )
            )
        ).scalar_one(),
    )


async def get_deployment(
    db: AsyncSession, dep_id: UUID4
) -> models.Deployment | None:
    return cast(models.Deployment, await db.get(models.Deployment, str(dep_id)))


async def get_deployments(
    db: AsyncSession, org_id: UUID4, page: int = 0, limit: int = 10
) -> List[models.Deployment]:
    results = await db.execute(
        select(models.Deployment)
        .where(models.Deployment.org_id == str(org_id))
        .order_by(asc(models.Deployment.name))
        .offset(page)
        .limit(limit)
    )
    return results.scalars().all()


async def delete_deployment(db: AsyncSession, dep_id: UUID4) -> None:
    await db.execute(
        delete(models.Deployment).where(models.Deployment.id == str(dep_id))
    )
    await db.commit()


async def does_deployment_belong_to_org(
    db: AsyncSession,
    org_id: UUID4,
    dep_id: UUID4,
) -> bool:
    result = await db.execute(
        select(models.Deployment.id)
        .where(models.Deployment.id == str(dep_id))
        .where(models.Deployment.org_id == str(org_id))
    )
    return result.scalar() is not None


async def update_deployment(
    db: AsyncSession,
    dep: models.Deployment,
    new_dep: schemas.DeploymentCreate,
) -> None:
    df = schemas.dump_to_dict(new_dep)
    await db.execute(
        update(models.Deployment)
        .where(models.Deployment.id == str(dep.id))
        .where(models.Deployment.org_id == str(dep.org_id))
        .values(name=new_dep.name, definition=df["definition"])
    )
    await db.commit()


async def search_deployments_by_title(
    db: AsyncSession, org_id: UUID4, term: str, page: int = 0, limit: int = 10
) -> List[models.Deployment]:
    result = await db.execute(
        select(models.Deployment)
        .where(models.Deployment.org_id == str(org_id))
        .where(models.Deployment.name.ilike(f"%{term}%"))
        .order_by(desc(models.Deployment.created_date))
        .offset(page)
        .limit(limit)
    )
    return result.scalars().all()


async def count_deployments_by_title(
    db: AsyncSession, org_id: UUID4, term: str
) -> int:
    result = await db.execute(
        select(func.count(models.Deployment.id))
        .where(models.Deployment.org_id == str(org_id))
        .where(models.Deployment.name.ilike(f"%{term}%"))
    )
    return cast(int, result.scalar())
