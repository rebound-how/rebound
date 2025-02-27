import secrets
from base64 import b64decode, b64encode
from contextlib import contextmanager
from unittest.mock import AsyncMock, patch
from urllib.parse import parse_qs, urlparse

import pytest
import respx
from faker import Faker
from fastapi import FastAPI
from httpx import AsyncClient, Response

from reliably_app import agent
from reliably_app.config import Settings, get_settings
from reliably_app.database import SessionLocal
from reliably_app.login import crud, oauth, service
from reliably_app.login.providers.github import GitHub


@contextmanager
def mock_gcp_calls(with_delete: bool = False) -> None:
    with respx.mock() as respx_mock:

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"  # noqa
        ).mock(return_value=Response(200, json={"access_token": "abc"}))

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id"  # noqa
        ).mock(return_value=Response(200, text="my-project"))

        yield respx_mock


@pytest.mark.anyio
async def test_with_invalid_provider_should_fail(
    client: AsyncClient, fake: Faker
) -> None:
    response = await client.get("/login/with/plain")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_with_unimplemented_provider_should_fail(
    client: AsyncClient, fake: Faker
) -> None:
    try:
        service.OAUTH_PROVIDERS = {"github": GitHub, "gitlab": None}
        response = await client.get("/login/with/gitlab")
        assert response.status_code == 404
    finally:
        service.OAUTH_PROVIDERS = {"github": GitHub}


@pytest.mark.anyio
async def test_should_redirect_to_github(
    client: AsyncClient, fake: Faker
) -> None:
    response = await client.get("/login/with/github", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["content-length"] == "0"

    loc = urlparse(response.headers["location"])
    assert loc.scheme == "https"
    assert loc.netloc == "github.com"
    assert loc.path == "/login/oauth/authorize"

    qs = parse_qs(loc.query, keep_blank_values=True)
    assert qs["response_type"] == ["code"]
    assert "client_id" in qs
    assert qs["client_id"] != [""]
    assert qs["redirect_uri"] == [
        "http://127.0.0.1:8090/login/with/github/authorized"
    ]

    nonce = b64decode(qs["state"][0]).decode("utf-8")
    async with SessionLocal() as db:
        flow = await crud.get_auth_flow(db, "github", nonce)
        assert flow is not None


@pytest.mark.anyio
async def test_auth_with_github_without_a_code_or_idtoken_will_fail(
    client: AsyncClient, fake: Faker
) -> None:
    async with SessionLocal() as db:
        flow = await crud.create_auth_flow(db, "github", {})
        state_hash = str(flow.nonce)

    response = await client.get(
        "/login/with/github/authorized",
        params={"code": "", "state": b64encode(state_hash.encode("utf-8")).decode('utf-8')},
        follow_redirects=False,
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_login_with_github(
    stack_ready, client: AsyncClient, fake: Faker
) -> None:
    gh = oauth.github
    try:
        async with SessionLocal() as db:
            flow = await crud.create_auth_flow(db, "github", {})
            state_hash = str(flow.nonce)

        m = AsyncMock()
        m.authorize_access_token.return_value = {}
        m.userinfo.return_value = {
            "id": "80",
            "name": fake.name(),
            "email": fake.company_email(),
            "login": fake.user_name(),
            "html_url": fake.url(),
            "avatar_url": fake.url(),
            "blog": fake.url(),
        }
        oauth.github = m
        response = await client.get(
            "/login/with/github/authorized",
            params={"code": "xyz", "state": b64encode(state_hash.encode("utf-8")).decode('utf-8')},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "session" in response.cookies
        assert "context" in response.headers["location"]
        loc = response.headers["location"]
        qs = parse_qs(urlparse(loc).query)
        org_id = qs["context"][0]
        response = await client.get(
            f"/api/organization/{org_id}/", cookies=response.cookies
        )
        assert response.status_code == 200, response.json()

        async with SessionLocal() as db:
            flow = await crud.get_auth_flow(db, "github", str(flow.nonce))
            assert flow is None
    finally:
        oauth.github = gh


@pytest.mark.anyio
async def test_register_with_github_creates_org_user_and_internal_agent(
    stack_ready, client: AsyncClient, fake: Faker
) -> None:
    gh = oauth.github
    try:
        async with SessionLocal() as db:
            flow = await crud.create_auth_flow(db, "github", {})
            state_hash = str(flow.nonce)

        m = AsyncMock()
        m.authorize_access_token.return_value = {}
        m.userinfo.return_value = {
            "id": "80",
            "name": fake.name(),
            "email": fake.company_email(),
            "login": fake.user_name(),
            "html_url": fake.url(),
            "avatar_url": fake.url(),
            "blog": fake.url(),
            "family_name": None,
            "given_name": None,
        }
        oauth.github = m
        response = await client.get(
            "/login/with/github/authorized",
            params={"code": "xyz", "state": b64encode(state_hash.encode("utf-8")).decode('utf-8')},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "session" in response.cookies
        assert "context" in response.headers["location"]
        loc = response.headers["location"]
        qs = parse_qs(urlparse(loc).query)
        org_id = qs["context"][0]
        response = await client.get(
            f"/api/organization/{org_id}/", cookies=response.cookies
        )
        assert response.status_code == 200, response.json()

        response = await client.get("/api/me/info", cookies=response.cookies)
        assert response.status_code == 200
        info = response.json()

        user_id = info["profile"]["id"]
        async with SessionLocal() as s:
            a = await agent.crud.get_user_internal_agent(s, org_id, user_id)
            assert a is not None
            assert a.internal is True

    finally:
        oauth.github = gh


@pytest.mark.anyio
async def test_login_with_github_keeps_plan_redirection(
    stack_ready, client: AsyncClient, fake: Faker
) -> None:
    params = {
        "redirect_to": "subscribe",
        "plan": "start"
    }
    response = await client.get("/login/with/github", params=params, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["content-length"] == "0"

    loc = urlparse(response.headers["location"])
    assert loc.scheme == "https"
    assert loc.netloc == "github.com"
    assert loc.path == "/login/oauth/authorize"

    qs = parse_qs(loc.query, keep_blank_values=True)
    assert qs["response_type"] == ["code"]
    assert "client_id" in qs
    assert qs["client_id"] != [""]
    assert qs["redirect_uri"] == [
        "http://127.0.0.1:8090/login/with/github/authorized"
    ]

    nonce = b64decode(qs["state"][0]).decode("utf-8")
    async with SessionLocal() as db:
        flow = await crud.get_auth_flow(db, "github", nonce)
        assert flow is not None

        assert flow.state == {
            "redirect_to": "subscribe",
            "plan": "start"
        }


@pytest.mark.anyio
async def test_login_with_github_does_not_keeps_invalid_plan(
    stack_ready, client: AsyncClient, fake: Faker
) -> None:
    params = {
        "redirect_to": "subscribe",
        "plan": "whatever"
    }
    response = await client.get("/login/with/github", params=params, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["content-length"] == "0"

    loc = urlparse(response.headers["location"])
    assert loc.scheme == "https"
    assert loc.netloc == "github.com"
    assert loc.path == "/login/oauth/authorize"

    qs = parse_qs(loc.query, keep_blank_values=True)
    assert qs["response_type"] == ["code"]
    assert "client_id" in qs
    assert qs["client_id"] != [""]
    assert qs["redirect_uri"] == [
        "http://127.0.0.1:8090/login/with/github/authorized"
    ]

    nonce = b64decode(qs["state"][0]).decode("utf-8")
    async with SessionLocal() as db:
        flow = await crud.get_auth_flow(db, "github", nonce)
        assert flow is not None

        assert flow.state == {}

@pytest.mark.anyio
async def test_login_with_github_keeps_join_hash(
    stack_ready, client: AsyncClient, fake: Faker
) -> None:
    params = {
        "join": "blah"
    }
    response = await client.get("/login/with/github", params=params, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["content-length"] == "0"

    loc = urlparse(response.headers["location"])
    assert loc.scheme == "https"
    assert loc.netloc == "github.com"
    assert loc.path == "/login/oauth/authorize"

    qs = parse_qs(loc.query, keep_blank_values=True)
    assert qs["response_type"] == ["code"]
    assert "client_id" in qs
    assert qs["client_id"] != [""]
    assert qs["redirect_uri"] == [
        "http://127.0.0.1:8090/login/with/github/authorized"
    ]

    nonce = b64decode(qs["state"][0]).decode("utf-8")
    async with SessionLocal() as db:
        flow = await crud.get_auth_flow(db, "github", nonce)
        assert flow is not None

        assert flow.state == {
            "join_hash": "blah"
        }


@pytest.mark.anyio
async def test_register_requires_non_empty_state(
    stack_ready, client: AsyncClient, fake: Faker
) -> None:
    gh = oauth.github
    try:
        m = AsyncMock()
        m.authorize_access_token.return_value = {}
        m.userinfo.return_value = {
            "id": "80",
            "name": fake.name(),
            "email": fake.company_email(),
            "login": fake.user_name(),
            "html_url": fake.url(),
            "avatar_url": fake.url(),
            "blog": fake.url(),
            "family_name": None,
            "given_name": None,
        }
        oauth.github = m
        response = await client.get(
            "/login/with/github/authorized",
            params={"code": "xyz", "state": ""},
            follow_redirects=False,
        )
        assert response.status_code == 400

    finally:
        oauth.github = gh


@pytest.mark.anyio
async def test_register_requires_valid_state(
    stack_ready, client: AsyncClient, fake: Faker
) -> None:
    gh = oauth.github
    try:
        m = AsyncMock()
        m.authorize_access_token.return_value = {}
        m.userinfo.return_value = {
            "id": "80",
            "name": fake.name(),
            "email": fake.company_email(),
            "login": fake.user_name(),
            "html_url": fake.url(),
            "avatar_url": fake.url(),
            "blog": fake.url(),
            "family_name": None,
            "given_name": None,
        }
        oauth.github = m
        response = await client.get(
            "/login/with/github/authorized",
            params={"code": "xyz", "state": "bloop"},
            follow_redirects=False,
        )
        assert response.status_code == 400

    finally:
        oauth.github = gh


@pytest.mark.anyio
async def test_register_unknown_state(
    stack_ready, client: AsyncClient, fake: Faker
) -> None:
    gh = oauth.github
    try:
        m = AsyncMock()
        m.authorize_access_token.return_value = {}
        m.userinfo.return_value = {
            "id": "80",
            "name": fake.name(),
            "email": fake.company_email(),
            "login": fake.user_name(),
            "html_url": fake.url(),
            "avatar_url": fake.url(),
            "blog": fake.url(),
            "family_name": None,
            "given_name": None,
        }
        oauth.github = m
        response = await client.get(
            "/login/with/github/authorized",
            params={"code": "xyz", "state": b64encode(b"hello").decode("utf-8")},
            follow_redirects=False,
        )
        assert response.status_code == 400

    finally:
        oauth.github = gh


@pytest.mark.anyio
async def test_register_via_email(
    stack_ready,  application: FastAPI, client: AsyncClient, fake: Faker, settings: Settings,
) -> None:
    with patch("reliably_app.login.tasks.get_settings", autospec=True) as m:
        with patch("reliably_app.organization.tasks.get_settings", autospec=True) as t:
            settings = settings.model_copy(deep=True)
            settings.FEATURE_CLOUD_DEPLOYMENT = False
            settings.DEPLOYMENT_STRATEGY = "local"

            m.return_value = settings
            t.return_value = settings

            application.dependency_overrides[get_settings] = lambda: settings
            response = await client.post(
                "/login/with/email",
                json={"email": fake.email(), "password": secrets.token_hex(4), "register": True}
            )
            assert response.status_code == 200
            r = response.json()

            org_id = r["context"]
            response = await client.get(
                f"/api/organization/{org_id}/", cookies=response.cookies
            )
            assert response.status_code == 200, response.json()

            response = await client.get("/api/me/info", cookies=response.cookies)
            assert response.status_code == 200
            info = response.json()

            user_id = info["profile"]["id"]
            async with SessionLocal() as s:
                a = await agent.crud.get_user_internal_agent(s, org_id, user_id)
                assert a is not None
                assert a.internal is True


@pytest.mark.anyio
async def test_login_via_email_fails_when_password_is_invalid(
    stack_ready, client: AsyncClient, fake: Faker
) -> None:
    email = fake.email()

    response = await client.post(
        "/login/with/email",
        json={"email": email, "password": secrets.token_hex(4)}
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_register_via_email_long_enough(
    stack_ready, client: AsyncClient, fake: Faker
) -> None:
    response = await client.post(
        "/login/with/email",
        json={"email": "s@", "password": secrets.token_hex(4)}
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_register_via_email_with_password_long_enough(
    stack_ready, client: AsyncClient, fake: Faker
) -> None:
    response = await client.post(
        "/login/with/email",
        json={"email": fake.email(), "password": "meh"}
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_register_via_email_fail_when_feature_disabled(
    stack_ready, client: AsyncClient, fake: Faker, settings: Settings
) -> None:
    settings.FEATURE_LOGIN_EMAIL = False

    with patch("reliably_app.flags.get_settings", autospec=True) as m:
        m.return_value = settings
        response = await client.post(
            "/login/with/email",
            json={"email": fake.email(), "password": "meh12324456"}
        )
        assert response.status_code == 404
