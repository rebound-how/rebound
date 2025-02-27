import uuid

import pytest
from faker import Faker

from reliably_app.database import SessionLocal
from reliably_app.environment import crud, schemas


@pytest.mark.anyio
async def test_get_environments_returns_nothing_when_no_environments_exist(
    stack_ready,
):
    org_id = uuid.uuid4()
    async with SessionLocal() as db:
        assert await crud.get_environments(db, org_id) == []


@pytest.mark.anyio
async def test_get_environments_return_all_environments(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()

    e = schemas.EnvironmentCreate(
        name=name,
        envvars=schemas.EnvironmentVars(root=[{"var_name": "MY_VAR", "value": "hi"}]),
        secrets=schemas.EnvironmentSecrets(root=[{"var_name": "MY_SEC", "value": "hi", "key": "blah"}])
    )

    async with SessionLocal() as db:
        env = await crud.create_environment(db, org_id, e)
        assert env.id is not None

    async with SessionLocal() as db:
        envs = await crud.get_environments(db, org_id)

    assert len(envs) == 1
    assert envs[0].id == env.id
    assert str(envs[0].org_id) == org_id
    assert envs[0].name == e.name
    assert envs[0].envvars == env.envvars
    assert envs[0].secrets[0]["var_name"] == "MY_SEC"
    assert envs[0].secrets[0]["key"] == "blah"
    assert "value" in envs[0].secrets[0]


@pytest.mark.anyio
async def test_count_environments(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()

    e = schemas.EnvironmentCreate(
        name=name,
        envvars=schemas.EnvironmentVars(
            root=[{"var_name": "MY_VAR", "value": "hi"}]
        ),
        secrets=schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )

    async with SessionLocal() as db:
        env = await crud.create_environment(db, org_id, e)
        assert env.id is not None

    async with SessionLocal() as db:
        count = await crud.count_environments(db, org_id)

    assert count == 1


@pytest.mark.anyio
async def test_get_environment(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()

    e = schemas.EnvironmentCreate(
        name=name,
        envvars=schemas.EnvironmentVars(
            root=[{"var_name": "MY_VAR", "value": "hi"}]
        ),
        secrets=schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )

    async with SessionLocal() as db:
        env = await crud.create_environment(db, org_id, e)
        assert env.id is not None

    async with SessionLocal() as db:
        db_env = await crud.get_environment(db, env.id)

    assert db_env.id == env.id
    assert db_env.org_id == org_id
    assert db_env.name == env.name
    assert db_env.envvars == env.envvars
    assert len(db_env.secrets) == 1


@pytest.mark.anyio
async def test_get_user_returns_nothing_when_user_not_found(stack_ready):
    async with SessionLocal() as db:
        assert await crud.get_environment(db, uuid.uuid4()) is None


@pytest.mark.anyio
async def test_delete_environment(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()

    e = schemas.EnvironmentCreate(
        name=name,
        envvars=schemas.EnvironmentVars(
            root=[{"var_name": "MY_VAR", "value": "hi"}]
        ),
        secrets=schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )

    async with SessionLocal() as db:
        env = await crud.create_environment(db, org_id, e)
        assert env.id is not None

    async with SessionLocal() as db:
        env = await crud.get_environment(db, env.id)
        assert env is not None

    async with SessionLocal() as db:
        envs = await crud.get_environments(db, org_id)
        assert len(envs) == 1

    async with SessionLocal() as db:
        await crud.delete_environment(db, env.id)

    async with SessionLocal() as db:
        env = await crud.get_environment(db, env.id)
        assert env is None

    async with SessionLocal() as db:
        envs = await crud.get_environments(db, org_id)
        assert len(envs) == 0


@pytest.mark.anyio
async def test_does_environment_belong_to_org(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()

    e = schemas.EnvironmentCreate(
        name=name,
        envvars=schemas.EnvironmentVars(root=[{"var_name": "MY_VAR", "value": "hi"}]),
        secrets=schemas.EnvironmentSecrets(root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}])
    )

    async with SessionLocal() as db:
        env = await crud.create_environment(db, org_id, e)
        assert env.id is not None

    async with SessionLocal() as db:
        assert (
            await crud.does_environment_belong_to_org(db, org_id, env.id) is True
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_environment_belong_to_org(db, org_id, uuid.uuid4())
            is False
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_environment_belong_to_org(db, uuid.uuid4(), env.id)
            is False
        )
