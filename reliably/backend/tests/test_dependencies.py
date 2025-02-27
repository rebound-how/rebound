from uuid import uuid4

import pytest
from authlib.oidc.core import UserInfo
from faker import Faker
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import InvalidRequestError
from starlette.requests import Request

from reliably_app import account, agent, token
from reliably_app.database import SessionLocal
from reliably_app.dependencies.auth import (
    validate_auth,
    with_admin_user,
    with_user,
    with_user_in_org,
)
from reliably_app.dependencies.database import get_db
from reliably_app.dependencies.org import valid_org
from reliably_app.dependencies.scope import valid_in_scope


@pytest.mark.anyio
async def test_session_closes_transaction_on_closing(stack_ready):
    g = get_db()
    session = await anext(g)
    assert session.in_transaction()

    await g.aclose()
    assert not session.in_transaction()


@pytest.mark.anyio
async def test_session_cannot_be_reused_after_first_commit(stack_ready):
    g = get_db()
    session = await anext(g)
    await session.commit()

    with pytest.raises(InvalidRequestError):
        await session.execute(text("select 1;"))


@pytest.mark.anyio
async def test_validate_auth_requires_at_least_authorization_header_or_session_cookie(  # noqa
    stack_ready,
):
    scope = {
        "client": ("127.0.0.1", "8090"),
        "type": "http",
        "path": "/api/v1/organization",
        "headers": [],
    }

    r = Request(scope)

    with pytest.raises(HTTPException) as x:
        async with SessionLocal() as db:
            await validate_auth(r, authorization=None, user_id=None, db=db)

    assert x.value.detail == "Unauthorized"


@pytest.mark.anyio
async def test_validate_auth_requires_the_authorization_header_on_api_calls(
    stack_ready,
):
    scope = {
        "client": ("127.0.0.1", "8090"),
        "type": "http",
        "path": "/api/v1/organization",
        "headers": [("Host", "127.0.0.1:8090")],
    }

    r = Request(scope)

    with pytest.raises(HTTPException) as x:
        async with SessionLocal() as db:
            await validate_auth(r, authorization=None, user_id="xyz", db=db)

    assert x.value.detail == "Unauthorized"


@pytest.mark.anyio
async def test_validate_auth_requires_the_authorization_header_to_be_bearer_token(  # noqa
    stack_ready,
):
    scope = {
        "client": ("127.0.0.1", "8090"),
        "type": "http",
        "path": "/api/v1/organization",
        "headers": [],
    }

    r = Request(scope)

    with pytest.raises(HTTPException) as x:
        async with SessionLocal() as db:
            await validate_auth(
                r, authorization="basic xyz", user_id=None, db=db
            )

    assert x.value.detail == "Unauthorized"


@pytest.mark.anyio
async def test_validate_auth_requires_the_authorization_header_to_utf_8_encoded(
    stack_ready,
):
    scope = {
        "client": ("127.0.0.1", "8090"),
        "type": "http",
        "path": "/api/v1/organization",
        "headers": [],
    }

    r = Request(scope)

    with pytest.raises(HTTPException) as x:
        async with SessionLocal() as db:
            await validate_auth(
                r, authorization="bearer \ud800", user_id=None, db=db
            )

    assert x.value.detail == "Unauthorized"


@pytest.mark.anyio
async def test_validate_auth_token_must_be_32_characters(
    stack_ready,
):
    scope = {
        "client": ("127.0.0.1", "8090"),
        "type": "http",
        "path": "/api/v1/organization",
        "headers": [],
    }

    r = Request(scope)

    with pytest.raises(HTTPException) as x:
        async with SessionLocal() as db:
            await validate_auth(
                r, authorization="bearer xyz", user_id=None, db=db
            )

    assert x.value.detail == "Unauthorized"


@pytest.mark.anyio
async def test_validate_auth_requires_the_authorization_token_to_exist(
    stack_ready, authed
):
    scope = {
        "client": ("127.0.0.1", "8090"),
        "type": "http",
        "path": "/api/v1/organization",
        "headers": [],
    }

    r = Request(scope)

    authed_org, authed_user, _ = authed
    token_input = token.schemas.TokenCreate(name="hey")
    async with SessionLocal() as db:
        tok = await token.crud.create_token(
            db, authed_org.id, authed_user.id, token_input
        )
        tok_id = tok.id
        token_value = tok.token.decode("utf-8")

    async with SessionLocal() as db:
        oid, uid, tid = await validate_auth(
            r, authorization=f"bearer {token_value}", user_id=None, db=db
        )
        assert oid == authed_org.id
        assert uid == authed_user.id
        assert tid == tok_id


@pytest.mark.anyio
async def test_validate_auth_requires_the_authorization_token_to_not_be_revoked(
    stack_ready, authed
):
    scope = {
        "client": ("127.0.0.1", "8090"),
        "type": "http",
        "path": "/api/v1/organization",
        "headers": [],
    }

    r = Request(scope)

    authed_org, authed_user, _ = authed
    token_input = token.schemas.TokenCreate(name="hey")
    async with SessionLocal() as db:
        tok = await token.crud.create_token(
            db, authed_org.id, authed_user.id, token_input
        )
        tok_id = tok.id
        token_value = tok.token.decode("utf-8")

    async with SessionLocal() as db:
        await token.crud.revoke_token(db, tok_id)

    with pytest.raises(HTTPException):
        async with SessionLocal() as db:
            await validate_auth(
                r, authorization=f"bearer {token_value}", user_id=None, db=db
            )


@pytest.mark.anyio
async def test_validate_session_used_for_non_api_calls(stack_ready, authed):
    scope = {
        "client": ("127.0.0.1", "8090"),
        "type": "http",
        "path": "/organization",
        "headers": [],
    }

    r = Request(scope)

    with pytest.raises(HTTPException) as x:
        async with SessionLocal() as db:
            await validate_auth(
                r, authorization="bearer xyz", user_id=None, db=db
            )

    assert x.value.detail == "Unauthorized"


@pytest.mark.anyio
async def test_valid_session_returns_user_id(stack_ready, authed):
    scope = {
        "client": ("127.0.0.1", "8090"),
        "type": "http",
        "path": "/organization",
        "headers": [],
    }

    r = Request(scope)

    async with SessionLocal() as db:
        _, user_id, _ = await validate_auth(
            r, authorization=None, user_id="xyz", db=db
        )
        assert user_id == "xyz"


@pytest.mark.anyio
async def test_validate_auth_may_not_ve_valid(stack_ready, authed):
    scope = {
        "client": ("127.0.0.1", "8090"),
        "type": "http",
        "path": "/api/v1/organization",
        "headers": [],
    }

    r = Request(scope)

    with pytest.raises(HTTPException):
        async with SessionLocal() as db:
            await validate_auth(
                r, authorization="bearer xyz", user_id=None, db=db
            )


@pytest.mark.anyio
async def test_valid_org_with_an_existing_org(stack_ready, authed):
    authed_org, _, _ = authed
    async with SessionLocal() as db:
        org = await valid_org(authed_org.id, db)
        assert org.id == authed_org.id


@pytest.mark.anyio
async def test_valid_org_with_an_invalid_org(stack_ready, authed):
    with pytest.raises(HTTPException):
        async with SessionLocal() as db:
            await valid_org(uuid4(), db)


@pytest.mark.anyio
async def test_get_authed_user_for_api(stack_ready, authed):
    authed_org, authed_user, authed_token = authed

    async with SessionLocal() as db:
        user = await with_user_in_org(
            (authed_org.id, authed_user.id, authed_token.id), authed_org, db
        )
        assert user.id == authed_user.id


@pytest.mark.anyio
async def test_get_authed_user_for_session(stack_ready, authed):
    authed_org, authed_user, _ = authed
    async with SessionLocal() as db:
        user = await with_user_in_org(
            (None, authed_user.id, None), authed_org, db
        )
        assert user.id == authed_user.id


@pytest.mark.anyio
async def test_get_authed_user_fails_when_user_does_not_belong_to_org(
    stack_ready, authed, fake: Faker
):
    authed_org, _, _ = authed
    u = account.schemas.UserCreate(
        username=fake.name(),
        email=fake.company_email(),
        openid=UserInfo({"sub": "xyz"}),
    )

    async with SessionLocal() as db:
        user = await account.crud.create_user(db, u)

    with pytest.raises(HTTPException) as x:
        async with SessionLocal() as db:
            user = await with_user_in_org((None, user.id, None), authed_org, db)
    assert x.value.status_code == 403


@pytest.mark.anyio
async def test_get_authed_user_fails_when_user_invalid(
    stack_ready, authed, fake: Faker
):
    authed_org, _, _ = authed

    with pytest.raises(HTTPException) as x:
        async with SessionLocal() as db:
            await with_user_in_org((None, uuid4(), None), authed_org, db)
    assert x.value.status_code == 403


@pytest.mark.anyio
async def test_get_admin_user_fails_when_user_invalid(
    stack_ready, authed, fake: Faker
):
    with pytest.raises(HTTPException) as x:
        async with SessionLocal() as db:
            await with_admin_user((None, uuid4(), None), db)
    assert x.value.status_code == 401


@pytest.mark.anyio
async def test_get_admin_user(stack_ready, authed, fake: Faker):
    _, authed_user, _ = authed

    async with SessionLocal() as db:
        user = await with_admin_user((None, authed_user.id, None), db)
        assert user.id == authed_user.id


@pytest.mark.anyio
async def test_get_user(stack_ready, authed, fake: Faker):
    _, authed_user, _ = authed

    async with SessionLocal() as db:
        user = await with_user((None, authed_user.id, None), db)
        assert user.id == authed_user.id


@pytest.mark.anyio
async def test_get_user_not_found(stack_ready, authed, fake: Faker):
    with pytest.raises(HTTPException):
        async with SessionLocal() as db:
            await with_user((None, str(uuid4()), None), db)


@pytest.mark.anyio
async def test_requires_agent_in_scope(stack_ready, authed, fake: Faker):
    authed_org, _, _ = authed

    u = account.schemas.UserCreate(
        username=fake.name(),
        email=fake.company_email(),
        openid=UserInfo({"sub": "xyz"}),
        as_agent=True,
    )

    async with SessionLocal() as db:
        user = await account.crud.create_user(db, u)

    token_input = token.schemas.TokenCreate(name="hey")
    async with SessionLocal() as db:
        tok = await token.crud.create_token(
            db, authed_org.id, user.id, token_input
        )
        tok_id = tok.id

    ac = agent.schemas.AgentCreate(
        user_id=str(user.id), token_id=str(tok_id), sub="xyz"
    )

    async with SessionLocal() as db:
        await agent.crud.create_agent(db, authed_org.id, ac, user.id)

    with pytest.raises(HTTPException) as x:
        user = await valid_in_scope(user)
    assert x.value.status_code == 403

    assert valid_in_scope(user, scopes=("user", "agent")) is user
