import secrets
from typing import List, cast

import orjson
from pydantic import UUID4
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import account, organization, token
from reliably_app.agent import models, schemas
from reliably_app.database import SessionLocal

__all__ = [
    "does_agent_belong_to_org",
    "create_agent",
    "create_user_agent",
    "get_agent",
    "get_agents",
    "get_user_internal_agent",
    "delete_agent",
    "count_agents",
    "get_agent_from_user",
]


async def create_agent(
    db: AsyncSession,
    org_id: UUID4,
    agent: schemas.AgentCreate,
    from_user_id: UUID4,
    internal: bool = False,
) -> models.Agent:
    name = f"agent-{agent.sub}"
    db_agent = models.Agent(
        org_id=org_id,
        name=name,
        user_id=str(agent.user_id),
        token_id=str(agent.token_id),
        internal=internal,
        from_user_id=from_user_id,
    )
    db.add(db_agent)
    await db.commit()

    return cast(models.Agent, db_agent)


async def create_user_agent(
    org: organization.models.Organization,
    from_user_id: UUID4,
    internal: bool = False,
) -> models.Agent:
    sub = secrets.token_hex(4)
    agent_name = f"agent-{sub}"

    async with SessionLocal() as s:
        uc = account.schemas.UserCreate(
            as_agent=True,
            username=agent_name,
            openid_profile={"sub": sub, "preferred_username": agent_name},
        )
        user = await account.crud.create_user(s, uc)
        user_id = str(user.id)

        async with SessionLocal() as s:
            await organization.crud.add_user(s, org, user, agent=True)

    async with SessionLocal() as s:
        tc = token.schemas.TokenCreate(name=f"agent-{sub}")
        t = await token.crud.create_token(
            s,
            org.id,  # type: ignore
            user_id,  # type: ignore
            tc,
        )
        token_id = str(t.id)

    async with SessionLocal() as s:
        ac = schemas.AgentCreate(
            org_id=org.id, user_id=user_id, token_id=token_id, sub=sub
        )
        agent = await create_agent(
            s,
            org.id,  # type: ignore
            ac,
            from_user_id,
            internal,
        )

    return agent


async def count_agents(db: AsyncSession, org_id: UUID4) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.Agent.id))
                .where(models.Agent.org_id == str(org_id))
                .where(models.Agent.internal.is_(False))
            )
        ).scalar_one(),
    )


async def get_agent(db: AsyncSession, agent_id: UUID4) -> models.Agent | None:
    return cast(models.Agent, await db.get(models.Agent, str(agent_id)))


async def get_user_internal_agent(
    db: AsyncSession, org_id: UUID4, from_user_id: UUID4
) -> models.Agent | None:
    results = await db.execute(
        select(models.Agent)
        .where(models.Agent.org_id == str(org_id))
        .where(models.Agent.from_user_id == str(from_user_id))
        .where(models.Agent.internal.is_(True))
        .limit(1)
    )
    return results.scalars().first()


async def get_agents(
    db: AsyncSession, org_id: UUID4, page: int = 0, limit: int = 10
) -> List[models.Agent]:
    results = await db.execute(
        select(models.Agent)
        .where(models.Agent.org_id == str(org_id))
        .where(models.Agent.internal.is_(False))
        .order_by(models.Agent.name)
        .offset(page)
        .limit(limit)
    )
    return results.scalars().all()


async def delete_agent(db: AsyncSession, agent_id: UUID4) -> None:
    await db.execute(
        delete(models.Agent).where(models.Agent.id == str(agent_id))
    )
    await db.commit()


async def does_agent_belong_to_org(
    db: AsyncSession,
    org_id: UUID4,
    agent_id: UUID4,
) -> bool:
    result = await db.execute(
        select(models.Agent)
        .where(models.Agent.id == str(agent_id))
        .where(models.Agent.org_id == str(org_id))
    )
    return result.scalar() is not None


async def set_state(
    db: AsyncSession, agent_id: UUID4, state: schemas.AgentState
) -> None:
    q = (
        update(models.Agent)
        .where(models.Agent.id == str(agent_id))
        .values(state=orjson.loads(state.model_dump_json()))
    )

    await db.execute(q)
    await db.commit()


async def get_agent_from_user(
    db: AsyncSession, org_id: UUID4, user_id: UUID4
) -> models.Agent | None:
    result = await db.execute(
        select(models.Agent)
        .where(models.Agent.org_id == str(org_id))
        .where(models.Agent.user_id == str(user_id))
    )

    return result.scalars().first()


async def get_from_user_id(
    db: AsyncSession, org_id: UUID4, agent_user_id: UUID4
) -> models.Agent | None:
    result = await db.execute(
        select(models.Agent)
        .where(models.Agent.org_id == str(org_id))
        .where(models.Agent.user_id == str(agent_user_id))
    )

    return result.scalars().first()


async def get_from_real_user_id(
    db: AsyncSession, org_id: UUID4, user_id: UUID4
) -> models.Agent | None:
    result = await db.execute(
        select(models.Agent)
        .where(models.Agent.org_id == str(org_id))
        .where(models.Agent.from_user_id == str(user_id))
    )

    return result.scalars().first()
