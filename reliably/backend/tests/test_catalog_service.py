import uuid
from copy import deepcopy

import pytest
from faker import Faker
from httpx import AsyncClient

ITEM = {
    "metadata": {
        "name": "Terminate a pod at random",
        "labels": ["gcp", "gke"],
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
                        "required": False,
                        "help": "",
                        "placeholder": "",
                    },
                    {
                        "name": "label_selector",
                        "title": "Pod label selector",
                        "type": "string",
                        "required": False,
                        "help": "",
                        "placeholder": "",
                    },
                    {
                        "name": "name",
                        "title": "Name of the pod",
                        "type": "string",
                        "required": False,
                        "help": "",
                        "placeholder": "",
                    },
                    {
                        "name": "all",
                        "title": "Terminate all matching pods",
                        "type": "boolean",
                        "default": False,
                        "required": False,
                        "help": "",
                        "placeholder": "",
                    },
                    {
                        "name": "rand",
                        "title": "Pick n pods at random",
                        "type": "boolean",
                        "default": True,
                        "required": False,
                        "help": "",
                        "placeholder": "",
                    },
                    {
                        "name": "grace_period",
                        "title": "Termination grace period (-1 means infinite)",
                        "type": "number",
                        "default": -1,
                        "required": False,
                        "help": "",
                        "placeholder": "",
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

STARTER_ITEM_DEF = {
    "metadata": {
        "name": "Terminate a pod at random",
        "labels": ["gcp", "gke"],
    },
    "spec": {
        "provider": "reliably/starter-definition",
        "schema": {
            "arguments": [
                    {
                        "name": "ns",
                        "title": "Pod namespace",
                        "default": "default",
                        "type": "string",
                        "required": False,
                        "help": "",
                        "placeholder": "",
                    },
                    {
                        "name": "label_selector",
                        "title": "Pod label selector",
                        "type": "string",
                        "required": False,
                        "help": "",
                        "placeholder": "",
                    },
                    {
                        "name": "name",
                        "title": "Name of the pod",
                        "type": "string",
                        "required": False,
                        "help": "",
                        "placeholder": "",
                    },
                    {
                        "name": "all",
                        "title": "Terminate all matching pods",
                        "type": "boolean",
                        "default": False,
                        "required": False,
                        "help": "",
                        "placeholder": "",
                    },
                    {
                        "name": "rand",
                        "title": "Pick n pods at random",
                        "type": "boolean",
                        "default": True,
                        "required": False,
                        "help": "",
                        "placeholder": "",
                    },
                    {
                        "name": "grace_period",
                        "title": "Termination grace period (-1 means infinite)",
                        "type": "number",
                        "default": -1,
                        "required": False,
                        "help": "",
                        "placeholder": "",
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


STARTER_ITEM_CARD = {
    "metadata": {
        "name": "Check SLO",
        "labels": ["gcp", "gke"],
    },
    "spec": {
        "provider": "reliably/starter-card",
        "definition_id": "",
        "content": "hello there"
    }
}


@pytest.mark.anyio
async def test_create_catalog_item(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs",
        headers=headers,
        json=ITEM,
    )
    assert response.status_code == 201, response.json()
    catalog = response.json()
    assert "id" in catalog


@pytest.mark.anyio
async def test_create_catalog_starter_item(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs",
        headers=headers,
        json=STARTER_ITEM_DEF,
    )
    assert response.status_code == 201, response.json()
    catalog = response.json()
    item_id = catalog["id"]

    s = deepcopy(STARTER_ITEM_CARD)
    s["spec"]["definition_id"] = item_id

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs",
        headers=headers,
        json=s,
    )
    assert response.status_code == 201, response.json()
    catalog = response.json()
    assert "id" in catalog
    starter_item_id = catalog["id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs",
        headers=headers,
        params={"provider": "reliably/starter-card"}
    )
    assert response.status_code == 200
    catalogs = response.json()

    assert catalogs["count"] == 1
    assert len(catalogs["items"]) == 1
    assert catalogs["items"][0]["id"] == starter_item_id

    linked_item_id = catalogs["items"][0]["manifest"]["spec"]["definition_id"]

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs/{linked_item_id}",
        headers=headers,
        params={"item_type": "reliably/starter-card"}
    )
    assert response.status_code == 200
    item = response.json()
    assert item["id"] == item_id


@pytest.mark.anyio
async def test_cannot_get_invalid_catalog_item(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs/{str(uuid.uuid4())}",  # noqa
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_list_catalog_items(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs",
        headers=headers,
        json=ITEM,
    )
    assert response.status_code == 201
    catalog = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs",
        headers=headers,
    )
    assert response.status_code == 200
    catalogs = response.json()

    assert catalogs["count"] == 1
    assert len(catalogs["items"]) == 1
    assert catalogs["items"][0]["id"] == catalog["id"]


@pytest.mark.anyio
async def test_paginate_catalog_items(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs",
        headers=headers,
        json=ITEM,
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs",
        headers=headers,
        json=ITEM,
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs",
        headers=headers,
        json=ITEM,
    )
    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs",
        headers=headers,
        params={"limit": 1},
    )
    assert response.status_code == 200, response.json()
    catalogs = response.json()

    assert catalogs["count"] == 3
    assert len(catalogs["items"]) == 1

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs?page=2",
        headers=headers,
    )
    assert response.status_code == 200
    catalogs = response.json()

    assert catalogs["count"] == 3
    assert len(catalogs["items"]) == 0


@pytest.mark.anyio
async def test_delete_catalog_item(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs",
        headers=headers,
        json=ITEM,
    )
    assert response.status_code == 201
    catalog = response.json()
    catalog_id = catalog["id"]

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs/{catalog_id}",
        headers=headers,
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs/{catalog_id}",
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_cannot_get_catalog_item_from_another_org(
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
        f"/api/v1/organization/{str(authed_org.id)}/catalogs",
        headers=headers,
        json=ITEM,
    )
    assert response.status_code == 201
    catalog = response.json()

    response = await client.get(
        f"/api/v1/organization/{str(org['id'])}/catalogs/{catalog['id']}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs/{catalog['id']}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_cannot_delete_catalog_item_from_another_org(
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
        f"/api/v1/organization/{str(authed_org.id)}/catalogs",
        headers=headers,
        json=ITEM,
    )
    assert response.status_code == 201, response.json()
    catalog = response.json()

    response = await client.delete(
        f"/api/v1/organization/{str(org['id'])}/catalogs/{catalog['id']}",
        headers=headers,
    )
    assert response.status_code == 404

    response = await client.delete(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs/{catalog['id']}",
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_catalog_items_page_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs?page=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_catalog_items_limit_must_be_positive_or_zero(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs?limit=-1",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_catalog_items_limit_cannot_be_greater_than_10(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs?limit=20",
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_catalog_items_by_tags(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs",
        headers=headers,
        json=ITEM,
    )
    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs/by/labels",
        params={"labels": ["gcp", "gke"]},
        headers=headers,
    )
    assert response.status_code == 200, response.json()
    items = response.json()

    assert len(items) == 1


@pytest.mark.anyio
async def test_get_catalog_items_labels(
    client: AsyncClient, authed: None, fake: Faker
) -> None:
    authed_org, _, authed_token = authed
    headers = {"Authorization": f"Bearer {authed_token.token.decode('utf-8')}"}

    response = await client.post(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs",
        headers=headers,
        json=ITEM,
    )
    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/organization/{str(authed_org.id)}/catalogs/labels",
        headers=headers,
    )
    assert response.status_code == 200, response.json()
    items = response.json()
    assert items == ["gke", "gcp"]
