from uuid import uuid4

import pytest
from faker import Faker
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_users_returns_a_list_of_users(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    _, authed_user, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get("/api/v1/user", headers=headers)
    assert response.status_code == 200

    users = response.json()
    assert users["count"] == 1
    assert len(users["items"]) == 1
    assert users["items"][0]["email"] == authed_user.email
    assert users["items"][0]["username"] == authed_user.username


@pytest.mark.anyio
async def test_get_user_returns_a_single_user(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    _, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    username = fake.name()
    email = fake.company_email()
    response = await client.post(
        "/api/v1/user",
        json={"username": username, "email": email, "openid": {"sub": "xyz"}},
        headers=headers,
    )
    assert response.status_code == 201, response.json()
    user = response.json()

    response = await client.get(f"/api/v1/user/{user['id']}", headers=headers)
    assert response.status_code == 200

    u = response.json()
    assert u["id"] == user["id"]
    assert u["username"] == user["username"]
    assert u["email"] == user["email"]


@pytest.mark.anyio
async def test_can_create_two_users_with_same_email(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    _, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    username = fake.name()
    email = fake.company_email()
    response = await client.post(
        "/api/v1/user",
        json={"username": username, "email": email, "openid": {"sub": "xyz"}},
        headers=headers,
    )
    assert response.status_code == 201

    username = fake.name()
    response = await client.post(
        "/api/v1/user",
        json={"username": username, "email": email, "openid": {"sub": "abc"}},
        headers=headers,
    )
    assert response.status_code == 201


@pytest.mark.anyio
async def test_cannot_create_two_users_with_same_username(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    _, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    username = fake.name()
    email = fake.company_email()
    response = await client.post(
        "/api/v1/user",
        json={"username": username, "email": email, "openid": {"sub": "xyz"}},
        headers=headers,
    )
    assert response.status_code == 201

    email = fake.company_email()
    response = await client.post(
        "/api/v1/user",
        json={"username": username, "email": email, "openid": {"sub": "xyz"}},
        headers=headers,
    )
    assert response.status_code == 409


@pytest.mark.anyio
async def test_user_not_found_returns_404(
    client: AsyncClient, authed: None
) -> None:
    _, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(f"/api/v1/user/{uuid4()}", headers=headers)
    assert response.status_code == 404


@pytest.mark.anyio
async def test_paginate_users(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    _, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    username = fake.name()
    email = fake.company_email()
    response = await client.post(
        "/api/v1/user",
        json={"username": username, "email": email, "openid": {"sub": "xyz"}},
        headers=headers,
    )
    assert response.status_code == 201

    username = fake.name()
    email = fake.company_email()
    response = await client.post(
        "/api/v1/user",
        json={"username": username, "email": email, "openid": {"sub": "abc"}},
        headers=headers,
    )
    assert response.status_code == 201

    username = fake.name()
    email = fake.company_email()
    response = await client.post(
        "/api/v1/user",
        json={"username": username, "email": email, "openid": {"sub": "def"}},
        headers=headers,
    )
    assert response.status_code == 201

    response = await client.get("/api/v1/user?limit=1", headers=headers)
    assert response.status_code == 200

    r = response.json()
    assert r["count"] == 4
    assert len(r["items"]) == 1

    response = await client.get("/api/v1/user?page=2", headers=headers)
    assert response.status_code == 200

    r = response.json()
    assert r["count"] == 4
    assert len(r["items"]) == 3
