from fastapi import Depends, HTTPException, Path, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import organization
from reliably_app.dependencies.database import get_db

__all__ = ["valid_org"]


async def valid_org(
    org_id: UUID4 = Path(), db: AsyncSession = Depends(get_db)
) -> organization.models.Organization:
    org = await organization.crud.get_org(db, org_id)
    if not org:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if org.deleted:
        raise HTTPException(status.HTTP_410_GONE)

    return org
