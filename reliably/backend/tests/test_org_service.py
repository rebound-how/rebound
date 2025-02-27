from uuid import uuid4

import pytest
from faker import Faker
from httpx import AsyncClient

from reliably_app import account
from reliably_app.database import SessionLocal


@pytest.mark.anyio
async def test_get_organizations_of_an_user(
    client: AsyncClient, fake: Faker
) -> None:
    pass


@pytest.mark.anyio
async def test_get_org_returns_a_single_org(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    _, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.company()
    response = await client.post(
        "/api/v1/organization", json={"name": name}, headers=headers
    )
    assert response.status_code == 201
    org = response.json()

    response = await client.get(
        f"/api/v1/organization/{org['id']}/", headers=headers
    )
    assert response.status_code == 200

    o = response.json()
    assert o["id"] == org["id"]
    assert o["name"] == org["name"]


@pytest.mark.anyio
async def test_cannot_add_a_user_more_than_once_in_an_org(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    _, authed_user, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.company()
    response = await client.post(
        "/api/v1/organization", json={"name": name}, headers=headers
    )
    assert response.status_code == 201, response.json()
    org = response.json()

    response = await client.post(
        f"/api/v1/organization/{org['id']}/users",
        json={"user_id": str(authed_user.id)},
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{org['id']}/users", headers=headers
    )
    assert response.status_code == 200
    users = response.json()
    assert users["count"] == 1
    assert len(users["items"]) == 1


@pytest.mark.anyio
async def test_cannot_create_two_orgs_with_same_name(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    _, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    company = fake.company()
    response = await client.post(
        "/api/v1/organization", json={"name": company}, headers=headers
    )
    assert response.status_code == 201

    response = await client.post(
        "/api/v1/organization", json={"name": company}, headers=headers
    )
    assert response.status_code == 201
    assert response.json()["name"] != company
    assert response.json()["name"].startswith(company)


@pytest.mark.anyio
async def test_org_not_found_returns_404(
    client: AsyncClient, authed: None
) -> None:
    _, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{uuid4()}/", headers=headers
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_can_add_and_remove_users_to_an_organization(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    _, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.company()
    response = await client.post(
        "/api/v1/organization", json={"name": name}, headers=headers
    )
    assert response.status_code == 201
    org = response.json()

    username = fake.name()
    email = fake.company_email()

    async with SessionLocal() as db:
        user = await account.crud.create_user(
            db, account.schemas.UserCreate(username=username, email=email)
        )
        user_id = str(user.id)

    response = await client.post(
        f"/api/v1/organization/{org['id']}/users",
        json={"user_id": user_id},
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{org['id']}/users", headers=headers
    )
    assert response.status_code == 200
    users = response.json()
    assert users["count"] == 2
    assert len(users["items"]) == 2

    response = await client.delete(
        f"/api/v1/organization/{org['id']}/users/{user_id}", headers=headers
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{org['id']}/users", headers=headers
    )
    assert response.status_code == 200
    users = response.json()
    assert users["count"] == 1
    assert len(users["items"]) == 1


@pytest.mark.anyio
async def test_paginate_org_users(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    _, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.company()
    response = await client.post(
        "/api/v1/organization", json={"name": name}, headers=headers
    )
    assert response.status_code == 201
    org = response.json()

    username = fake.name()
    email = fake.company_email()

    async with SessionLocal() as db:
        user = await account.crud.create_user(
            db, account.schemas.UserCreate(username=username, email=email)
        )
        user_id = str(user.id)

    response = await client.post(
        f"/api/v1/organization/{org['id']}/users",
        json={"user_id": user_id},
        headers=headers,
    )
    assert response.status_code == 200

    username = fake.name()
    email = fake.company_email()

    async with SessionLocal() as db:
        user = await account.crud.create_user(
            db, account.schemas.UserCreate(username=username, email=email)
        )
        user_id = str(user.id)

    response = await client.post(
        f"/api/v1/organization/{org['id']}/users",
        json={"user_id": user_id},
        headers=headers,
    )
    assert response.status_code == 200

    username = fake.name()
    email = fake.company_email()

    async with SessionLocal() as db:
        user = await account.crud.create_user(
            db, account.schemas.UserCreate(username=username, email=email)
        )
        user_id = str(user.id)

    response = await client.post(
        f"/api/v1/organization/{org['id']}/users",
        json={"user_id": user_id},
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{org['id']}/users?limit=1", headers=headers
    )
    assert response.status_code == 200
    users = response.json()
    assert users["count"] == 4
    assert len(users["items"]) == 1

    response = await client.get(
        f"/api/v1/organization/{org['id']}/users?page=2", headers=headers
    )
    assert response.status_code == 200
    users = response.json()
    assert users["count"] == 4
    assert len(users["items"]) == 3

    response = await client.get(
        f"/api/v1/organization/{org['id']}/users?page=2&limit=2",
        headers=headers,
    )
    assert response.status_code == 200
    users = response.json()
    assert users["count"] == 4
    assert len(users["items"]) == 2
