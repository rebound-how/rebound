from fastapi import Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import organization
from reliably_app.dependencies.database import get_db
from reliably_app.experiment import crud, models

__all__ = ["valid_experiment"]


async def valid_experiment(
    exp_id: UUID4,
    org: organization.models.Organization = Depends(
        organization.validators.valid_org
    ),
    db: AsyncSession = Depends(get_db),
) -> models.Experiment:
    if not await crud.does_experiment_belong_to_org(
        db,
        org.id,  # type: ignore
        exp_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    exp = await crud.get_experiment(db, exp_id)
    if not exp:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return exp
