import secrets
import uuid

import pytest
from faker import Faker
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_deployment(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()
    repo = "https://github.com/my/repo"
    gh_dep_name = fake.name()
    token = secrets.token_hex(16)

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "name": gh_dep_name,
                "token": token,
            },
        },
    )
    assert response.status_code == 201, response.json()
    dep = response.json()
    assert "id" in dep
    assert dep["org_id"] == str(authed_org.id)


@pytest.mark.anyio
async def test_get_deployment_return_secrets_opaqued(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()
    repo = "https://github.com/my/repo"
    gh_dep_name = fake.name()
    token = secrets.token_hex(16)

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "name": gh_dep_name,
                "token": token,
            },
        },
    )
    assert response.status_code == 201
    dep = response.json()
    assert "id" in dep
    assert dep["org_id"] == str(authed_org.id)

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/deployments/{dep['id']}",
        headers=headers,
    )
    assert response.json()["definition"]["token"] == "**********"


@pytest.mark.anyio
async def test_create_deployment_with_a_used_name_will_fail(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()
    repo = "https://github.com/my/repo"
    gh_dep_name = fake.name()
    token = secrets.token_hex(16)

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "name": gh_dep_name,
                "token": token,
            },
        },
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "name": gh_dep_name,
                "token": token,
            },
        },
    )
    assert response.status_code == 409


@pytest.mark.anyio
async def test_delete_deployment(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()
    repo = "https://github.com/my/repo"
    gh_dep_name = fake.name()
    token = secrets.token_hex(16)

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "name": gh_dep_name,
                "token": token,
            },
        },
    )
    assert response.status_code == 201
    d = response.json()
    dep_id = d["id"]

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/deployments/{dep_id}",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/deployments/{dep_id}",
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_cannot_get_deployment_from_another_org(
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

    name = fake.name()
    repo = "https://github.com/my/repo"
    gh_dep_name = fake.name()
    token = secrets.token_hex(16)

    response = await client.post(
        f"/api/v1/organization/{org['id']}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "name": gh_dep_name,
                "token": token,
            },
        },
    )
    assert response.status_code == 201
    d = response.json()
    dep_id = d["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/deployments/{dep_id}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.get(
        f"/api/v1/organization/{org['id']}/deployments/{dep_id}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_cannot_delete_deployment_from_another_org(
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

    name = fake.name()
    repo = "https://github.com/my/repo"
    gh_dep_name = fake.name()
    token = secrets.token_hex(16)

    response = await client.post(
        f"/api/v1/organization/{org['id']}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "name": gh_dep_name,
                "token": token,
            },
        },
    )
    assert response.status_code == 201
    d = response.json()
    dep_id = d["id"]

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/deployments/{dep_id}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.delete(
        f"/api/v1/organization/{org['id']}/deployments/{dep_id}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_list_deployments(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()
    repo = "https://github.com/my/repo"
    gh_dep_name = fake.name()
    token = secrets.token_hex(16)

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "name": gh_dep_name,
                "token": token,
            },
        },
    )
    assert response.status_code == 201
    d = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
    )
    assert response.status_code == 200
    deps = response.json()

    assert deps["count"] == 2
    assert len(deps["items"]) == 2
    assert deps["items"][1]["id"] == d["id"]


@pytest.mark.anyio
async def test_paginate_deploymens(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()
    repo = "https://github.com/my/repo"
    gh_dep_name = fake.name()
    token = secrets.token_hex(16)

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "name": gh_dep_name,
                "token": token,
            },
        },
    )
    assert response.status_code == 201

    name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "name": gh_dep_name,
                "token": token,
            },
        },
    )
    assert response.status_code == 201

    name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "name": gh_dep_name,
                "token": token,
            },
        },
    )
    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        params={"limit": 1},
    )
    assert response.status_code == 200, response.json()
    deployments = response.json()

    assert deployments["count"] == 4
    assert len(deployments["items"]) == 1

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/deployments?page=2",
        headers=headers,
    )
    assert response.status_code == 200
    deployments = response.json()

    assert deployments["count"] == 4
    assert len(deployments["items"]) == 0


@pytest.mark.anyio
async def test_deployment_page_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/deployments?page=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_deployment_limit_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/deployments?limit=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_deployment_limit_cannot_be_greater_than_10(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/deployments?limit=20",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_deployment_plans(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep = response.json()
    assert "id" in dep
    assert dep["org_id"] == str(authed_org.id)

    dep_id = dep["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201
    plan = response.json()
    plan_id = plan["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/deployments/{dep_id}/plans",
        headers=headers,
    )
    assert response.status_code == 200
    plan_ids = response.json()
    assert [plan_id] == plan_ids


@pytest.mark.anyio
async def test_cannot_delete_deployment_if_used_by_plan(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep = response.json()
    assert "id" in dep
    assert dep["org_id"] == str(authed_org.id)

    dep_id = dep["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201
    plan = response.json()
    plan_id = plan["id"]

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/deployments/{dep_id}",
        headers=headers,
    )
    assert response.status_code == 400
    error = response.json()
    assert error["status"] == 400
    assert error["title"] == "deployment is used by at least another plan"

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/deployments/{dep_id}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_update_deployment(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()
    repo = "https://github.com/my/repo"
    username = fake.name()
    token = secrets.token_hex(16)

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "username": username,
                "token": token,
            },
        },
    )
    assert response.status_code == 201
    d = response.json()
    dep_id = d["id"]

    name = fake.name()
    repo = "https://github.com/my/repo2"
    token = secrets.token_hex(16)

    response = await client.put(
        f"/api/v1/organization/{str(authed_org.id)}/deployments/{dep_id}",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "username": username,
                "token": token,
            }
        }
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/deployments/{dep_id}",
        headers=headers,
    )
    nd = response.json()

    assert response.status_code == 200
    assert d["id"] == nd["id"]
    assert d["name"] != nd["name"]
    assert d["definition"] != nd["definition"]
    assert nd["name"] == name
    assert nd["definition"]["type"] == "github"
    assert nd["definition"]["repo"] == repo
    assert nd["definition"]["username"] == username


@pytest.mark.anyio
async def test_clone_deployment(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()
    repo = "https://github.com/my/repo"
    username = fake.name()
    token = secrets.token_hex(16)

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "username": username,
                "token": token,
            },
        },
    )
    assert response.status_code == 201
    d = response.json()
    dep_id = d["id"]

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments/{dep_id}/clone",
        headers=headers,
        json={
            "name": name,
        }
    )
    assert response.status_code == 201
    nd = response.json()

    assert d["id"] != nd["id"]
    assert d["name"] != nd["name"]
    assert d["definition"] == nd["definition"]
    assert nd["name"] == name
    assert nd["definition"]["type"] == "github"
    assert nd["definition"]["repo"] == repo
    assert nd["definition"]["username"] == username


@pytest.mark.anyio
async def test_clone_deployment_fails_with_conflict(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()
    repo = "https://github.com/my/repo"
    username = fake.name()
    token = secrets.token_hex(16)

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "username": username,
                "token": token,
            },
        },
    )
    assert response.status_code == 201
    d = response.json()
    dep_id = d["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments/{dep_id}/clone",
        headers=headers,
        json={
            "name": name,
        }
    )
    assert response.status_code == 409


@pytest.mark.anyio
async def test_search_by_name(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()
    repo = "https://github.com/my/repo"
    username = fake.name()
    token = secrets.token_hex(16)

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": name,
            "definition": {
                "type": "github",
                "repo": repo,
                "username": username,
                "token": token,
            },
        },
    )
    assert response.status_code == 201
    d = response.json()


    pattern = name[2:5]
    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/deployments/search",
        headers=headers,
        params={
            "pattern": pattern,
        }
    )
    assert response.status_code == 200

    items = response.json()

    assert items["count"] == 1
    assert items["items"][0]["id"] == d["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/deployments/search",
        headers=headers,
        params={
            "pattern": "5678",
        }
    )
    assert response.status_code == 200
    items = response.json()
    assert items["count"] == 0