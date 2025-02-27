import json
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any, Dict
from unittest.mock import patch

import pytest
import trustme
from faker import Faker
from httpx import AsyncClient
from lueur.models import Discovery, Meta, Resource, GCPMeta

ca = trustme.CA()
server_cert = ca.issue_cert("example.com")


@pytest.mark.anyio
@patch("reliably_app.snapshot.tasks.snapshot_gcp.explore", autospec=True)
async def test_experiment_generation(
    explore_gcp, client: AsyncClient, authed: None, fake: Faker
):
    org = await create_org(client, authed, fake)
    org_id = org["id"]

    agent = await create_agent(client, authed, org_id)
    agent_id = agent["id"]

    await create_catalog(client, authed, org_id)
    await create_snapshot(explore_gcp, client, authed, org_id, agent_id)

    experiment = await build_experiment_from_catalog_and_snapshot(
        client, authed, org_id
    )

    args = experiment["method"][0]["provider"]["arguments"]
    assert args["label_selector"] == {'age': '2', 'app': 'consumer'}

    await refresh_snapshot(explore_gcp, client, authed, org_id, agent_id)
    experiment = await build_experiment_from_catalog_and_snapshot(
        client, authed, org_id

    )

    args = experiment["method"][0]["provider"]["arguments"]
    assert args["label_selector"] == {'age': '3', 'app': 'consumer'}


###############################################################################
# Helpers
###############################################################################
async def create_org(
    client: AsyncClient, authed: None, fake: Faker
) -> Dict[str, Any]:
    response = await client.post(
        "/api/v1/organization",
        json={"name": fake.company()},
        headers=auth_header(authed),
    )
    assert response.status_code == 201
    return response.json()


async def create_agent(
    client: AsyncClient, authed: None, org_id: str
) -> Dict[str, Any]:
    response = await client.post(
        f"/api/v1/organization/{org_id}/agents",
        headers=auth_header(authed),
    )
    assert response.status_code == 201
    return response.json()


async def create_catalog(
    client: AsyncClient, authed: None, org_id: str
) -> Dict[str, Any]:
    ITEM = {
        "metadata": {
            "name": "Terminate a pod at random",
            "labels": ["gcp", "gke"]
        },
        "spec": {
            "provider": "chaostoolkit",
            "type": "action",
            "schema": {
                "arguments": [
                        {
                            "name": "ns",
                            "title": "Pod namespace",
                            "default": "default",
                            "type": "string",
                            "help": "",
                            "placeholder": "",
                            "required": False,
                        },
                        {
                            "name": "label_selector",
                            "title": "Pod label selector",
                            "type": "string",
                            "help": "",
                            "placeholder": "",
                            "required": False,
                        },
                        {
                            "name": "name",
                            "title": "Name of the pod",
                            "type": "string",
                            "help": "",
                            "placeholder": "",
                            "required": False,
                        },
                        {
                            "name": "all",
                            "title": "Terminate all matching pods",
                            "type": "boolean",
                            "help": "",
                            "placeholder": "",
                            "default": False,
                            "required": False,
                        },
                        {
                            "name": "rand",
                            "title": "Pick n pods at random",
                            "type": "boolean",
                            "help": "",
                            "placeholder": "",
                            "default": True,
                            "required": False,
                        },
                        {
                            "name": "grace_period",
                            "title": "Termination grace period",
                            "type": "number",
                            "help": "",
                            "placeholder": "",
                            "default": -1,
                            "required": False,
                        },
                ]
            },
            "template": {
                "type": "action",
                "name": "terminate-pod",
                "provider": {
                    "type": "python",
                    "module": "chaosk8s.pod.actions",
                    "func": "terminate_pods",
                },
            },
        },
    }

    response = await client.post(
        f"/api/v1/organization/{org_id}/catalogs",
        headers=auth_header(authed),
        json=ITEM,
    )
    assert response.status_code == 201
    return response.json()


async def create_snapshot(
    explore_gcp, client: AsyncClient, authed: None, org_id: str, agent_id: str,
) -> Dict[str, Any]:
    fake = Faker()
    discovered = Discovery(
        id="test",
        meta=Meta(
            name="snapshot-yesterday",
            display="GCP",
            kind="gcp",
            category="loadbalancer"
        ),
        resources=[
            Resource(
                id="lb",
                meta=GCPMeta(
                    kind="loadbalancer",
                    category="loadbalancer",
                    project="hello",
                    region="us-east1",
                    name="lb6",
                    display="load balancer 6"
                ),
                struct={
                    "labels": {'age': '2', 'app': 'consumer'}
                }
            )
        ]
    )
    explore_gcp.return_value = discovered

    authed_org, _, authed_token = authed
    headers = auth_header(authed)

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/integrations",
        headers=headers,
        json={
            "name": fake.name(),
            "provider": "snapshot",
            "vendor": "gcp",
            "environment": {
                "name": fake.name(),
                "envvars": [
                    {"var_name": "RELIABLY_EXPLORE_GCP", "value": "1"},
                    {"var_name": "GOOGLE_CLOUD_PROJECT_ID", "value": "fake"},
                    {"var_name": "GOOGLE_CLOUD_REGION", "value": "us-east1"},
                ],
                "secrets": [
                    {
                        "key": "creds",
                        "var_name": "GOOGLE_APPLICATION_CREDENTIALS",
                        "value": json.dumps({
                            "type": "service_account",
                            "project_id": "fakeproject",
                            "client_email": "a@example.com",
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                            "universe_domain": "googleapis.com",
                            "private_key_id": "085a3066f9a48b5dc241c4d13b4df7c83848f0d5",
                            "private_key": server_cert.private_key_pem.bytes().decode('utf-8')
                        })
                    }
                ],
            }
        }
    )
    assert response.status_code == 201
    intg = response.json()
    assert "id" in intg

    response = await client.post(
        f"/api/v1/organization/{org_id}/snapshots",
        headers=headers,
        json={
            "agent_id": agent_id,
            "integration_id": intg["id"]
        },
    )
    assert response.status_code == 201, response.json()
    snapshot = response.json()

    response = await client.get(
        f"/api/v1/organization/{org_id}/snapshots/refresh",
        headers=auth_header(authed),
    )
    assert response.status_code == 200

    return snapshot


async def refresh_snapshot(
    explore_gcp, client: AsyncClient, authed: None, org_id: str, agent_id: str,
) -> Dict[str, Any]:
    fake = Faker()
    discovered = Discovery(
        id="test",
        meta=Meta(
            name="snapshot-yesterday",
            display="GCP",
            kind="gcp",
            category="loadbalancer"
        ),
        resources=[
            Resource(
                id="lb",
                meta=GCPMeta(
                    kind="loadbalancer",
                    category="loadbalancer",
                    project="hello",
                    region="us-east1",
                    name="lb6",
                    display="load balancer 6"
                ),
                struct={
                    "labels": {'age': '3', 'app': 'consumer'}
                }
            )
        ]
    )
    explore_gcp.return_value = discovered

    authed_org, _, authed_token = authed
    headers = auth_header(authed)

    response = await client.post(
        f"/api/v1/organization/{org_id}/integrations",
        headers=headers,
        json={
            "name": fake.name(),
            "provider": "snapshot",
            "vendor": "gcp",
            "environment": {
                "name": fake.name(),
                "envvars": [
                    {"var_name": "RELIABLY_EXPLORE_GCP", "value": "1"},
                    {"var_name": "GOOGLE_CLOUD_PROJECT_ID", "value": "fake"},
                    {"var_name": "GOOGLE_CLOUD_REGION", "value": "us-east1"},
                ],
                "secrets": [
                    {
                        "key": "creds",
                        "var_name": "GOOGLE_APPLICATION_CREDENTIALS",
                        "value": json.dumps({
                            "type": "service_account",
                            "project_id": "fakeproject",
                            "client_email": "a@example.com",
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                            "universe_domain": "googleapis.com",
                            "private_key_id": "085a3066f9a48b5dc241c4d13b4df7c83848f0d5",
                            "private_key": server_cert.private_key_pem.bytes().decode('utf-8')
                        })
                    }
                ],
            }
        }
    )
    assert response.status_code == 201
    intg = response.json()
    assert "id" in intg

    response = await client.post(
        f"/api/v1/organization/{org_id}/snapshots",
        headers=headers,
        json={
            "agent_id": agent_id,
            "integration_id": intg["id"]
        },
    )
    assert response.status_code == 201, response.json()
    snapshot = response.json()

    response = await client.get(
        f"/api/v1/organization/{org_id}/snapshots/refresh",
        headers=auth_header(authed),
    )
    assert response.status_code == 200

    return snapshot


async def get_most_recent_snapshot_values(
    client: AsyncClient, authed: None, org_id: str
) -> Dict[str, Any]:
    response = await client.get(
        f"/api/v1/organization/{org_id}/snapshots/current",
        headers=auth_header(authed),
        params={
            "path": "$.resources.[?@.meta.kind=='loadbalancer'].struct.labels"
        },
    )
    assert response.status_code == 200
    return response.json()


async def build_experiment_from_catalog_and_snapshot(
    client: AsyncClient, authed: None, org_id: str
) -> Dict[str, Any]:
    response = await client.get(
        f"/api/v1/organization/{org_id}/catalogs/by/labels",
        params={"labels": ["gcp", "gke"]},
        headers=auth_header(authed),
    )
    assert response.status_code == 200
    items = response.json()

    action = items[0]
    template = deepcopy(action["manifest"]["spec"]["template"])

    values = await get_most_recent_snapshot_values(client, authed, org_id)

    template["provider"]["arguments"] = {"label_selector": values[0]}

    return {
        "title": "Terminate a random pod",
        "description": "n/a",
        "method": [template],
    }


def auth_header(authed: None) -> Dict[str, str]:
    _, _, authed_token = authed
    return {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}
