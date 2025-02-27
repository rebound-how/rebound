import re

import pytest
from authlib.oidc.core import UserInfo
from faker import Faker

from reliably_app import account, login
from reliably_app.database import SessionLocal
from reliably_app.organization import crud, errors, schemas


@pytest.mark.anyio
async def test_get_user_organizations(stack_ready, fake: Faker):
    username = fake.name()
    email = fake.company_email()
    u = account.schemas.UserCreate(username=username, email=email)

    name = fake.company()
    o = schemas.OrganizationCreate(name=name)

    async with SessionLocal() as d1:
        user = await account.crud.create_user(d1, u)

    async with SessionLocal() as d2:
        org = await crud.create_org(d2, o)

    async with SessionLocal() as db:
        orgs = await crud.get_user_orgs(db, user.id)
        assert len(orgs) == 0

    async with SessionLocal() as db:
        await crud.add_user(db, org, user)

    async with SessionLocal() as db:
        orgs = await crud.get_user_orgs(db, user.id)
        assert len(orgs) == 1
        assert orgs[0].id == org.id


@pytest.mark.anyio
async def test_get_org_users(stack_ready, fake: Faker):
    username = fake.name()
    email = fake.company_email()
    u1 = account.schemas.UserCreate(username=username, email=email)

    username = fake.name()
    email = fake.company_email()
    u2 = account.schemas.UserCreate(username=username, email=email)

    username = fake.name()
    email = fake.company_email()
    u3 = account.schemas.UserCreate(username=username, email=email)

    name = fake.company()
    o1 = schemas.OrganizationCreate(name=name)

    name = fake.company()
    o2 = schemas.OrganizationCreate(name=name)

    async with SessionLocal() as d1:
        user1 = await account.crud.create_user(d1, u1)
    async with SessionLocal() as d2:
        user2 = await account.crud.create_user(d2, u2)
    async with SessionLocal() as d3:
        user3 = await account.crud.create_user(d3, u3)
    async with SessionLocal() as d4:
        org1 = await crud.create_org(d4, o1)
    async with SessionLocal() as d5:
        org2 = await crud.create_org(d5, o2)

    async with SessionLocal() as d1:
        await crud.add_user(d1, org1, user1)
    async with SessionLocal() as d1:
        await crud.add_user(d2, org1, user3)
    async with SessionLocal() as d1:
        await crud.add_user(d3, org2, user2)

    async with SessionLocal() as db:
        users = await crud.get_org_users(db, org1.id)
        assert len(users) == 2

        users = await crud.get_org_users(db, org2.id)
        assert len(users) == 1

    async with SessionLocal() as db:
        await crud.remove_user(db, org1, user1)
        users = await crud.get_org_users(db, org1.id)
        assert len(users) == 1


@pytest.mark.anyio
async def test_create_org(stack_ready, fake: Faker):
    name = fake.company()
    o = schemas.OrganizationCreate(name=name)

    async with SessionLocal() as db:
        org = await crud.create_org(db, o)
    assert org is not None
    assert org.name == name


@pytest.mark.anyio
async def test_delete_org(stack_ready, fake: Faker):
    name = fake.company()
    o = schemas.OrganizationCreate(name=name)

    async with SessionLocal() as db:
        org = await crud.create_org(db, o)
    assert org is not None
    assert org.name == name

    async with SessionLocal() as db:
        await crud.delete_org(db, org.id)

    async with SessionLocal() as db:
        assert await crud.get_org(db, org.id) is None


@pytest.mark.anyio
async def test_cannot_create_org_with_same_name(stack_ready, fake: Faker):
    name = fake.company()
    o = schemas.OrganizationCreate(name=name)
    async with SessionLocal() as db:
        await crud.create_org(db, o)

    with pytest.raises(errors.OrgAlreadyExistError):
        async with SessionLocal() as db:
            await crud.create_org(db, o)


@pytest.mark.anyio
async def test_create_org_and_user_from_registration(stack_ready, fake: Faker):
    name = fake.name()
    user_info = UserInfo(sub="xyz", preferred_username=name)

    async with SessionLocal() as db:
        org, user = await login.tasks.new_org(
            name, info=user_info
        )
        org_id = org.id
        user_id = user.id

    async with SessionLocal() as db:
        orgs = await crud.get_user_orgs(db, user_id)
        assert len(orgs) == 1
        assert orgs[0].name == name

    async with SessionLocal() as db:
        users = await crud.get_org_users(db, org_id)
        assert len(users) == 1
        assert users[0].id == user_id
        assert users[0].username == name


@pytest.mark.anyio
async def test_automatically_add_suffix_when_orgname_taken(stack_ready, fake: Faker):
    name = fake.name()
    user_info = UserInfo(sub="xyz", preferred_username=name)
    oc = schemas.OrganizationCreate(name=name)

    async with SessionLocal() as db:
        await crud.create_org(db, oc)

    async with SessionLocal() as db:
        org, _ = await login.tasks.new_org(name, info=user_info)
        assert re.match(f"{name}[0-9]{{5,5}}", org.name) is not None


@pytest.mark.anyio
async def test_fail_if_user_already_exists(stack_ready, fake: Faker):
    name = fake.name()
    user_info = UserInfo(sub="xyz", preferred_username=name)
    uc = account.schemas.UserCreate(
        username=name, email=fake.company_email(), openid_profile=user_info
    )

    async with SessionLocal() as db:
        await account.crud.create_user(db, uc)

    with pytest.raises(account.errors.UserAlreadyExistError):
        async with SessionLocal() as db:
            await login.tasks.new_org(name, info=user_info)


@pytest.mark.anyio
async def test_count_user_in_orgs(stack_ready, authed):
    authed_org, _, _ = authed
    async with SessionLocal() as db:
        count = await crud.count_users_in_org(db, authed_org.id)

    assert count == 1
