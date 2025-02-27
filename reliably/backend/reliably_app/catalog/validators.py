from fastapi import Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import organization
from reliably_app.catalog import crud, models
from reliably_app.dependencies.database import get_db

__all__ = ["valid_catalog"]


async def valid_catalog(
    catalog_id: UUID4,
    org: organization.models.Organization = Depends(
        organization.validators.valid_org
    ),
    db: AsyncSession = Depends(get_db),
) -> models.Catalog:
    if not await crud.does_catalog_belong_to_org(
        db,
        org.id,  # type: ignore
        catalog_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    agent = await crud.get_catalog(db, catalog_id)
    if not agent:  # noqa
        raise HTTPException(status.HTTP_404_NOT_FOUND)  # pragma: nocover

    return agent
