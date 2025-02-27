import uuid

import pytest
from faker import Faker
from fastapi import HTTPException

from reliably_app.database import SessionLocal
from reliably_app.organization import crud, schemas, validators


@pytest.mark.anyio
async def test_unknown_org_raises_401(stack_ready):
    with pytest.raises(HTTPException):
        async with SessionLocal() as db:
            await validators.valid_org(uuid.uuid4(), db)


@pytest.mark.anyio
async def test_returns_user(stack_ready, fake: Faker):
    name = fake.name()

    async with SessionLocal() as db:
        org = await crud.create_org(db, schemas.OrganizationCreate(name=name))

    async with SessionLocal() as db:
        o = await validators.valid_org(org.id, db)

    assert o.id == org.id
    assert o.name == org.name
