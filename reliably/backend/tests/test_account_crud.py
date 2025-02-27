import uuid

import pytest
from authlib.oidc.core import UserInfo
from faker import Faker

from reliably_app.account import crud, errors, schemas
from reliably_app.database import SessionLocal


@pytest.mark.anyio
async def test_get_users_returns_nothing_when_no_user_exist(stack_ready):
    async with SessionLocal() as db:
        assert await crud.get_users(db) == []


@pytest.mark.anyio
async def test_get_users_return_all_users(stack_ready, fake: Faker):
    username = fake.name()
    email = fake.company_email()

    u = schemas.UserCreate(
        username=username, email=email, openid=UserInfo({"sub": "xyz"})
    )

    async with SessionLocal() as db:
        user = await crud.create_user(db, u)
        assert user.id is not None

    async with SessionLocal() as db:
        users = await crud.get_users(db)

    assert len(users) == 1
    assert users[0].id == user.id
    assert users[0].username == user.username
    assert users[0].email == user.email


@pytest.mark.anyio
async def test_count_users(stack_ready, fake: Faker):
    username = fake.name()
    email = fake.company_email()

    u = schemas.UserCreate(
        username=username, email=email, openid=UserInfo({"sub": "xyz"})
    )

    async with SessionLocal() as db:
        user = await crud.create_user(db, u)
        assert user.id is not None

    async with SessionLocal() as db:
        count = await crud.count_users(db)
        assert count == 1


@pytest.mark.anyio
async def test_get_user(stack_ready, fake: Faker):
    username = fake.name()
    email = fake.company_email()

    u = schemas.UserCreate(
        username=username, email=email, openid=UserInfo({"sub": "xyz"})
    )

    async with SessionLocal() as db:
        user = await crud.create_user(db, u)

    async with SessionLocal() as db:
        fetched_user = await crud.get_user(db, user.id)

    assert fetched_user.id == user.id
    assert fetched_user.username == user.username
    assert fetched_user.email == user.email


@pytest.mark.anyio
async def test_get_user_by_openid(stack_ready, fake: Faker):
    username = fake.name()
    email = fake.company_email()

    u = schemas.UserCreate(
        username=username, email=email, openid=UserInfo({"sub": "xyz"})
    )

    async with SessionLocal() as db:
        user = await crud.create_user(db, u)

    async with SessionLocal() as db:
        fetched_user = await crud.get_user_by_openid(
            db, UserInfo({"sub": "xyz"})
        )

    assert fetched_user.id == user.id
    assert fetched_user.username == user.username
    assert fetched_user.email == user.email


@pytest.mark.anyio
async def test_get_user_returns_nothing_when_user_not_found(stack_ready):
    async with SessionLocal() as db:
        assert await crud.get_user(db, uuid.uuid4()) is None


@pytest.mark.anyio
async def test_cannot_create_user_with_same_email(stack_ready, fake: Faker):
    username = fake.name()
    email = fake.company_email()

    u = schemas.UserCreate(
        username=username, email=email, openid=UserInfo({"sub": "xyz"})
    )
    async with SessionLocal() as db:
        await crud.create_user(db, u)

    username = fake.name()
    u = schemas.UserCreate(
        username=username, email=email, openid=UserInfo({"sub": "xyz"})
    )

    try:
        async with SessionLocal() as db:
            await crud.create_user(db, u)
    except errors.UserAlreadyExistError:
        pytest.fail("create two users with the same email is tolerated")


@pytest.mark.anyio
async def test_cannot_create_user_with_same_username(stack_ready, fake: Faker):
    username = fake.name()
    email = fake.company_email()

    u = schemas.UserCreate(
        username=username, email=email, openid=UserInfo({"sub": "xyz"})
    )
    async with SessionLocal() as db:
        await crud.create_user(db, u)

    email = fake.company_email()
    u = schemas.UserCreate(
        username=username, email=email, openid=UserInfo({"sub": "xyz"})
    )

    with pytest.raises(errors.UserAlreadyExistError):
        async with SessionLocal() as db:
            await crud.create_user(db, u)
