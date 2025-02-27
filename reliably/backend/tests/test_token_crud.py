from uuid import uuid4

import pytest
from faker import Faker

from reliably_app.database import SessionLocal
from reliably_app.token import crud, errors, schemas


@pytest.mark.anyio
async def test_create_token(stack_ready, fake: Faker):
    async with SessionLocal() as db:
        tok = await crud.create_token(
            db, uuid4(), uuid4(), schemas.TokenCreate(name=fake.name())
        )
        assert tok.id is not None
        assert tok.token is not None
        assert len(tok.token) == 32
        assert tok.revoked is False


@pytest.mark.anyio
async def test_create_token_fails_if_name_already_used(
    stack_ready, fake: Faker
):
    tc = schemas.TokenCreate(name=fake.name())
    uid = uuid4()
    oid = uuid4()
    async with SessionLocal() as db:
        t = await crud.create_token(db, oid, uid, tc)
        assert t.id is not None
        assert t.token is not None
        assert len(t.token) == 32

    with pytest.raises(errors.TokenNameAlreadyExistError):
        async with SessionLocal() as db:
            await crud.create_token(db, oid, uid, tc)


@pytest.mark.anyio
async def test_get_tokens(stack_ready, fake: Faker):
    tc1 = schemas.TokenCreate(name=fake.name())
    tc2 = schemas.TokenCreate(name=fake.name())

    uid = uuid4()
    oid = uuid4()

    async with SessionLocal() as db:
        tok1 = await crud.create_token(db, oid, uid, tc1)
        tok2 = await crud.create_token(db, oid, uid, tc2)
        tokens = await crud.get_tokens(db, oid, uid)
        assert len(tokens) == 2
        assert tok1 in tokens
        assert tok2 in tokens


@pytest.mark.anyio
async def test_get_token(stack_ready, fake: Faker):
    async with SessionLocal() as db:
        tok = await crud.create_token(
            db, uuid4(), uuid4(), schemas.TokenCreate(name=fake.name())
        )
        assert tok.id is not None
        assert tok.token is not None
        assert len(tok.token) == 32

        async with SessionLocal() as db:
            t = await crud.get_token(db, tok.id)
            assert tok.id == t.id


@pytest.mark.anyio
async def test_get_token_returns_none_when_invalid(stack_ready):
    async with SessionLocal() as db:
        t = await crud.get_token(db, uuid4())
        assert t is None


@pytest.mark.anyio
async def test_get_token_by_value(stack_ready, fake: Faker):
    async with SessionLocal() as db:
        uid = uuid4()
        oid = uuid4()
        tok = await crud.create_token(
            db, oid, uid, schemas.TokenCreate(name=fake.name())
        )
        assert tok.id is not None
        assert tok.token is not None
        assert len(tok.token) == 32

        async with SessionLocal() as db:
            t = await crud.get_by_token_value(db, tok.token)
            assert tok.id == t.id


@pytest.mark.anyio
async def test_does_token_belong_to_user(stack_ready, fake: Faker):
    async with SessionLocal() as db:
        uid = uuid4()
        oid = uuid4()
        tok = await crud.create_token(
            db, oid, uid, schemas.TokenCreate(name=fake.name())
        )
        assert tok.id is not None
        assert tok.token is not None
        assert len(tok.token) == 32

        async with SessionLocal() as db:
            t = await crud.does_token_belong_to_user(db, tok.id, uid)
            assert t is True

        async with SessionLocal() as db:
            t = await crud.does_token_belong_to_user(db, uuid4(), uid)
            assert t is False


@pytest.mark.anyio
async def test_revoke_token_does_not_delete_it(stack_ready, fake: Faker):
    async with SessionLocal() as db:
        uid = uuid4()
        oid = uuid4()
        tok = await crud.create_token(
            db, oid, uid, schemas.TokenCreate(name=fake.name())
        )
        assert tok.id is not None
        assert tok.token is not None
        assert len(tok.token) == 32

        async with SessionLocal() as db:
            await crud.revoke_token(db, tok.id)

            async with SessionLocal() as db:
                t = await crud.get_token(db, tok.id)
                assert t is not None
                assert t.revoked is True


@pytest.mark.anyio
async def test_delete_token(stack_ready, fake: Faker):
    async with SessionLocal() as db:
        uid = uuid4()
        oid = uuid4()
        tok = await crud.create_token(
            db, oid, uid, schemas.TokenCreate(name=fake.name())
        )
        assert tok.id is not None
        assert tok.token is not None
        assert len(tok.token) == 32

        async with SessionLocal() as db:
            await crud.delete_token(db, tok.id)

        async with SessionLocal() as db:
            t = await crud.get_token(db, uuid4())
            assert t is None


@pytest.mark.anyio
async def test_count_tokens(stack_ready, fake: Faker):
    async with SessionLocal() as db:
        uid = uuid4()
        oid = uuid4()
        tok = await crud.create_token(
            db, oid, uid, schemas.TokenCreate(name=fake.name())
        )
        assert tok.id is not None
        assert tok.token is not None
        assert len(tok.token) == 32

        async with SessionLocal() as db:
            assert await crud.count_tokens(db, uid) == 1
