import uuid

import pytest
from faker import Faker
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_agent(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201
    agent = response.json()
    assert "id" in agent


@pytest.mark.anyio
async def test_cannot_get_invalid_agent(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/agents/{str(uuid.uuid4())}",
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_list_agents(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201
    agent = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 200
    agents = response.json()

    assert agents["count"] == 1
    assert len(agents["items"]) == 1
    assert agents["items"][0]["id"] == agent["id"]


@pytest.mark.anyio
async def test_paginate_agents(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
        params={"limit": 1},
    )
    assert response.status_code == 200, response.json()
    agents = response.json()

    assert agents["count"] == 3
    assert len(agents["items"]) == 1

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/agents?page=2",
        headers=headers,
    )
    assert response.status_code == 200
    agents = response.json()

    assert agents["count"] == 3
    assert len(agents["items"]) == 0


@pytest.mark.anyio
async def test_delete_agent(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201
    agent = response.json()
    agent_id = agent["id"]

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/agents/{agent_id}",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/agents/{agent_id}",
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_cannot_get_agent_from_another_org(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.company()
    response = await client.post(
        "/api/v1/organization", json={"name": name}, headers=headers
    )
    assert response.status_code == 201
    org = response.json()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201
    agent = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(org['id'])}/agents/{agent['id']}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/agents/{agent['id']}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_cannot_delete_agent_from_another_org(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.company()
    response = await client.post(
        "/api/v1/organization", json={"name": name}, headers=headers
    )
    assert response.status_code == 201
    org = response.json()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201
    agent = response.json()

    response = await client.delete(
        f"/api/v1/organization/{str(org['id'])}/agents/{agent['id']}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/agents/{agent['id']}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_agent_page_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/agents?page=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_agent_limit_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/agents?limit=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_agent_limit_cannot_be_greater_than_10(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/agents?limit=20",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_set_agent_state(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201
    agent = response.json()
    agent_id = agent["id"]

    for s in ("running",):
        response = await client.put(
            f"/api/v1/organization/{str(authed_org.id)}/agents/{agent_id}/state",  # noqa
            headers=headers,
            json={"status": s},
        )
        assert response.status_code == 200, response.json()

        response = await client.get(
            f"/api/v1/organization/{str(authed_org.id)}/agents/{agent_id}",
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["state"]["status"] == s
