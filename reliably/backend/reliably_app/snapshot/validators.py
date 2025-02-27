from fastapi import Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import organization
from reliably_app.dependencies.database import get_db
from reliably_app.snapshot import crud, models

__all__ = ["valid_snapshot"]


async def valid_snapshot(
    snapshot_id: UUID4,
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(
        organization.validators.valid_org
    ),
) -> models.Snapshot:
    if not await crud.does_snapshot_belong_to_org(
        db,
        org.id,  # type: ignore
        snapshot_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    plan = await crud.get_snapshot(db, snapshot_id)
    if not plan:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return plan
