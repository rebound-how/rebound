import pytest
from faker import Faker
from httpx import AsyncClient

from reliably_app import token
from reliably_app.database import SessionLocal


@pytest.mark.anyio
async def test_create_token(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/tokens",
        headers=headers,
        json={"name": name},
    )
    assert response.status_code == 201
    token = response.json()
    token["id"] == authed_token.id
    token["name"] == authed_token.name
    token["token"] == authed_token.token.decode("utf-8")


@pytest.mark.anyio
async def test_create_token_with_a_used_name_will_fail(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/tokens",
        headers=headers,
        json={"name": name},
    )
    assert response.status_code == 201
    token = response.json()
    token["id"] == authed_token.id
    token["name"] == authed_token.name
    token["token"] == authed_token.token.decode("utf-8")

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/tokens",
        headers=headers,
        json={"name": name},
    )
    assert response.status_code == 409


@pytest.mark.anyio
async def test_get_user_tokens(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/tokens", headers=headers
    )
    assert response.status_code == 200
    tokens = response.json()

    assert tokens["count"] == 1
    assert len(tokens["items"]) == 1
    tokens["items"][0]["id"] == authed_token.id
    tokens["items"][0]["name"] == authed_token.name
    tokens["items"][0]["token"] == authed_token.token.decode("utf-8")


@pytest.mark.anyio
async def test_get_user_token(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/tokens/{str(authed_token.id)}",  # noqa
        headers=headers,
    )
    assert response.status_code == 200
    tokens = response.json()
    tokens["id"] == authed_token.id
    tokens["name"] == authed_token.name
    tokens["token"] == authed_token.token.decode("utf-8")


@pytest.mark.anyio
async def test_delete_user_token(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/tokens/{str(authed_token.id)}",  # noqa
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/tokens/{str(authed_token.id)}",  # noqa
        headers=headers,
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_cannot_get_token_from_someone_else_in_your_org(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    username = fake.name()
    email = fake.company_email()
    response = await client.post(
        "/api/v1/user",
        json={"username": username, "email": email, "openid": {"sub": "xyz"}},
        headers=headers,
    )
    assert response.status_code == 201
    user = response.json()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/users",
        headers=headers,
        json={"user_id": user["id"]},
    )
    assert response.status_code == 200

    async with SessionLocal() as db:
        t = token.schemas.TokenCreate(name="hey")
        new_token = await token.crud.create_token(
            db, authed_org.id, user["id"], t
        )
        new_token_value = new_token.token.decode("utf-8")

    headers = {"Authorization": f"Bearer {new_token_value}"}
    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/tokens/{str(authed_token.id)}",  # noqa
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_cannot_delete_token_from_someone_else_in_your_org(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    username = fake.name()
    email = fake.company_email()
    response = await client.post(
        "/api/v1/user",
        json={"username": username, "email": email, "openid": {"sub": "xyz"}},
        headers=headers,
    )
    assert response.status_code == 201
    user = response.json()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/users",
        headers=headers,
        json={"user_id": user["id"]},
    )
    assert response.status_code == 200

    async with SessionLocal() as db:
        t = token.schemas.TokenCreate(name="hey")
        new_token = await token.crud.create_token(
            db, authed_org.id, user["id"], t
        )
        new_token_value = new_token.token.decode("utf-8")

    headers = {"Authorization": f"Bearer {new_token_value}"}
    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/tokens/{str(authed_token.id)}",  # noqa
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_token_page_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/tokens?page=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_token_limit_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/tokens?limit=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_token_limit_cannot_be_greater_than_10(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/tokens?limit=20",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_paginate_tokens(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/tokens",
        headers=headers,
        json={"name": name},
    )
    assert response.status_code == 201

    name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/tokens",
        headers=headers,
        json={"name": name},
    )
    assert response.status_code == 201

    name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/tokens",
        headers=headers,
        json={"name": name},
    )
    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/tokens?limit=1",
        headers=headers,
    )
    assert response.status_code == 200, response.json()
    tokens = response.json()

    assert tokens["count"] == 4
    assert len(tokens["items"]) == 1

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/tokens?page=2",
        headers=headers,
    )
    assert response.status_code == 200, response.json()
    tokens = response.json()

    assert tokens["count"] == 4
    assert len(tokens["items"]) == 3

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/tokens?page=2&limit=2",
        headers=headers,
    )
    assert response.status_code == 200, response.json()
    tokens = response.json()

    assert tokens["count"] == 4
    assert len(tokens["items"]) == 2
