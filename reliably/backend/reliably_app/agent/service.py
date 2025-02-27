import sys
from datetime import datetime, timezone
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from reliably_app import account, organization, token
from reliably_app.agent import crud, models, schemas, validators
from reliably_app.dependencies.auth import with_user_in_org
from reliably_app.dependencies.database import get_db
from reliably_app.dependencies.org import valid_org

__all__ = ["extend_routers"]

router = APIRouter()


def extend_routers(web: APIRouter, api: APIRouter) -> None:
    web.include_router(router, prefix="/agents", include_in_schema=False)
    api.include_router(router, prefix="/agents")


@router.get(
    "",
    response_model=schemas.Agents,
    status_code=status.HTTP_200_OK,
    description="Retrieve all organization's agents",
    tags=["Agent"],
    summary="Retrieve all organization's agents",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Agents,
            "description": "Ok Response",
        }
    },
)
async def index(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, int | List[models.Agent]]:
    count = await crud.count_agents(db, org.id)  # type: ignore

    if not count:
        return {"count": 0, "items": []}

    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    if (limit * page) > count:
        return {"count": count, "items": []}

    agents = await crud.get_agents(
        db,
        org.id,  # type: ignore
        page=limit * page,
        limit=limit,
    )
    return {"count": count, "items": agents}


@router.post(
    "",
    response_model=schemas.Agent,
    status_code=status.HTTP_201_CREATED,
    description="Add a new agent",
    tags=["Agent"],
    summary="Add a new agent",
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.Agent,
            "description": "Created",
        },
        status.HTTP_409_CONFLICT: {
            "model": str,
            "description": "Name already used",
        },
    },
)
async def create(
    request: Request,
    user: account.models.User = Depends(with_user_in_org),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Agent:
    return await crud.create_user_agent(org, user.id)  # type: ignore


@router.get(
    "/{agent_id}",
    name="get_agent",
    response_model=schemas.Agent,
    status_code=status.HTTP_200_OK,
    description="Retrieve an agent in an organinzation",
    tags=["Agent"],
    summary="Retrieve an agent",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Agent,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Agent was not found",
        },
    },
)
async def get(
    agent: models.Agent = Depends(validators.valid_agent),
) -> models.Agent:
    return agent


@router.delete(
    "/{agent_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Delete the given agent",
    tags=["Agent"],
    summary="Delete the given agent",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
    },
)
async def delete(
    agent_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    if not await crud.does_agent_belong_to_org(
        db,
        org.id,  # type: ignore
        agent_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await crud.delete_agent(db, agent_id)


@router.put(
    "/{agent_id}/state",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Set the state of the agent",
    tags=["Plan"],
    summary="Set the state of the agent",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Agent was not found",
        },
    },
)
async def set_state(
    state: schemas.AgentState,
    agent: models.Agent = Depends(validators.valid_agent),
    db: AsyncSession = Depends(get_db),
) -> None:
    state.received_time = datetime.now(tz=timezone.utc)
    await crud.set_state(db, agent.id, state)  # type: ignore


@router.get(
    "/{agent_id}/token",
    response_model=token.schemas.Token,
    status_code=status.HTTP_200_OK,
    description="Get the agent's token",
    tags=["Plan"],
    summary="Get the agent's token",
    responses={
        status.HTTP_200_OK: {
            "model": token.schemas.Token,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Agent was not found",
        },
    },
)
async def get_agent_token(
    agent: models.Agent = Depends(validators.valid_agent),
    db: AsyncSession = Depends(get_db),
) -> token.models.Token:
    return await token.crud.get_token(db, agent.token_id)  # type: ignore
