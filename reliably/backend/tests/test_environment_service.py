import re
import uuid
from contextlib import contextmanager

import pytest
import respx
from faker import Faker
from httpx import AsyncClient, Response


@pytest.mark.anyio
async def test_create_environment(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201
    env = response.json()
    assert "id" in env
    assert env["org_id"] == str(authed_org.id)


@pytest.mark.anyio
async def test_get_environment_return_secrets_in_plaintext(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201
    env = response.json()
    assert "id" in env
    assert env["org_id"] == str(authed_org.id)

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env['id']}",
        headers=headers,
    )
    resp = response.json()
    assert resp["envvars"] == [{"var_name": "MY_VAR", "value": "hi"}]
    assert len(resp["secrets"]) == 1


@pytest.mark.anyio
async def test_delete_environment(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201
    d = response.json()
    env_id = d["id"]

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}",
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_cannot_get_environment_from_another_org(
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

    response = await client.post(
        f"/api/v1/organization/{org['id']}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201
    d = response.json()
    env_id = d["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.get(
        f"/api/v1/organization/{org['id']}/environments/{env_id}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_cannot_delete_environment_from_another_org(
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

    response = await client.post(
        f"/api/v1/organization/{org['id']}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201
    d = response.json()
    env_id = d["id"]

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.delete(
        f"/api/v1/organization/{org['id']}/environments/{env_id}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_list_environments(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201
    d = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
    )
    assert response.status_code == 200
    envs = response.json()

    assert envs["count"] == 1
    assert len(envs["items"]) == 1
    assert envs["items"][0]["id"] == d["id"]


@pytest.mark.anyio
async def test_paginate_environments(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201

    name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201

    name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        params={"limit": 1},
    )
    assert response.status_code == 200, response.json()
    environments = response.json()

    assert environments["count"] == 3
    assert len(environments["items"]) == 1

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments?page=2",
        headers=headers,
    )
    assert response.status_code == 200
    environments = response.json()

    assert environments["count"] == 3
    assert len(environments["items"]) == 0


@pytest.mark.anyio
async def test_environment_page_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments?page=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_environment_limit_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments?limit=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_environment_limit_cannot_be_greater_than_10(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments?limit=20",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_environment_plans(
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
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201
    env = response.json()
    env_id = env["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "environment": {"provider": "reliably_cloud", "id": env_id},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201
    plan = response.json()
    plan_id = plan["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}/plans",
        headers=headers,
    )
    assert response.status_code == 200
    plan_ids = response.json()
    assert [plan_id] == plan_ids


@pytest.mark.anyio
async def test_cannot_environment_if_plan_still_exists(
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
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201
    env = response.json()
    env_id = env["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "environment": {"provider": "reliably_cloud", "id": env_id},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201
    plan = response.json()
    plan_id = plan["id"]

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}",
        headers=headers,
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_update_environment_var(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201, response.json()
    env = response.json()
    assert "id" in env
    assert env["org_id"] == str(authed_org.id)
    env_id = env["id"]


    response = await client.put(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}/set",
        headers=headers,
        json={"var_name": "MY_VAR", "value": "hello"}
    )
    assert response.status_code == 200, response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}/clear",
        headers=headers,
    )
    assert response.status_code == 200
    env = response.json()
    assert env["envvars"][0]["var_name"] == "MY_VAR"
    assert env["envvars"][0]["value"] == "hello"


@pytest.mark.anyio
async def test_update_environment_secret(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201
    env = response.json()
    assert "id" in env
    assert env["org_id"] == str(authed_org.id)
    env_id = env["id"]

    response = await client.put(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}/set",
        headers=headers,
        json={"var_name": "SEC", "value": "boom", "key": "mykey"}
    )
    assert response.status_code == 200, response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}/clear",
        headers=headers,
    )
    assert response.status_code == 200
    env = response.json()
    assert env["secrets"][0]["var_name"] == "SEC"
    assert env["secrets"][0]["value"] == "boom"


@pytest.mark.anyio
async def test_update_environment_var_and_secret(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201
    env = response.json()
    assert "id" in env
    assert env["org_id"] == str(authed_org.id)
    env_id = env["id"]

    response = await client.put(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}/set",
        headers=headers,
        json={"var_name": "SEC", "value": "boom", "key": "mykey"}
    )
    assert response.status_code == 200, response.json()

    response = await client.put(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}/set",
        headers=headers,
        json={"var_name": "MY_VAR", "value": "hello"}
    )
    assert response.status_code == 200, response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}/clear",
        headers=headers,
    )
    assert response.status_code == 200
    env = response.json()
    assert env["secrets"][0]["var_name"] == "SEC"
    assert env["secrets"][0]["value"] == "boom"

    assert env["envvars"][0]["var_name"] == "MY_VAR"
    assert env["envvars"][0]["value"] == "hello"


@pytest.mark.anyio
async def test_remove_environment_var(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}, {"var_name": "YOUR_VAR", "value": "bonjour"}, {"var_name": "THEIR_VAR", "value": "hola"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201
    env = response.json()
    assert "id" in env
    assert env["org_id"] == str(authed_org.id)
    env_id = env["id"]

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}/remove/YOUR_VAR",
        headers=headers,
    )
    assert response.status_code == 200, response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}/clear",
        headers=headers,
    )
    assert response.status_code == 200
    env = response.json()
    assert len(env["envvars"]) == 2
    assert env["envvars"][0] == {"var_name": "MY_VAR", "value": "hi"}
    assert env["envvars"][1] == {"var_name": "THEIR_VAR", "value": "hola"}


@pytest.mark.anyio
async def test_remove_environment_secret(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}, {"var_name": "YOUR_VAR", "value": "bonjour", "key": "yourkey"}, {"var_name": "THEIR_VAR", "value": "hola", "key": "theirkey"}],
        },
    )
    assert response.status_code == 201
    env = response.json()
    assert "id" in env
    assert env["org_id"] == str(authed_org.id)
    env_id = env["id"]

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}/remove/yourkey",
        headers=headers,
    )
    assert response.status_code == 200, response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}/clear",
        headers=headers,
    )
    assert response.status_code == 200
    env = response.json()
    assert len(env["secrets"]) == 2
    assert env["secrets"][0] == {"var_name": "SEC", "value": "hello", "key": "mykey"}
    assert env["secrets"][1] == {"var_name": "THEIR_VAR", "value": "hola", "key": "theirkey"}


@pytest.mark.anyio
async def test_add_environment_var(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}, {"var_name": "THEIR_VAR", "value": "hola"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201
    env = response.json()
    assert "id" in env
    assert env["org_id"] == str(authed_org.id)
    env_id = env["id"]

    response = await client.put(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}/set",
        headers=headers,
        json={"var_name": "YOUR_VAR", "value": "bonjour"}
    )
    assert response.status_code == 200, response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}/clear",
        headers=headers,
    )
    assert response.status_code == 200
    env = response.json()
    assert len(env["envvars"]) == 3
    assert env["envvars"][0] == {"var_name": "MY_VAR", "value": "hi"}
    assert env["envvars"][1] == {"var_name": "THEIR_VAR", "value": "hola"}
    assert env["envvars"][2] == {"var_name": "YOUR_VAR", "value": "bonjour"}


@pytest.mark.anyio
async def test_clone_environment(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201
    d = response.json()
    env_id = d["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}/clone",
        headers=headers,
        json={
            "name": "my new name",
        }
    )
    assert response.status_code == 201, response.json()
    cloned_d = response.json()
    cloned_env_id = cloned_d["id"]

    assert env_id != cloned_env_id
    assert d["name"] != cloned_d["name"]
    assert cloned_d["name"] == "my new name"
    assert d["envvars"] == cloned_d["envvars"]
    assert d["secrets"] == cloned_d["secrets"]


@pytest.mark.anyio
async def test_get_enviroments_simple(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201
    e = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments/simple",
        headers=headers,
    )
    assert response.status_code == 200
    d = response.json()
    
    assert len(d) == 1
    assert d[0]["id"] == e["id"]
    assert d[0]["name"] == e["name"]


@pytest.mark.anyio
async def test_search_by_name(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/environments",
        headers=headers,
        json={
            "name": name,
            "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
            "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
        },
    )
    assert response.status_code == 201
    d = response.json()


    pattern = name[2:5]
    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments/search",
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
        f"/api/v1/organization/{str(authed_org.id)}/environments/search",
        headers=headers,
        params={
            "pattern": "5678",
        }
    )
    assert response.status_code == 200
    items = response.json()
    assert items["count"] == 0
