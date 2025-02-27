import json
import uuid

import pytest
from faker import Faker
from httpx import AsyncClient

from reliably_app.database import SessionLocal
from reliably_app.plan import crud, schemas


@pytest.mark.anyio
async def test_create_plan(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "environment": {"type": "github", "name": env_name},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201
    plan = response.json()
    assert "id" in plan
    assert plan["definition"]["deployment"]["deployment_id"] == dep_id
    assert plan["definition"]["environment"]["provider"] == "github"
    assert plan["definition"]["environment"]["name"] == env_name
    assert plan["definition"]["schedule"]["type"] == "now"


@pytest.mark.anyio
async def test_list_plans(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "environment": {"type": "github", "name": env_name},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201
    plan = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
    )
    assert response.status_code == 200
    plans = response.json()

    assert plans["count"] == 1
    assert len(plans["items"]) == 1
    assert plans["items"][0]["id"] == plan["id"]


@pytest.mark.anyio
async def test_paginate_plans(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "environment": {"type": "github", "name": env_name},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "environment": {"type": "github", "name": env_name},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "environment": {"type": "github", "name": env_name},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        params={"limit": 1},
    )
    assert response.status_code == 200, response.json()
    plans = response.json()

    assert plans["count"] == 3
    assert len(plans["items"]) == 1

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans?page=2",
        headers=headers,
    )
    assert response.status_code == 200
    plans = response.json()

    assert plans["count"] == 3
    assert len(plans["items"]) == 0


@pytest.mark.anyio
async def test_delete_plan(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "environment": {"type": "github", "name": env_name},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201
    plan = response.json()
    plan_id = plan["id"]

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}",
        headers=headers,
    )
    assert response.status_code == 404

    async with SessionLocal() as db:
        plan = await crud.get_plan(db, plan_id, status=None)
        assert plan.id is not None
        assert plan.status == schemas.PlanStatus.deleted


@pytest.mark.anyio
async def test_cannot_get_plan_from_another_org(
    client: AsyncClient, authed: None, mock_cloud_resources_creation: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.company()
    with mock_cloud_resources_creation():
        response = await client.post(
            "/api/v1/organization", json={"name": name}, headers=headers
        )
        assert response.status_code == 201
        org = response.json()

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "environment": {"type": "github", "name": env_name},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201
    plan = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(org['id'])}/plans/{plan['id']}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans/{plan['id']}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_cannot_delete_plan_from_another_org(
    client: AsyncClient, authed: None, mock_cloud_resources_creation: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.company()
    with mock_cloud_resources_creation():
        response = await client.post(
            "/api/v1/organization", json={"name": name}, headers=headers
        )
        assert response.status_code == 201
        org = response.json()

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "environment": {"type": "github", "name": env_name},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201
    plan = response.json()

    response = await client.delete(
        f"/api/v1/organization/{str(org['id'])}/plans/{plan['id']}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/plans/{plan['id']}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_plan_page_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans?page=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_plan_limit_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans?limit=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_plan_limit_cannot_be_greater_than_10(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans?limit=20",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_set_plan_status(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "environment": {"type": "github", "name": env_name},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201
    plan = response.json()
    plan_id = plan["id"]

    for s in (
        "creating",
        "created",
        "completed",
        "running",
        "iteration completed",
    ):
        response = await client.put(
            f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}/status",
            headers=headers,
            json={"status": s},
        )
        assert response.status_code == 200

        response = await client.get(
            f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}",
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == s
        assert response.json()["error"] is None

    for s in ("creation error", "error"):
        error = fake.word()
        response = await client.put(
            f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}/status",
            headers=headers,
            json={"status": s, "error": error},
        )
        assert response.status_code == 200

        response = await client.get(
            f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}",
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == s
        assert response.json()["error"] == error


@pytest.mark.anyio
async def test_get_next_schedulable(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "environment": {"type": "github", "name": env_name},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now", "via_agent": True},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201
    plan = response.json()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201
    agent = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/agents/{agent['id']}/token",  # noqa
        headers=headers,
    )
    assert response.status_code == 200
    token = response.json()

    agent_headers = {"Authorization": f"Bearer {token['token']}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans/schedulables/next",
        headers=agent_headers,
        params={"deployment_type": "whatever"},
    )
    assert response.status_code == 422, response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans/schedulables/next",
        headers=agent_headers,
        params={"deployment_type": "noop"},
    )
    assert response.status_code == 200
    p = response.json()

    assert plan["id"] == p["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans/schedulables/next",
        headers=agent_headers,
        params={"deployment_type": "noop"},
    )
    assert response.status_code == 200
    p = response.json()

    assert p is None


@pytest.mark.anyio
async def test_list_plan_executions(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
        json={"definition": {}},
    )
    assert response.status_code == 201, response.json()
    x = response.json()
    x_id = x["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "environment": {"type": "github", "name": env_name},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [x_id],
        },
    )
    assert response.status_code == 201
    plan = response.json()
    plan_id = plan["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}/executions",
        headers=headers,
    )
    execs = response.json()

    assert execs["count"] == 0

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x_id}/executions",  # noqa
        headers=headers,
        json={"result": {}, "plan_id": plan_id},
    )
    assert response.status_code == 201
    xc = response.json()
    assert "id" in xc
    assert xc["org_id"] == str(authed_org.id)
    exec_id = xc["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}/executions",
        headers=headers,
    )
    execs = response.json()

    assert execs["count"] == 1


@pytest.mark.anyio
async def test_update_plan(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    x_id = str(uuid.uuid4())

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "environment": {"type": "github", "name": env_name},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [x_id],
        },
    )
    assert response.status_code == 201
    plan = response.json()
    plan_id = plan["id"]


    response = await client.put(
        f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}",
        headers=headers,
        json={
            "title": "my plan",
            "environment": {"type": "github", "name": env_name},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "cron", "pattern": "* */1 * * *"},
            "experiments": [x_id],
        },
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}",
        headers=headers,
    )
    assert response.status_code == 200
    plan = response.json()

    assert plan["definition"]["schedule"]["type"] == "cron"
    assert plan["definition"]["schedule"]["pattern"] == "* */1 * * *"


@pytest.mark.anyio
async def test_update_plan_cannot_change_experiment(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    x_id = str(uuid.uuid4())

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "environment": {"type": "github", "name": env_name},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [x_id],
        },
    )
    assert response.status_code == 201
    plan = response.json()
    plan_id = plan["id"]


    response = await client.put(
        f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}",
        headers=headers,
        json={
            "title": "my plan",
            "environment": {"type": "github", "name": env_name},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "cron", "pattern": "* */1 * * *"},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_search_by_name(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "title": "hello world",
            "environment": {"type": "github", "name": "hello"},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [str(uuid.uuid4())],
        },
    )
    assert response.status_code == 201
    d = response.json()


    pattern = "lo worl"
    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans/search",
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
        f"/api/v1/organization/{str(authed_org.id)}/plans/search",
        headers=headers,
        params={
            "pattern": "5678",
        }
    )
    assert response.status_code == 200
    items = response.json()
    assert items["count"] == 0


@pytest.mark.anyio
async def test_search_by_name_ands_experiment(
    client: AsyncClient, authed: None, agent_token: str, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {agent_token}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
        json={"definition": json.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    x = response.json()
    x_id = x["id"]

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/plans",
        headers=headers,
        json={
            "title": "hello world",
            "environment": {"type": "github", "name": "hello"},
            "deployment": {"deployment_id": dep_id},
            "schedule": {"type": "now"},
            "experiments": [x_id],
        },
    )
    assert response.status_code == 201
    d = response.json()
    plan_id = d["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x_id}/executions",
        headers=headers,
        json={"plan_id": plan_id, "result": json.dumps(
            {"title": "hello world"}), "log": "hello world"},
    )
    assert response.status_code == 201
    exec = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x_id}/plans",
        headers=headers,
        params={
            "pattern": "lo worl",
        }
    )
    assert response.status_code == 200
    plan_ids = response.json()
    assert len(plan_ids) == 1

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x_id}/plans",
        headers=headers,
        params={
            "pattern": "46675",
        }
    )
    assert response.status_code == 200
    plan_ids = response.json()
    assert len(plan_ids) == 0
