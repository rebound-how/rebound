from fastapi import Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import organization
from reliably_app.agent import crud, models
from reliably_app.dependencies.database import get_db

__all__ = ["valid_agent"]


async def valid_agent(
    agent_id: UUID4,
    org: organization.models.Organization = Depends(
        organization.validators.valid_org
    ),
    db: AsyncSession = Depends(get_db),
) -> models.Agent:
    if not await crud.does_agent_belong_to_org(
        db,
        org.id,  # type: ignore
        agent_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    agent = await crud.get_agent(db, agent_id)
    if not agent:  # noqa
        raise HTTPException(status.HTTP_404_NOT_FOUND)  # pragma: nocover

    return agent
