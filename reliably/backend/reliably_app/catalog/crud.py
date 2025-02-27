from typing import List, cast

import orjson
from pydantic import UUID4
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app.catalog import models, schemas

__all__ = [
    "does_catalog_belong_to_org",
    "create_catalog",
    "get_catalog",
    "get_catalogs",
    "delete_catalog",
    "count_catalogs",
    "get_catalog_items_by_labels",
]


async def create_catalog(
    db: AsyncSession,
    org_id: UUID4,
    manifest: schemas.CatalogItemCreate,
    user_id: UUID4 | None = None,
) -> models.Catalog:
    db_catalog = models.Catalog(
        org_id=str(org_id),
        user_id=str(user_id) if user_id else None,
        manifest=orjson.loads(manifest.model_dump_json(by_alias=True)),
    )
    db.add(db_catalog)
    await db.commit()

    return cast(models.Catalog, db_catalog)


async def replace_catalog(
    db: AsyncSession,
    org_id: UUID4,
    item: models.Catalog,
    manifest: schemas.CatalogItemCreate,
    user_id: UUID4 | None = None,
) -> None:
    item.user_id = str(user_id) if user_id else str(item.user_id)  # type: ignore
    item.manifest = orjson.loads(manifest.model_dump_json(by_alias=True))

    await db.commit()


async def count_catalogs(db: AsyncSession, org_id: UUID4, provider: str) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.Catalog.id))
                .where(models.Catalog.org_id == str(org_id))
                .where(
                    models.Catalog.manifest.contains(
                        {"spec": {"provider": provider}}
                    )
                )
            )
        ).scalar_one(),
    )


async def get_catalog(
    db: AsyncSession, catalog_id: UUID4
) -> models.Catalog | None:
    return cast(models.Catalog, await db.get(models.Catalog, str(catalog_id)))


async def get_catalogs(
    db: AsyncSession,
    org_id: UUID4,
    provider: str,
    page: int = 0,
    limit: int = 10,
) -> List[models.Catalog]:
    results = await db.execute(
        select(models.Catalog)
        .where(models.Catalog.org_id == str(org_id))
        .where(
            models.Catalog.manifest.contains({"spec": {"provider": provider}})
        )
        .offset(page)
        .limit(limit)
    )
    return results.scalars().all()


async def delete_catalog(db: AsyncSession, catalog_id: UUID4) -> None:
    await db.execute(
        delete(models.Catalog).where(models.Catalog.id == str(catalog_id))
    )
    await db.commit()


async def does_catalog_belong_to_org(
    db: AsyncSession,
    org_id: UUID4,
    catalog_id: UUID4,
) -> bool:
    result = await db.execute(
        select(models.Catalog)
        .where(models.Catalog.id == str(catalog_id))
        .where(models.Catalog.org_id == str(org_id))
    )
    return result.scalar() is not None


async def get_catalog_items_by_labels(
    db: AsyncSession, org_id: UUID4, labels: List[str]
) -> List[models.Catalog]:
    results = await db.execute(
        select(models.Catalog)
        .where(models.Catalog.org_id == str(org_id))
        .where(
            models.Catalog.manifest.contains({"metadata": {"labels": labels}})
        )
        .where(
            models.Catalog.manifest.contains(
                {"spec": {"provider": "chaostoolkit"}}
            )
        )
    )
    return results.scalars().all()


async def get_catalog_items_by_name(
    db: AsyncSession, org_id: UUID4, provider: str, name: str
) -> models.Catalog | None:
    results = await db.execute(
        select(models.Catalog)
        .where(models.Catalog.org_id == str(org_id))
        .where(models.Catalog.manifest.contains({"metadata": {"name": name}}))
        .where(
            models.Catalog.manifest.contains({"spec": {"provider": provider}})
        )
        .limit(1)
    )
    return results.scalars().first()


async def get_catalog_items_labels(
    db: AsyncSession, org_id: UUID4
) -> List[str]:
    results = await db.execute(
        select(
            func.jsonb_array_elements_text(
                models.Catalog.manifest["metadata"]["labels"]
            )
        )
        .where(models.Catalog.org_id == str(org_id))
        .where(
            models.Catalog.manifest.contains(
                {"spec": {"provider": "chaostoolkit"}}
            )
        )
        .distinct()
    )
    return results.scalars().all()
