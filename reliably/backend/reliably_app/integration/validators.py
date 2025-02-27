from fastapi import Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import organization
from reliably_app.dependencies.database import get_db
from reliably_app.integration import crud, models

__all__ = ["valid_integration"]


async def valid_integration(
    integration_id: UUID4,
    org: organization.models.Organization = Depends(
        organization.validators.valid_org
    ),
    db: AsyncSession = Depends(get_db),
) -> models.Integration:
    if not await crud.does_integration_belong_to_org(
        db,
        org.id,  # type: ignore
        integration_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    intg = await crud.get_integration(db, integration_id)
    if not intg:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)  # noqa

    return intg
