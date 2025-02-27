import uuid

import pytest
import ujson
from faker import Faker
from httpx import AsyncClient


EXPERIMENT = {
    "version": "1.0.0",
    "dry": None,
    "title": "A dummy experiment",
    "method": [
        {
            "name": "say-hello",
            "type": "action",
            "pauses": {"after": 3},
            "controls": [
                {
                    "name": "repeat-me",
                    "provider": {
                        "type": "python",
                        "module": "chaosaddons.controls.repeat",
                        "arguments": {"repeat_count": 5},
                    },
                }
            ],
            "provider": {
                "path": "echo",
                "type": "process",
                "arguments": "hello",
            },
        },
    ],
    "description": "n/a",
    "steady-state-hypothesis": {
        "title": "check this, check that",
        "probes": [
            {
                "name": "echo-hello",
                "type": "probe",
                "provider": {
                    "path": "echo",
                    "type": "process",
                    "arguments": "hello boom",
                },
                "tolerance": 0,
            }
        ],
    },
}
EXECUTION = {
    "end": "2022-12-12T08:45:41.809371",
    "run": [
        {
            "end": "2022-12-12T08:45:26.753514",
            "start": "2022-12-12T08:45:26.750047",
            "output": {"status": 0, "stderr": "", "stdout": "hello\n"},
            "status": "succeeded",
            "activity": {
                "name": "say-hello",
                "type": "action",
                "pauses": {"after": 3},
                "controls": [
                    {
                        "name": "repeat-me",
                        "provider": {
                            "type": "python",
                            "module": "chaosaddons.controls.repeat",
                            "arguments": {"repeat_count": 5},
                        },
                    }
                ],
                "provider": {
                    "path": "echo",
                    "type": "process",
                    "arguments": "hello",
                },
            },
            "duration": 0.003467,
        },
        {
            "end": "2022-12-12T08:45:29.764655",
            "start": "2022-12-12T08:45:29.758925",
            "output": {"status": 0, "stderr": "", "stdout": "hello\n"},
            "status": "succeeded",
            "activity": {
                "name": "say-hello",
                "type": "action",
                "pauses": {"after": 3},
                "controls": [
                    {
                        "name": "repeat-me",
                        "provider": {
                            "type": "python",
                            "module": "chaosaddons.controls.repeat",
                            "arguments": {"repeat_count": 5},
                        },
                    }
                ],
                "provider": {
                    "path": "echo",
                    "type": "process",
                    "arguments": "hello",
                },
                "iteration_index": 1,
            },
            "duration": 0.00573,
        },
        {
            "end": "2022-12-12T08:45:32.776209",
            "start": "2022-12-12T08:45:32.770224",
            "output": {"status": 0, "stderr": "", "stdout": "hello\n"},
            "status": "succeeded",
            "activity": {
                "name": "say-hello",
                "type": "action",
                "pauses": {"after": 3},
                "controls": [
                    {
                        "name": "repeat-me",
                        "provider": {
                            "type": "python",
                            "module": "chaosaddons.controls.repeat",
                            "arguments": {"repeat_count": 5},
                        },
                    }
                ],
                "provider": {
                    "path": "echo",
                    "type": "process",
                    "arguments": "hello",
                },
                "iteration_index": 2,
            },
            "duration": 0.005985,
        },
        {
            "end": "2022-12-12T08:45:35.785165",
            "start": "2022-12-12T08:45:35.780983",
            "output": {"status": 0, "stderr": "", "stdout": "hello\n"},
            "status": "succeeded",
            "activity": {
                "name": "say-hello",
                "type": "action",
                "pauses": {"after": 3},
                "controls": [
                    {
                        "name": "repeat-me",
                        "provider": {
                            "type": "python",
                            "module": "chaosaddons.controls.repeat",
                            "arguments": {"repeat_count": 5},
                        },
                    }
                ],
                "provider": {
                    "path": "echo",
                    "type": "process",
                    "arguments": "hello",
                },
                "iteration_index": 3,
            },
            "duration": 0.004182,
        },
        {
            "end": "2022-12-12T08:45:38.798661",
            "start": "2022-12-12T08:45:38.793821",
            "output": {"status": 0, "stderr": "", "stdout": "hello\n"},
            "status": "succeeded",
            "activity": {
                "name": "say-hello",
                "type": "action",
                "pauses": {"after": 3},
                "controls": [
                    {
                        "name": "repeat-me",
                        "provider": {
                            "type": "python",
                            "module": "chaosaddons.controls.repeat",
                            "arguments": {"repeat_count": 5},
                        },
                    }
                ],
                "provider": {
                    "path": "echo",
                    "type": "process",
                    "arguments": "hello",
                },
                "iteration_index": 4,
            },
            "duration": 0.00484,
        },
    ],
    "node": "localhost",
    "start": "2022-12-12T08:45:26.108932",
    "status": "completed",
    "deviated": False,
    "duration": 15.705720901489258,
    "platform": "Linux-5.15.60-x86_64-with-glibc2.35",
    "rollbacks": [],
    "experiment": {
        "dry": None,
        "title": "A dummy experiment",
        "method": [
            {
                "name": "say-hello",
                "type": "action",
                "pauses": {"after": 3},
                "controls": [
                    {
                        "name": "repeat-me",
                        "provider": {
                            "type": "python",
                            "module": "chaosaddons.controls.repeat",
                            "arguments": {"repeat_count": 5},
                        },
                    }
                ],
                "provider": {
                    "path": "echo",
                    "type": "process",
                    "arguments": "hello",
                },
            },
            {
                "name": "say-hello",
                "type": "action",
                "pauses": {"after": 3},
                "controls": [
                    {
                        "name": "repeat-me",
                        "provider": {
                            "type": "python",
                            "module": "chaosaddons.controls.repeat",
                            "arguments": {"repeat_count": 5},
                        },
                    }
                ],
                "provider": {
                    "path": "echo",
                    "type": "process",
                    "arguments": "hello",
                },
                "iteration_index": 1,
            },
            {
                "name": "say-hello",
                "type": "action",
                "pauses": {"after": 3},
                "controls": [
                    {
                        "name": "repeat-me",
                        "provider": {
                            "type": "python",
                            "module": "chaosaddons.controls.repeat",
                            "arguments": {"repeat_count": 5},
                        },
                    }
                ],
                "provider": {
                    "path": "echo",
                    "type": "process",
                    "arguments": "hello",
                },
                "iteration_index": 2,
            },
            {
                "name": "say-hello",
                "type": "action",
                "pauses": {"after": 3},
                "controls": [
                    {
                        "name": "repeat-me",
                        "provider": {
                            "type": "python",
                            "module": "chaosaddons.controls.repeat",
                            "arguments": {"repeat_count": 5},
                        },
                    }
                ],
                "provider": {
                    "path": "echo",
                    "type": "process",
                    "arguments": "hello",
                },
                "iteration_index": 3,
            },
            {
                "name": "say-hello",
                "type": "action",
                "pauses": {"after": 3},
                "controls": [
                    {
                        "name": "repeat-me",
                        "provider": {
                            "type": "python",
                            "module": "chaosaddons.controls.repeat",
                            "arguments": {"repeat_count": 5},
                        },
                    }
                ],
                "provider": {
                    "path": "echo",
                    "type": "process",
                    "arguments": "hello",
                },
                "iteration_index": 4,
            },
        ],
        "version": "1.0.0",
        "controls": [
            {
                "name": "reliably",
                "provider": {
                    "type": "python",
                    "module": "chaosreliably.controls.experiment",
                    "arguments": {
                        "exp_id": "79de1bbe-04f9-4e42-8e57-3cd6d1bb77b7",
                        "org_id": "8f67bb6a-4944-40af-80b0-921023467cdc",
                    },
                },
            }
        ],
        "description": "n/a",
        "steady-state-hypothesis": {
            "title": "check this, check that",
            "probes": [
                {
                    "name": "echo-hello",
                    "type": "probe",
                    "provider": {
                        "path": "echo",
                        "type": "process",
                        "arguments": "hello boom",
                    },
                    "tolerance": 0,
                }
            ],
        },
    },
    "steady_states": {
        "after": {
            "probes": [
                {
                    "end": "2022-12-12T08:45:41.807123",
                    "start": "2022-12-12T08:45:41.803371",
                    "output": {
                        "status": 0,
                        "stderr": "",
                        "stdout": "hello boom\n",
                    },
                    "status": "succeeded",
                    "activity": {
                        "name": "echo-hello",
                        "type": "probe",
                        "provider": {
                            "path": "echo",
                            "type": "process",
                            "arguments": "hello boom",
                        },
                        "tolerance": 0,
                    },
                    "duration": 0.003752,
                    "tolerance_met": True,
                }
            ],
            "steady_state_met": True,
        },
        "before": {
            "probes": [
                {
                    "end": "2022-12-12T08:45:26.747544",
                    "start": "2022-12-12T08:45:26.735228",
                    "output": {
                        "status": 0,
                        "stderr": "",
                        "stdout": "hello boom\n",
                    },
                    "status": "succeeded",
                    "activity": {
                        "name": "echo-hello",
                        "type": "probe",
                        "provider": {
                            "path": "echo",
                            "type": "process",
                            "arguments": "hello boom",
                        },
                        "tolerance": 0,
                    },
                    "duration": 0.012316,
                    "tolerance_met": True,
                }
            ],
            "steady_state_met": True,
        },
        "during": [],
    },
    "chaoslib-version": "1.29.0",
}


@pytest.mark.anyio
async def test_create_execution(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments",
        headers=headers,
        json={"definition": ujson.dumps(EXPERIMENT)},
    )
    assert response.status_code == 201, response.json()
    x = response.json()

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x['id']}/executions",  # noqa
        headers=headers,
        json={"result": ujson.dumps(EXECUTION)},
    )
    assert response.status_code == 201
    xc = response.json()
    assert "id" in xc
    assert xc["org_id"] == str(authed_org.id)
    exec_id = xc["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x['id']}/executions",  # noqa
        headers=headers,
    )
    assert response.status_code == 200
    execs = response.json()
    assert execs["count"] == 1
    assert len(execs["items"]) == 1

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/series/executions/per/experiment",  # noqa
        headers=headers,
        params={"exp_id": x["id"]},
    )
    assert response.status_code == 200
    series = response.json()
    assert series["labels"] == []

    response = await client.put(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x['id']}/executions/{exec_id}/results",  # noqa
        headers=headers,
        json={"result": ujson.dumps(EXECUTION)},
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/series/executions/per/experiment",  # noqa
        headers=headers,
        params={"exp_id": x["id"]},
    )
    assert response.status_code == 200
    series = response.json()
    assert series["labels"] == []

    response = await client.put(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x['id']}/executions/{exec_id}/state",  # noqa
        headers=headers,
        json={
            "current": "finished",
            "status": "completed",
            "deviated": False
        }
    )
    assert response.status_code == 200, response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/series/executions/per/experiment",  # noqa
        headers=headers,
        params={"exp_id": x["id"]},
    )
    assert response.status_code == 200
    series = response.json()
    assert series["labels"] == [xc["id"]]


@pytest.mark.anyio
async def test_delete_execution(
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
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    x = response.json()
    exp_id = x["id"]

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

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x['id']}/executions",  # noqa
        headers=headers,
        json={
            "result": ujson.dumps({"title": "hello world"}),
            "plan_id": plan_id,
        },
    )
    assert response.status_code == 201
    xc = response.json()
    assert "id" in xc
    assert xc["org_id"] == str(authed_org.id)

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["executions_count"] == 1

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x['id']}/executions/{xc['id']}",  # noqa
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x['id']}/executions/{xc['id']}",  # noqa
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["executions_count"] == 0


@pytest.mark.anyio
async def test_execution_must_be_retrieved_from_its_experiment(
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
    x = response.json()

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    x2 = response.json()

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={"result": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    exec = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x2['id']}/executions/{exec['id']}",  # noqa
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.get(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions/{exec['id']}",  # noqa
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_execution_get_log(
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
    x = response.json()

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={"result": ujson.dumps(
            {"title": "hello world"}), "log": "hello world"},
    )
    assert response.status_code == 201
    exec = response.json()

    response = await client.get(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions/{exec['id']}/log",  # noqa
        headers=headers,
    )
    assert response.status_code == 200
    assert response.text == "hello world"


@pytest.mark.anyio
async def test_execution_get_journal(
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
    x = response.json()

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={"result": ujson.dumps(
            {"title": "hello world"}), "log": "hello world"},
    )
    assert response.status_code == 201
    exec = response.json()

    response = await client.get(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions/{exec['id']}/results",  # noqa
        headers=headers,
    )
    assert response.status_code == 200
    r = response.json()
    assert r["title"] == "hello world"
    assert "start" in r


@pytest.mark.anyio
async def test_cannot_get_execution_from_another_org(
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
    x = response.json()

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={"result": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    exec = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x['id']}/executions/{exec['id']}",  # noqa
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.get(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions/{exec['id']}",  # noqa
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_cannot_delete_execution_from_another_org(
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
    x = response.json()

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={"result": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    exec = response.json()

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x['id']}/executions/{exec['id']}",  # noqa
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.delete(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions/{exec['id']}",  # noqa
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_cannot_update_execution_result_from_another_org(
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
    x = response.json()

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={"result": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    exec = response.json()

    response = await client.put(
        f"/api/v1/organization/{str(authed_org.id)}/experiments/{x['id']}/executions/{exec['id']}/results",  # noqa
        headers=headers,
        json={"result": ujson.dumps({"title": "hello monde"})},
    )
    assert response.status_code == 404

    response = await client.get(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions/{exec['id']}/results",  # noqa
        headers=headers,
    )
    assert response.status_code == 200
    r = response.json()
    assert r["title"] == "hello world"
    assert "start" in r


@pytest.mark.anyio
async def test_list_executions_from_org(
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
    x = response.json()

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={"result": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    exec = response.json()

    response = await client.get(
        f"/api/v1/organization/{org['id']}/executions",
        headers=headers,
    )
    assert response.status_code == 200
    execs = response.json()

    assert execs["count"] == 1
    assert len(execs["items"]) == 1
    assert execs["items"][0]["id"] == exec["id"]


@pytest.mark.anyio
async def test_paginate_executions_from_org(
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
    x = response.json()

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={"result": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={"result": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={"result": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={"result": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/organization/{org['id']}/executions",
        headers=headers,
        params={"limit": 1},
    )
    assert response.status_code == 200, response.json()
    executions = response.json()

    assert executions["count"] == 4
    assert len(executions["items"]) == 1

    response = await client.get(
        f"/api/v1/organization/{org['id']}/executions?page=2&limit=1",
        headers=headers,
    )
    assert response.status_code == 200
    executions = response.json()

    assert executions["count"] == 4
    assert len(executions["items"]) == 1


@pytest.mark.anyio
async def test_execution_page_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/executions?page=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_execution_limit_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/executions?limit=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_execution_limit_cannot_be_greater_than_10(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/executions?limit=20",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_list_executions_from_plan(
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

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{org['id']}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    x = response.json()
    exp_id = x["id"]

    response = await client.post(
        f"/api/v1/organization/{org['id']}/plans",
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

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={
            "plan_id": plan_id,
            "result": ujson.dumps({"title": "hello world"}),
        },
    )
    assert response.status_code == 201
    exec = response.json()

    response = await client.get(
        f"/api/v1/organization/{org['id']}/executions",
        headers=headers,
    )
    assert response.status_code == 200
    execs = response.json()

    assert execs["count"] == 1
    assert len(execs["items"]) == 1
    assert execs["items"][0]["id"] == exec["id"]
    assert execs["items"][0]["plan_id"] == plan_id


@pytest.mark.anyio
async def test_paginate_executions_from_plan(
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

    env_name = fake.name()
    response = await client.post(
        f"/api/v1/organization/{org['id']}/deployments",
        headers=headers,
        json={
            "name": env_name,
            "definition": {"type": "noop"},
        },
    )
    assert response.status_code == 201
    dep_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments",
        headers=headers,
        json={"definition": ujson.dumps({"title": "hello world"})},
    )
    assert response.status_code == 201
    x = response.json()
    exp_id = x["id"]

    response = await client.post(
        f"/api/v1/organization/{org['id']}/plans",
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

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={
            "plan_id": plan_id,
            "result": ujson.dumps({"title": "hello world"}),
        },
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={
            "plan_id": plan_id,
            "result": ujson.dumps({"title": "hello world"}),
        },
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={
            "plan_id": plan_id,
            "result": ujson.dumps({"title": "hello world"}),
        },
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={
            "plan_id": plan_id,
            "result": ujson.dumps({"title": "hello world"}),
        },
    )
    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/organization/{org['id']}/plans/{plan_id}/executions",
        headers=headers,
        params={"limit": 1},
    )
    assert response.status_code == 200, response.json()
    executions = response.json()

    assert executions["count"] == 4
    assert len(executions["items"]) == 1

    response = await client.get(
        f"/api/v1/organization/{org['id']}/plans/{plan_id}/executions?page=2",
        headers=headers,
        params={"limit": 1},
    )
    assert response.status_code == 200
    executions = response.json()

    assert executions["count"] == 4
    assert len(executions["items"]) == 1


@pytest.mark.anyio
async def test_execution_page_must_be_positive_or_zero_for_plan(
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
    exp_id = response.json()["id"]

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
        f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}/executions?page=-1",  # noqa
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_execution_limit_must_be_positive_or_zero_for_plan(
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
    exp_id = response.json()["id"]

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
        f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}/executions?limit=-1",  # noqa
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_execution_limit_cannot_be_greater_than_10_for_plan(
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
    exp_id = response.json()["id"]

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
        f"/api/v1/organization/{str(authed_org.id)}/plans/{plan_id}/executions?limit=20",  # noqa
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_execution_set_user_state(
    client: AsyncClient, authed: None, agent_token: str, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {agent_token}"}

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
    x = response.json()

    response = await client.post(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions",
        headers=headers,
        json={"result": ujson.dumps(
            {"title": "hello world"}), "log": "hello world"},
    )
    assert response.status_code == 201
    exec = response.json()

    response = await client.get(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions/{exec['id']}/state",  # noqa
        headers=headers,
    )
    assert response.status_code == 200
    state = response.json()
    assert state["current"] == "pending"

    response = await client.put(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions/{exec['id']}/state",  # noqa
        headers=headers,
        json={
            "state": "terminate",
            "skip_rollbacks": True,
        }
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{org['id']}/experiments/{x['id']}/executions/{exec['id']}/state",  # noqa
        headers=headers,
    )
    assert response.status_code == 200
    state = response.json()
    assert state["current"] == "terminate"
    assert state["skip_rollbacks"] is True
