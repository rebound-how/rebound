import secrets
import uuid

import pytest
from faker import Faker

from reliably_app.database import SessionLocal
from reliably_app.deployment import crud, errors, schemas


@pytest.mark.anyio
async def test_get_deployments_returns_nothing_when_no_deployments_exist(
    stack_ready,
):
    org_id = uuid.uuid4()
    async with SessionLocal() as db:
        assert await crud.get_deployments(db, org_id) == []


@pytest.mark.anyio
async def test_get_deployments_return_all_deployments(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()
    repo = "https://github.com/my/repo"
    gh_dep_name = fake.name()
    username = fake.user_name()
    token = secrets.token_hex(16)

    dc = schemas.DeploymentCreate(
        name=name,
        definition=schemas.DeploymentGitHubDefinition(
            repo=repo, name=gh_dep_name, username=username, token=token
        ),
    )

    async with SessionLocal() as db:
        dep = await crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    async with SessionLocal() as db:
        deps = await crud.get_deployments(db, org_id)

    assert len(deps) == 1
    assert deps[0].id == dep.id
    assert str(deps[0].org_id) == org_id
    assert deps[0].name == dep.name
    assert deps[0].definition == dep.definition


@pytest.mark.anyio
async def test_count_deployments(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()
    repo = "https://github.com/my/repo"
    gh_dep_name = fake.name()
    username = fake.user_name()
    token = secrets.token_hex(16)

    dc = schemas.DeploymentCreate(
        name=name,
        definition=schemas.DeploymentGitHubDefinition(
            repo=repo, name=gh_dep_name, username=username, token=token
        ),
    )

    async with SessionLocal() as db:
        dep = await crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    async with SessionLocal() as db:
        count = await crud.count_deployments(db, org_id)

    assert count == 1


@pytest.mark.anyio
async def test_get_deployment(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()
    repo = "https://github.com/my/repo"
    gh_dep_name = fake.name()
    username = fake.user_name()
    token = secrets.token_hex(16)

    dc = schemas.DeploymentCreate(
        name=name,
        definition=schemas.DeploymentGitHubDefinition(
            repo=repo, name=gh_dep_name, username=username, token=token
        ),
    )

    async with SessionLocal() as db:
        dep = await crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    async with SessionLocal() as db:
        db_dep = await crud.get_deployment(db, dep.id)

    assert db_dep.id == dep.id
    assert db_dep.org_id == org_id
    assert db_dep.name == dep.name
    assert db_dep.definition == dep.definition


@pytest.mark.anyio
async def test_get_user_returns_nothing_when_user_not_found(stack_ready):
    async with SessionLocal() as db:
        assert await crud.get_deployment(db, uuid.uuid4()) is None


@pytest.mark.anyio
async def test_cannot_create_deployment_with_same_name(
    stack_ready, fake: Faker
):
    org_id = str(uuid.uuid4())
    name = fake.name()
    repo = "https://github.com/my/repo"
    gh_dep_name = fake.name()
    username = fake.user_name()
    token = secrets.token_hex(16)

    dc = schemas.DeploymentCreate(
        name=name,
        definition=schemas.DeploymentGitHubDefinition(
            repo=repo, name=gh_dep_name, username=username, token=token
        ),
    )

    async with SessionLocal() as db:
        dep = await crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    with pytest.raises(errors.DeploymentAlreadyExistsError):
        async with SessionLocal() as db:
            await crud.create_deployment(db, org_id, dc)


@pytest.mark.anyio
async def test_delete_deployment(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()
    repo = "https://github.com/my/repo"
    gh_dep_name = fake.name()
    username = fake.user_name()
    token = secrets.token_hex(16)

    dc = schemas.DeploymentCreate(
        name=name,
        definition=schemas.DeploymentGitHubDefinition(
            repo=repo, name=gh_dep_name, username=username, token=token
        ),
    )

    async with SessionLocal() as db:
        dep = await crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    async with SessionLocal() as db:
        dep = await crud.get_deployment(db, dep.id)
        assert dep is not None

    async with SessionLocal() as db:
        deps = await crud.get_deployments(db, org_id)
        assert len(deps) == 1

    async with SessionLocal() as db:
        await crud.delete_deployment(db, dep.id)

    async with SessionLocal() as db:
        dep = await crud.get_deployment(db, dep.id)
        assert dep is None

    async with SessionLocal() as db:
        deps = await crud.get_deployments(db, org_id)
        assert len(deps) == 0


@pytest.mark.anyio
async def test_does_deployment_belong_to_org(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()
    repo = "https://github.com/my/repo"
    gh_dep_name = fake.name()
    username = fake.user_name()
    token = secrets.token_hex(16)

    dc = schemas.DeploymentCreate(
        name=name,
        definition=schemas.DeploymentGitHubDefinition(
            repo=repo, name=gh_dep_name, username=username, token=token
        ),
    )

    async with SessionLocal() as db:
        dep = await crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    async with SessionLocal() as db:
        assert (
            await crud.does_deployment_belong_to_org(db, org_id, dep.id) is True
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_deployment_belong_to_org(db, org_id, uuid.uuid4())
            is False
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_deployment_belong_to_org(db, uuid.uuid4(), dep.id)
            is False
        )


@pytest.mark.anyio
async def test_update_deployment(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    name = fake.name()
    repo = "https://github.com/my/repo"
    gh_dep_name = fake.name()
    username = fake.user_name()
    token = secrets.token_hex(16)

    dc = schemas.DeploymentCreate(
        name=name,
        definition=schemas.DeploymentGitHubDefinition(
            repo=repo, username=username, token=token
        ),
    )

    async with SessionLocal() as db:
        dep = await crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    async with SessionLocal() as db:
        db_dep = await crud.get_deployment(db, dep.id)

    assert db_dep.id == dep.id
    assert db_dep.org_id == org_id
    assert db_dep.name == dep.name
    assert db_dep.definition == dep.definition

    username = fake.user_name()
    token = secrets.token_hex(16)

    new_dc = schemas.DeploymentCreate(
        name=name,
        definition=schemas.DeploymentGitHubDefinition(
            repo=repo, username=username, token=token
        ),
    )

    async with SessionLocal() as db:
        await crud.update_deployment(db, db_dep, new_dc)

    async with SessionLocal() as db:
        new_db_dep = await crud.get_deployment(db, dep.id)

    assert db_dep.id == new_db_dep.id
    assert db_dep.org_id == new_db_dep.org_id
    assert db_dep.name == new_db_dep.name
    assert db_dep.definition != new_db_dep.definition

    dc = schemas.Deployment.model_validate(new_db_dep, from_attributes=True)
    assert dc.definition.username == username
    assert dc.definition.clear_token == token
