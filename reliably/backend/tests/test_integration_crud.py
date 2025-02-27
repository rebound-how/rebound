import uuid

import pytest
from faker import Faker

from reliably_app import environment
from reliably_app.database import SessionLocal
from reliably_app.integration import crud, errors, schemas


@pytest.mark.anyio
async def test_get_integrations_returns_nothing_when_no_integrations_exist(
    stack_ready,
):
    org_id = uuid.uuid4()
    async with SessionLocal() as db:
        assert await crud.get_integrations(db, org_id) == []


@pytest.mark.anyio
async def test_get_integrations_return_all_integrations(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()

    e = environment.schemas.EnvironmentCreate(
        name=name,
        envvars=[],
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_SEC", "value": "hi", "key": "blah"}]
        )
    )

    async with SessionLocal() as db:
        env = await environment.crud.create_environment(db, org_id, e, "integration")
        assert env.id is not None

    i = schemas.IntegrationCreate(
        name="slack",
        provider="slack",
        environment=e
    )
    async with SessionLocal() as db:
        intg = await crud.create_integration(db, org_id, i, env.id)
        assert intg.id is not None

    async with SessionLocal() as db:
        intgs = await crud.get_integrations(db, org_id)

    assert len(intgs) == 1
    assert intgs[0].id == intg.id
    assert str(intgs[0].org_id) == org_id
    assert intgs[0].name == intg.name


@pytest.mark.anyio
async def test_count_integrations(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()

    e = environment.schemas.EnvironmentCreate(
        name=name,
        envvars=[],
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )

    async with SessionLocal() as db:
        env = await environment.crud.create_environment(db, org_id, e, "integration")
        assert env.id is not None

    i = schemas.IntegrationCreate(
        name="slack",
        provider="slack",
        environment=e
    )
    async with SessionLocal() as db:
        intg = await crud.create_integration(db, org_id, i, env.id)
        assert intg.id is not None

    async with SessionLocal() as db:
        count = await crud.count_integrations(db, org_id)

    assert count == 1


@pytest.mark.anyio
async def test_get_integration(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()

    e = environment.schemas.EnvironmentCreate(
        name=name,
        envvars=[],
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )

    async with SessionLocal() as db:
        env = await environment.crud.create_environment(db, org_id, e, "integration")
        assert env.id is not None

    i = schemas.IntegrationCreate(
        name="slack",
        provider="slack",
        environment=e
    )
    async with SessionLocal() as db:
        intg = await crud.create_integration(db, org_id, i, env.id)
        assert intg.id is not None

    async with SessionLocal() as db:
        db_intg = await crud.get_integration(db, intg.id)

    assert db_intg.id == intg.id
    assert db_intg.org_id == org_id
    assert db_intg.name == intg.name


@pytest.mark.anyio
async def test_get_many_integrations(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()

    e = environment.schemas.EnvironmentCreate(
        name=name,
        envvars=[],
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )

    async with SessionLocal() as db:
        env = await environment.crud.create_environment(db, org_id, e, "integration")
        assert env.id is not None

    i = schemas.IntegrationCreate(
        name="slack",
        provider="slack",
        environment=e
    )
    async with SessionLocal() as db:
        intg = await crud.create_integration(db, org_id, i, env.id)
        assert intg.id is not None

    async with SessionLocal() as db:
        intgs = await crud.get_many_integrations(db, org_id, [intg.id])

    assert len(intgs) == 1


@pytest.mark.anyio
async def test_cannot_create_integration_with_same_name(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()

    e = environment.schemas.EnvironmentCreate(
        name=name,
        envvars=[],
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )

    async with SessionLocal() as db:
        env = await environment.crud.create_environment(db, org_id, e, "integration")
        assert env.id is not None

    i = schemas.IntegrationCreate(
        name="slack",
        provider="slack",
        environment=e
    )
    async with SessionLocal() as db:
        intg = await crud.create_integration(db, org_id, i, env.id)
        assert intg.id is not None

    e1 = environment.schemas.EnvironmentCreate(
        name=name,
        envvars=[],
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )

    async with SessionLocal() as db:
        env1 = await environment.crud.create_environment(db, org_id, e1, "integration")
        assert env1.id is not None

    i1 = schemas.IntegrationCreate(
        name="slack",
        provider="slack",
        environment=e1
    )

    with pytest.raises(errors.IntegrationAlreadyExistsError):
        async with SessionLocal() as db:
            intg = await crud.create_integration(db, org_id, i1, env1.id)
            assert intg.id is not None


@pytest.mark.anyio
async def test_get_user_returns_nothing_when_user_not_found(stack_ready):
    async with SessionLocal() as db:
        assert await crud.get_integration(db, uuid.uuid4()) is None


@pytest.mark.anyio
async def test_delete_integration(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()

    e = environment.schemas.EnvironmentCreate(
        name=name,
        envvars=[],
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )

    i = schemas.IntegrationCreate(
        name="slack",
        provider="slack",
        environment=e
    )

    async with SessionLocal() as db:
        env = await environment.crud.create_environment(
            db, org_id, e, "integration")
        assert env.id is not None

    async with SessionLocal() as db:
        intg = await crud.create_integration(db, org_id, i, env.id)
        assert intg.id is not None

    async with SessionLocal() as db:
        intg = await crud.get_integration(db, intg.id)
        assert intg is not None

    async with SessionLocal() as db:
        intgs = await crud.get_integrations(db, org_id)
        assert len(intgs) == 1

    async with SessionLocal() as db:
        await crud.delete_integration(db, intg.id)

    async with SessionLocal() as db:
        await environment.crud.delete_environment(db, env.id)

    async with SessionLocal() as db:
        intg = await crud.get_integration(db, env.id)
        assert intg is None

    async with SessionLocal() as db:
        intgs = await crud.get_integrations(db, org_id)
        assert len(intgs) == 0


@pytest.mark.anyio
async def test_does_integration_belong_to_org(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()

    e = environment.schemas.EnvironmentCreate(
        name=name,
        envvars=[],
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )

    i = schemas.IntegrationCreate(
        name="slack",
        provider="slack",
        environment=e
    )

    async with SessionLocal() as db:
        env = await environment.crud.create_environment(
            db, org_id, e, "integration")
        assert env.id is not None

    async with SessionLocal() as db:
        intg = await crud.create_integration(db, org_id, i, env.id)
        assert intg.id is not None

    async with SessionLocal() as db:
        assert (
            await crud.does_integration_belong_to_org(db, org_id, intg.id) is True
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_integration_belong_to_org(db, org_id, uuid.uuid4())
            is False
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_integration_belong_to_org(db, uuid.uuid4(), intg.id)
            is False
        )
