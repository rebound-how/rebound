import re
from contextlib import contextmanager

import pytest
import respx
import ujson
from faker import Faker
from httpx import AsyncClient, Response


@pytest.mark.anyio
async def test_create_experiment(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    exp = response.json()
    assert "id" in exp
    assert exp["org_id"] == str(authed_org.id)


@pytest.mark.anyio
async def test_get_raw_experiment(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    exp = response.json()
    exp_id = exp["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{exp_id}/raw",
        headers=headers,
    )
    assert response.status_code == 200
    raw = response.json()
    assert raw["title"] == "hello world"
    assert "controls" in raw


@pytest.mark.anyio
async def test_delete_experiment(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    d = response.json()
    exp_id = d["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{exp_id}/executions",  # noqa
        headers=headers,
        json={"result": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    exec = response.json()
    exec_id = exec["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/executions",
        headers=headers,
    )
    execs = response.json()
    assert execs["count"] == 1
    assert execs["items"][0]["id"] == exec_id

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{exp_id}",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/executions",
        headers=headers,
    )
    execs = response.json()
    assert execs["count"] == 0


@pytest.mark.anyio
async def test_cannot_get_experiment_from_another_org(
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
        f"/api/v1/organization/{org['id']}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    d = response.json()
    exp_id = d["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{exp_id}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{exp_id}/raw",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.get(
        f"/api/v1/organization/{org['id']}/experiments/{exp_id}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_cannot_delete_experiment_if_plan_still_exists(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    d = response.json()
    exp_id = d["id"]

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
            "experiments": [exp_id],
        },
    )
    assert response.status_code == 201

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{exp_id}",
        headers=headers,
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_cannot_delete_experiment_from_another_org(
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
        f"/api/v1/organization/{org['id']}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    d = response.json()
    exp_id = d["id"]

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{exp_id}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.delete(
        f"/api/v1/organization/{org['id']}/experiments/{exp_id}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_list_experiments(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    d = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
    )
    assert response.status_code == 200
    exps = response.json()

    assert exps["count"] == 1
    assert len(exps["items"]) == 1
    assert exps["items"][0]["id"] == d["id"]


@pytest.mark.anyio
async def test_paginate_experiments(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
        params={"limit": 1},
    )
    assert response.status_code == 200, response.json()
    experiments = response.json()

    assert experiments["count"] == 3
    assert len(experiments["items"]) == 1

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments?page=2",
        headers=headers,
    )
    assert response.status_code == 200
    experiments = response.json()

    assert experiments["count"] == 3
    assert len(experiments["items"]) == 0


@pytest.mark.anyio
async def test_experiment_page_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments?page=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_experiment_limit_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments?limit=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_experiment_limit_cannot_be_greater_than_10(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments?limit=20",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_import_experiment(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/import",
        headers=headers,
        json={"experiment": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201, response.json()
    exp = response.json()
    assert "id" in exp
    assert exp["org_id"] == str(authed_org.id)


@pytest.mark.anyio
async def test_import_experiment_removes_reliably_values(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/import",
        headers=headers,
        json={
            "experiment": ujson.dumps(
                {
                    "title": "hello world",
                    "configuration": {"reliably_org_id": str(authed_org.id)},
                    "extensions": [
                        {
                            "name": "other",
                        },
                        {"name": "reliably", "message": "bye bye"},
                        {
                            "name": "other again",
                        },
                    ],
                }
            )
        },
    )
    assert response.status_code == 201, response.json()
    exp = response.json()
    assert "id" in exp
    assert exp["org_id"] == str(authed_org.id)

    assert exp["definition"] == {
        "title": "hello world",
        "configuration": {"reliably_org_id": str(authed_org.id)},
        "extensions": [
            {
                "name": "other",
            },
            {
                "name": "other again",
            },
        ],
        "controls": [
            {
                "name": "reliably",
                "provider": {
                    "type": "python",
                    "module": "chaosreliably.controls.experiment",
                    "arguments": {
                        "org_id": str(authed_org.id),
                        "exp_id": exp["id"],
                    },
                },
            }
        ],
    }


@pytest.mark.anyio
async def test_get_all_experiments(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/import",
        headers=headers,
        json={
            "experiment": ujson.dumps(
                {
                    "title": "hello world",
                }
            )
        },
    )
    assert response.status_code == 201, response.json()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/import",
        headers=headers,
        json={
            "experiment": ujson.dumps(
                {
                    "title": "a beautiful morning",
                }
            )
        },
    )
    assert response.status_code == 201, response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/all",
        headers=headers,
    )
    assert response.status_code == 200, response.json()

    x = response.json()
    assert x["count"] == 2
    assert x["items"][0]["title"] == "a beautiful morning"
    assert x["items"][1]["title"] == "hello world"


@pytest.mark.anyio
async def test_get_experiments_summary(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/import",
        headers=headers,
        json={
            "experiment": ujson.dumps(
                {
                    "title": "hello world",
                }
            )
        },
    )
    assert response.status_code == 201, response.json()
    x1_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/import",
        headers=headers,
        json={
            "experiment": ujson.dumps(
                {
                    "title": "a beautiful morning",
                }
            )
        },
    )
    assert response.status_code == 201, response.json()
    x2_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x1_id}/executions",  # noqa
        headers=headers,
        json={"result": ujson.dumps({"status": "failed"})},
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x1_id}/executions",  # noqa
        headers=headers,
        json={"result": ujson.dumps({"status": "completed"})},
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x2_id}/executions",  # noqa
        headers=headers,
        json={"result": ujson.dumps({"status": "deviated"})},
    )
    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/summary",
        headers=headers,
    )
    assert response.status_code == 200, response.json()

    x = response.json()
    assert len(x) == 2


@pytest.mark.anyio
async def test_get_experiment_plans(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    exp = response.json()
    exp_id = exp["id"]

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
            "experiments": [exp_id],
        },
    )
    assert response.status_code == 201
    plan = response.json()
    plan_id = plan["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{exp_id}/plans",
        headers=headers,
    )
    assert response.status_code == 200
    plans = response.json()
    assert len(plans) == 1
    assert plans[0] == plan_id


@pytest.mark.anyio
async def test_search_by_name(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.name()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    d = response.json()


    pattern = "lo worl"
    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/search",
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
        f"/api/v1/organization/{str(authed_org.id)}/experiments/search",
        headers=headers,
        params={
            "pattern": "5678",
        }
    )
    assert response.status_code == 200
    items = response.json()
    assert items["count"] == 0


@pytest.mark.anyio
async def test_replace_experiment(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    exp = response.json()
    assert "id" in exp
    exp_id = exp["id"]
    assert exp["org_id"] == str(authed_org.id)


    response = await client.put(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{exp_id}",
        headers=headers,
        json={"experiment": ujson.dumps({"title": "hi there"})},
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{exp_id}",
        headers=headers,
    )
    assert response.status_code == 200
    exp = response.json()
    assert "id" in exp
    assert exp_id == exp["id"]
    assert exp["definition"]["title"] == "hi there"

