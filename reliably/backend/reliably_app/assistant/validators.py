from fastapi import Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import organization
from reliably_app.assistant import crud, models
from reliably_app.dependencies.database import get_db

__all__ = ["valid_scenario"]


async def valid_scenario(
    scenario_id: UUID4,
    org: organization.models.Organization = Depends(
        organization.validators.valid_org
    ),
    db: AsyncSession = Depends(get_db),
) -> models.AssistantScenario:
    if not await crud.does_scenario_belong_to_org(
        db,
        org.id,  # type: ignore
        scenario_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    scenario = await crud.get_scenario(db, scenario_id)
    if not scenario:  # noqa
        raise HTTPException(status.HTTP_404_NOT_FOUND)  # pragma: nocover

    return scenario
