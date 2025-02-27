import logging

from fastapi import Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import organization
from reliably_app.dependencies.database import get_db
from reliably_app.plan import crud, models

__all__ = ["valid_plan"]

logger = logging.getLogger("reliably_app")


async def valid_plan(
    plan_id: UUID4,
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(
        organization.validators.valid_org
    ),
) -> models.Plan:
    if not await crud.does_plan_belong_to_org(
        db,
        org.id,  # type: ignore
        plan_id,
    ):
        logger.info(f"Plan {plan_id} does not belong to org {org.id}")
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    plan = await crud.get_plan(db, plan_id)
    if not plan:  # pragma: no cover
        logger.info(f"Plan {plan_id} could not be found")
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return plan
