from fastapi import Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app.dependencies.database import get_db
from reliably_app.organization import crud, models

__all__ = ["valid_org"]


async def valid_org(
    org_id: UUID4, db: AsyncSession = Depends(get_db)
) -> models.Organization:
    org = await crud.get_org(db, org_id)
    if not org:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if org.deleted:
        raise HTTPException(status.HTTP_410_GONE)

    return org
