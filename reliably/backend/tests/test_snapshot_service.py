import json
import uuid
from unittest.mock import patch

import pytest
import trustme
from faker import Faker
from lueur.models import Discovery, Meta, GCPMeta, Resource
from httpx import AsyncClient

from reliably_app import snapshot
from reliably_app.database import SessionLocal

ca = trustme.CA()
server_cert = ca.issue_cert("example.com")


@pytest.mark.anyio
@patch("reliably_app.snapshot.tasks.snapshot_gcp.explore", autospec=True)
async def test_create_snapshot(
    explore_gcp, client: AsyncClient, authed: None, fake: Faker
) -> None:
    explore_gcp.return_value = Discovery(
        id="test",
        meta=Meta(
            name="snapshot-yesterday",
            display="GCP",
            kind="gcp",
            category="loadbalancer"
        ),
        resources=[]
    )

    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

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
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201
    agent = response.json()
    assert "id" in agent

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots",
        headers=headers,
        json={
            "agent_id": agent["id"],
            "integration_id": intg["id"]
        },
    )
    assert response.status_code == 201, response.json()


@pytest.mark.anyio
async def test_cannot_get_invalid_snapshot(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/{str(uuid.uuid4())}",  # noqa
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
@patch("reliably_app.snapshot.tasks.snapshot_gcp.explore", autospec=True)
async def test_list_snapshots(
    explore_gcp, client: AsyncClient, authed: None, fake: Faker
) -> None:
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
                struct={}
            )
        ]
    )
    explore_gcp.return_value = discovered

    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

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
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201
    agent = response.json()
    assert "id" in agent

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots",
        headers=headers,
        json={
            "agent_id": agent["id"],
            "integration_id": intg["id"]
        },
    )
    assert response.status_code == 201, response.json()
    snapshot = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/refresh",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots",
        headers=headers,
    )
    assert response.status_code == 200
    snapshots = response.json()

    assert snapshots["count"] == 2
    assert len(snapshots["items"]) == 2


@pytest.mark.anyio
@patch("reliably_app.snapshot.tasks.snapshot_gcp.explore", autospec=True)
async def test_paginate_snapshot_resources(
    explore_gcp, client: AsyncClient, authed: None, fake: Faker
) -> None:
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
                struct={}
            )
        ]
    )
    explore_gcp.return_value = discovered

    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

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
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201
    agent = response.json()
    assert "id" in agent

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots",
        headers=headers,
        json={
            "agent_id": agent["id"],
            "integration_id": intg["id"]
        },
    )
    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots",
        headers=headers,
        params={"limit": 1},
    )
    assert response.status_code == 200, response.json()
    snapshots = response.json()

    # we haven't refreshed once yet
    assert snapshots["count"] == 0
    assert len(snapshots["items"]) == 0

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/refresh",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots",
        headers=headers,
        params={"limit": 1},
    )
    assert response.status_code == 200, response.json()
    snapshots = response.json()

    assert snapshots["count"] == 2
    assert len(snapshots["items"]) == 1

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/latest",
        headers=headers,
    )
    assert response.status_code == 200
    snapshot = response.json()

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/{snapshot['id']}",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots?page=2",
        headers=headers,
    )
    assert response.status_code == 200
    snapshots = response.json()

    assert snapshots["count"] == 0
    assert len(snapshots["items"]) == 0


@pytest.mark.anyio
@patch("reliably_app.snapshot.tasks.snapshot_gcp.explore", autospec=True)
async def test_delete_snapshot(
    explore_gcp, client: AsyncClient, authed: None, fake: Faker
) -> None:
    explore_gcp.return_value = Discovery(
        id="test",
        meta=Meta(
            name="snapshot-yesterday",
            display="GCP",
            kind="gcp",
            category="loadbalancer"
        ),
        resources=[]
    )

    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

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
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201
    agent = response.json()
    assert "id" in agent

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots",
        headers=headers,
        json={
            "agent_id": agent["id"],
            "integration_id": intg["id"]
        },
    )
    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/refresh",
        headers=headers,
    )
    assert response.status_code == 200
    snapshot = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/latest",
        headers=headers,
    )
    assert response.status_code == 200
    snapshot = response.json()

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/{snapshot['id']}",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/{snapshot['id']}",
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
@patch("reliably_app.snapshot.tasks.snapshot_gcp.explore", autospec=True)
async def test_cannot_get_snapshot_from_another_org(
    explore_gcp, client: AsyncClient, authed: None, fake: Faker
) -> None:
    explore_gcp.return_value = Discovery(
        id="test",
        meta=Meta(
            name="snapshot-yesterday",
            display="GCP",
            kind="gcp",
            category="loadbalancer"
        ),
        resources=[]
    )

    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

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
    assert "id" in agent

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots",
        headers=headers,
        json={
            "agent_id": agent["id"],
            "integration_id": intg["id"]
        },
    )
    assert response.status_code == 201
    snapshot = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/refresh",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/latest",
        headers=headers,
    )
    assert response.status_code == 200
    snapshot = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(org['id'])}/snapshots/{snapshot['id']}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/{snapshot['id']}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
@patch("reliably_app.snapshot.tasks.snapshot_gcp.explore", autospec=True)
async def test_cannot_delete_snapshot_from_another_org(
    explore_gcp, client: AsyncClient, authed: None, fake: Faker
) -> None:
    explore_gcp.return_value = Discovery(
        id="test",
        meta=Meta(
            name="snapshot-yesterday",
            display="GCP",
            kind="gcp",
            category="loadbalancer"
        ),
        resources=[]
    )

    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    name = fake.company()
    response = await client.post(
        "/api/v1/organization", json={"name": name}, headers=headers
    )
    assert response.status_code == 201
    org = response.json()

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
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201
    agent = response.json()
    assert "id" in agent

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots",
        headers=headers,
        json={
            "agent_id": agent["id"],
            "integration_id": intg["id"]
        },
    )
    assert response.status_code == 201
    snapshot = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/refresh",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/latest",
        headers=headers,
    )
    assert response.status_code == 200
    snapshot = response.json()

    response = await client.delete(
        f"/api/v1/organization/{org['id']}/snapshots/{snapshot['id']}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/{snapshot['id']}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_snapshot_page_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots?page=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_snapshot_limit_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots?limit=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_snapshot_limit_cannot_be_greater_than_10(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots?limit=20",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
@patch("reliably_app.snapshot.tasks.snapshot_gcp.explore", autospec=True)
async def test_get_latest_snapshot(
    explore_gcp, client: AsyncClient, authed: None, fake: Faker
) -> None:
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
                struct={}
            )
        ]
    )
    explore_gcp.return_value = discovered

    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

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
        f"/api/v1/organization/{str(authed_org.id)}/agents",
        headers=headers,
    )
    assert response.status_code == 201
    agent = response.json()
    assert "id" in agent

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots",
        headers=headers,
        json={
            "agent_id": agent["id"],
            "integration_id": intg["id"]
        },
    )
    assert response.status_code == 201, response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/refresh",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/latest",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/snapshots/current",
        headers=headers,
        params={
            "path": "$.resources[?@.meta.kind=='loadbalancer'].meta.name"
        },
    )
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2  # explore gcp runs once without region and once with
    assert items[0] == "lb6"
