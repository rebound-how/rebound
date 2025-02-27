import uuid

import pytest
from faker import Faker
from fastapi import HTTPException

from reliably_app.account import crud, schemas, validators
from reliably_app.database import SessionLocal


@pytest.mark.anyio
async def test_unknown_user_raises_401(stack_ready):
    with pytest.raises(HTTPException):
        async with SessionLocal() as db:
            await validators.valid_user(db, user_id=uuid.uuid4())


@pytest.mark.anyio
async def test_returns_user(stack_ready, fake: Faker):
    username = fake.name()
    email = fake.company_email()
    async with SessionLocal() as db:
        user = await crud.create_user(
            db, schemas.UserCreate(username=username, email=email)
        )

    async with SessionLocal() as db:
        u = await validators.valid_user(db, user_id=user.id)
        assert u.id == user.id
        assert u.email == user.email
        assert u.username == user.username
