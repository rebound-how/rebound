import re
import uuid
from contextlib import contextmanager

import pytest
import respx
from faker import Faker
from httpx import AsyncClient, Response


@pytest.mark.anyio
async def test_create_integration(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/integrations",
        headers=headers,
        json={
            "name": fake.name(),
            "provider": "slack",
            "vendor": None,
            "environment": {
                "name": fake.name(),
                "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
                "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
            }
        }
    )
    assert response.status_code == 201
    intg = response.json()
    assert "id" in intg
    assert intg["org_id"] == str(authed_org.id)

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{intg['environment_id']}",
        headers=headers,
    )
    resp = response.json()
    assert resp["envvars"] == [{"var_name": "MY_VAR", "value": "hi"}]
    assert len(resp["secrets"]) == 1


@pytest.mark.anyio
async def test_get_ontegration_control_for_slack(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/integrations",
        headers=headers,
        json={
            "name": fake.name(),
            "provider": "slack",
            "vendor": None,
            "environment": {
                "name": fake.name(),
                "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
                "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
            }
        }
    )
    assert response.status_code == 201
    intg = response.json()
    assert "id" in intg
    assert intg["org_id"] == str(authed_org.id)

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/integrations/{intg['id']}/control",
        headers=headers,
    )
    resp = response.json()
    assert resp == {
        "name": "reliably-integration-slack",
        "provider": {
            "type": "python",
            "module": "chaosslack.control",
            "secrets": ["reliably-integration-slack"],
        }
    }


@pytest.mark.anyio
async def test_get_ontegration_control_for_opentelemetry(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/integrations",
        headers=headers,
        json={
            "name": fake.name(),
            "provider": "opentelemetry",
            "vendor": "honeycomb",
            "environment": {
                "name": fake.name(),
                "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
                "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
            }
        }
    )
    assert response.status_code == 201
    intg = response.json()
    assert "id" in intg
    assert intg["org_id"] == str(authed_org.id)

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/integrations/{intg['id']}/control",
        headers=headers,
    )
    resp = response.json()
    assert resp == {
        "name": "reliably-integration-opentelemetry",
        "provider": {
            "type": "python",
            "module": "chaostracing.oltp",
            "arguments": {
                "trace_botocore": True,
                "trace_httpx": True,
                "trace_request": True,
                "trace_urllib3": True,
            },
        },
    }


@pytest.mark.anyio
async def test_create_integration_with_used_name_is_not_allowed(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    intg_name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/integrations",
        headers=headers,
        json={
            "name": intg_name,
            "provider": "slack",
            "vendor": None,
            "environment": {
                "name": fake.name(),
                "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
                "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
            }
        }
    )
    assert response.status_code == 201
    intg = response.json()
    assert "id" in intg
    assert intg["org_id"] == str(authed_org.id)

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/integrations",
        headers=headers,
        json={
            "name": intg_name,
            "provider": "slack",
            "vendor": None,
            "environment": {
                "name": fake.name(),
                "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
                "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
            }
        }
    )
    assert response.status_code == 409


@pytest.mark.anyio
async def test_delete_integration_also_deletes_its_environment(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    intg_name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/integrations",
        headers=headers,
        json={
            "name": intg_name,
            "provider": "slack",
            "vendor": None,
            "environment": {
                "name": fake.name(),
                "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
                "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
            }
        }
    )
    assert response.status_code == 201
    intg = response.json()
    assert "id" in intg
    assert intg["org_id"] == str(authed_org.id)

    env_id = intg["environment_id"]

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/integrations/{intg['id']}",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/integrations/{intg['id']}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/environments/{env_id}",
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_cannot_get_integration_from_another_org(
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

    intg_name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{org['id']}/integrations",
        headers=headers,
        json={
            "name": intg_name,
            "provider": "slack",
            "vendor": None,
            "environment": {
                "name": fake.name(),
                "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
                "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
            }
        }
    )
    assert response.status_code == 201
    intg = response.json()
    assert "id" in intg
    assert intg["org_id"] == org['id']

    intg_id = intg["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/integrations/{intg_id}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.get(
        f"/api/v1/organization/{org['id']}/integrations/{intg_id}",
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

    intg_name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{org['id']}/integrations",
        headers=headers,
        json={
            "name": intg_name,
            "provider": "slack",
            "vendor": None,
            "environment": {
                "name": fake.name(),
                "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
                "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
            }
        }
    )
    assert response.status_code == 201
    intg = response.json()
    assert "id" in intg
    assert intg["org_id"] == org['id']

    intg_id = intg["id"]

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/integrations/{intg_id}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.delete(
        f"/api/v1/organization/{org['id']}/integrations/{intg_id}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_list_integrations(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    intg_name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/integrations",
        headers=headers,
        json={
            "name": intg_name,
            "provider": "slack",
            "vendor": None,
            "environment": {
                "name": fake.name(),
                "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
                "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
            }
        }
    )
    assert response.status_code == 201
    intg = response.json()
    assert "id" in intg
    assert intg["org_id"] == str(authed_org.id)

    intg_id = intg["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/integrations",
        headers=headers,
    )
    assert response.status_code == 200
    intgs = response.json()

    assert intgs["count"] == 1
    assert len(intgs["items"]) == 1
    assert intgs["items"][0]["id"] == intg_id


@pytest.mark.anyio
async def test_paginate_integrations(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    intg_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/integrations",
        headers=headers,
        json={
            "name": intg_name,
            "provider": "slack",
            "vendor": None,
            "environment": {
                "name": fake.name(),
                "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
                "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
            }
        }
    )
    assert response.status_code == 201

    intg_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/integrations",
        headers=headers,
        json={
            "name": intg_name,
            "provider": "slack",
            "vendor": None,
            "environment": {
                "name": fake.name(),
                "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
                "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
            }
        }
    )
    assert response.status_code == 201

    intg_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/integrations",
        headers=headers,
        json={
            "name": intg_name,
            "provider": "slack",
            "vendor": None,
            "environment": {
                "name": fake.name(),
                "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
                "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
            }
        }
    )
    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/integrations",
        headers=headers,
        params={"limit": 1},
    )
    assert response.status_code == 200, response.json()
    integrations = response.json()

    assert integrations["count"] == 3
    assert len(integrations["items"]) == 1

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/integrations?page=2",
        headers=headers,
    )
    assert response.status_code == 200
    integrations = response.json()

    assert integrations["count"] == 3
    assert len(integrations["items"]) == 0


@pytest.mark.anyio
async def test_integration_page_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/integrations?page=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_integration_limit_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/integrations?limit=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_integration_limit_cannot_be_greater_than_10(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/integrations?limit=20",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_integration_plans(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    intg_name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/integrations",
        headers=headers,
        json={
            "name": intg_name,
            "provider": "slack",
            "vendor": None,
            "environment": {
                "name": fake.name(),
                "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
                "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
            }
        }
    )
    assert response.status_code == 201
    intg = response.json()
    intg_id = intg["id"]

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
            "integrations": [intg_id],
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201
    plan = response.json()
    plan_id = plan["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/integrations/{intg_id}/plans",
        headers=headers,
    )
    assert response.status_code == 200
    plan_ids = response.json()
    assert [plan_id] == plan_ids


@pytest.mark.anyio
async def test_cannot_integration_if_plan_still_exists(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    intg_name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/integrations",
        headers=headers,
        json={
            "name": intg_name,
            "provider": "slack",
            "vendor": None,
            "environment": {
                "name": fake.name(),
                "envvars": [{"var_name": "MY_VAR", "value": "hi"}],
                "secrets": [{"var_name": "SEC", "value": "hello", "key": "mykey"}],
            }
        }
    )
    assert response.status_code == 201
    intg = response.json()
    intg_id = intg["id"]

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
            "integrations": [intg_id],
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201
    plan = response.json()
    plan_id = plan["id"]

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/integrations/{intg_id}",
        headers=headers,
    )
    assert response.status_code == 400
