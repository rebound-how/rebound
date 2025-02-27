import uuid
from datetime import datetime, timezone

import pytest
from faker import Faker

from reliably_app import organization
from reliably_app.agent import crud, schemas
from reliably_app.database import SessionLocal


@pytest.mark.anyio
async def test_get_agents_returns_nothing_when_no_agents_exist(stack_ready):
    org_id = uuid.uuid4()
    async with SessionLocal() as db:
        assert await crud.get_agents(db, org_id) == []


@pytest.mark.anyio
async def test_get_agents_return_all_agents(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    token_id = str(uuid.uuid4())

    pl = schemas.AgentCreate(sub="xyz", user_id=user_id, token_id=token_id)

    async with SessionLocal() as db:
        agent = await crud.create_agent(db, org_id, pl, user_id)
        assert agent.id is not None

    async with SessionLocal() as db:
        agents = await crud.get_agents(db, org_id)

    assert len(agents) == 1
    assert agents[0].id == agent.id
    assert str(agents[0].org_id) == org_id


@pytest.mark.anyio
async def test_count_agents(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    token_id = str(uuid.uuid4())

    pl = schemas.AgentCreate(sub="xyz", user_id=user_id, token_id=token_id)

    async with SessionLocal() as db:
        agent = await crud.create_agent(db, org_id, pl, user_id)
        assert agent.id is not None

    async with SessionLocal() as db:
        count = await crud.count_agents(db, org_id)

    assert count == 1


@pytest.mark.anyio
async def test_create_internal_agent(stack_ready, fake: Faker):
    user_id = str(uuid.uuid4())

    name = fake.company()
    o = organization.schemas.OrganizationCreate(name=name)

    async with SessionLocal() as db:
        org = await organization.crud.create_org(db, o)
        assert org.id is not None

    async with SessionLocal() as db:
        agent = await crud.create_user_agent(org, user_id, internal=True)
        assert agent.id is not None

    async with SessionLocal() as db:
        agent = await crud.get_user_internal_agent(db, org.id, user_id)
        assert agent.id is not None
        assert agent.internal is True


@pytest.mark.anyio
async def test_get_agent(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    token_id = str(uuid.uuid4())

    pl = schemas.AgentCreate(sub="xyz", user_id=user_id, token_id=token_id)

    async with SessionLocal() as db:
        agent = await crud.create_agent(db, org_id, pl, user_id)
        assert agent.id is not None

    async with SessionLocal() as db:
        pl = await crud.get_agent(db, agent.id)

    assert pl.id == agent.id
    assert str(pl.org_id) == org_id


@pytest.mark.anyio
async def test_get_agent_returns_nothing_when_agent_not_found(stack_ready):
    async with SessionLocal() as db:
        assert await crud.get_agent(db, uuid.uuid4()) is None


@pytest.mark.anyio
async def test_delete_agent(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    token_id = str(uuid.uuid4())

    pl = schemas.AgentCreate(sub="xyz", user_id=user_id, token_id=token_id)

    async with SessionLocal() as db:
        agent = await crud.create_agent(db, org_id, pl, user_id)
        assert agent.id is not None

    async with SessionLocal() as db:
        agent = await crud.get_agent(db, agent.id)
        assert agent is not None

    async with SessionLocal() as db:
        agents = await crud.get_agents(db, org_id)
        assert len(agents) == 1

    async with SessionLocal() as db:
        await crud.delete_agent(db, agent.id)

    async with SessionLocal() as db:
        agent = await crud.get_agent(db, agent.id)
        assert agent is None

    async with SessionLocal() as db:
        agents = await crud.get_agents(db, org_id)
        assert len(agents) == 0


@pytest.mark.anyio
async def test_does_agent_belong_to_org(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    token_id = str(uuid.uuid4())

    pl = schemas.AgentCreate(sub="xyz", user_id=user_id, token_id=token_id)

    async with SessionLocal() as db:
        agent = await crud.create_agent(db, org_id, pl, user_id)
        assert agent.id is not None

    async with SessionLocal() as db:
        assert await crud.does_agent_belong_to_org(db, org_id, agent.id) is True

    async with SessionLocal() as db:
        assert (
            await crud.does_agent_belong_to_org(db, org_id, uuid.uuid4())
            is False
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_agent_belong_to_org(db, uuid.uuid4(), agent.id)
            is False
        )


@pytest.mark.anyio
async def test_set_state(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    token_id = str(uuid.uuid4())

    pl = schemas.AgentCreate(sub="xyz", user_id=user_id, token_id=token_id)

    async with SessionLocal() as db:
        agent = await crud.create_agent(db, org_id, pl, user_id)
        assert agent.id is not None
        assert agent.state is None

    async with SessionLocal() as db:
        st = schemas.AgentState(
            status="running",
            scheduled_plans=3,
            received_time=datetime.now(tz=timezone.utc),
        )
        pl = await crud.set_state(db, agent.id, st)

    async with SessionLocal() as db:
        agent = await crud.get_agent(db, agent.id)
        assert agent.state["status"] == "running"

        a = schemas.Agent.model_validate(agent, from_attributes=True)
        assert a.state.status == "running"


@pytest.mark.anyio
async def test_get_agent_from_user(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    token_id = str(uuid.uuid4())

    pl = schemas.AgentCreate(sub="xyz", user_id=user_id, token_id=token_id)

    async with SessionLocal() as db:
        agent = await crud.create_agent(db, org_id, pl, user_id)
        assert agent.id is not None

    async with SessionLocal() as db:
        a = await crud.get_agent_from_user(db, org_id, user_id)

    assert agent.id == a.id
