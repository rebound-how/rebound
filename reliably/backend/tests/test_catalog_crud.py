import uuid

import pytest
from faker import Faker

from reliably_app.catalog import crud, schemas
from reliably_app.database import SessionLocal

CREATE = schemas.CatalogItemCreate(
    metadata=schemas.CatalogItemMetadata(
        name="Terminate a pod at random",
        labels=["gcp", "gke"],
    ),
    spec=schemas.CatalogChaostoolkitItemSpec(
        provider="chaostoolkit",
        type="action",
        schema=schemas.CatalogChaostoolkitItemSpecSchema(
            arguments=[
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
        ),
        template={
            "type": "action",
            "name": "terminate-pod",
            "provider": {
                "type": "python",
                "module": "chaosk8s.pod.actions",
                "func": "terminate_pods",
            },
        },
    ),
)


@pytest.mark.anyio
async def test_get_catalogs_returns_nothing_when_no_catalogs_exist(stack_ready):
    org_id = uuid.uuid4()
    async with SessionLocal() as db:
        assert await crud.get_catalogs(db, org_id, "chaostoolkit") == []


@pytest.mark.anyio
async def test_get_catalogs_return_all_catalogs(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())

    async with SessionLocal() as db:
        catalog = await crud.create_catalog(db, org_id, CREATE)
        assert catalog.id is not None

    async with SessionLocal() as db:
        catalogs = await crud.get_catalogs(db, org_id, "chaostoolkit")

    assert len(catalogs) == 1
    assert catalogs[0].id == catalog.id
    assert str(catalogs[0].org_id) == org_id


@pytest.mark.anyio
async def test_count_catalogs(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())

    async with SessionLocal() as db:
        catalog = await crud.create_catalog(db, org_id, CREATE)
        assert catalog.id is not None

    async with SessionLocal() as db:
        count = await crud.count_catalogs(db, org_id, "chaostoolkit")

    assert count == 1


@pytest.mark.anyio
async def test_get_catalog(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())

    async with SessionLocal() as db:
        catalog = await crud.create_catalog(db, org_id, CREATE)
        assert catalog.id is not None

    async with SessionLocal() as db:
        pl = await crud.get_catalog(db, catalog.id)

    assert pl.id == catalog.id
    assert str(pl.org_id) == org_id


@pytest.mark.anyio
async def test_get_catalog_returns_nothing_when_catalog_not_found(stack_ready):
    async with SessionLocal() as db:
        assert await crud.get_catalog(db, uuid.uuid4()) is None


@pytest.mark.anyio
async def test_delete_catalog(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())

    async with SessionLocal() as db:
        catalog = await crud.create_catalog(db, org_id, CREATE)
        assert catalog.id is not None

    async with SessionLocal() as db:
        catalog = await crud.get_catalog(db, catalog.id)
        assert catalog is not None

    async with SessionLocal() as db:
        catalogs = await crud.get_catalogs(db, org_id, "chaostoolkit")
        assert len(catalogs) == 1

    async with SessionLocal() as db:
        await crud.delete_catalog(db, catalog.id)

    async with SessionLocal() as db:
        catalog = await crud.get_catalog(db, catalog.id)
        assert catalog is None

    async with SessionLocal() as db:
        catalogs = await crud.get_catalogs(db, org_id, "chaostoolkit")
        assert len(catalogs) == 0


@pytest.mark.anyio
async def test_does_catalog_belong_to_org(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())

    async with SessionLocal() as db:
        catalog = await crud.create_catalog(db, org_id, CREATE)
        assert catalog.id is not None

    async with SessionLocal() as db:
        assert (
            await crud.does_catalog_belong_to_org(db, org_id, catalog.id)
            is True
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_catalog_belong_to_org(db, org_id, uuid.uuid4())
            is False
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_catalog_belong_to_org(db, uuid.uuid4(), catalog.id)
            is False
        )


@pytest.mark.anyio
async def test_get_catalog_items_by_labels(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())

    async with SessionLocal() as db:
        catalog = await crud.create_catalog(db, org_id, CREATE)
        assert catalog.id is not None

    async with SessionLocal() as db:
        items = await crud.get_catalog_items_by_labels(db, org_id, ["gcp"])

    assert len(items) == 1
    assert items[0].id == catalog.id
    assert str(items[0].org_id) == org_id

    async with SessionLocal() as db:
        items = await crud.get_catalog_items_by_labels(db, org_id, ["gke", "gcp"])

    assert len(items) == 1
    assert items[0].id == catalog.id
    assert str(items[0].org_id) == org_id

    async with SessionLocal() as db:
        items = await crud.get_catalog_items_by_labels(db, org_id, ["aws"])

    assert len(items) == 0


@pytest.mark.anyio
async def test_get_catalog_items_labels(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())

    async with SessionLocal() as db:
        catalog = await crud.create_catalog(db, org_id, CREATE)
        assert catalog.id is not None

    async with SessionLocal() as db:
        assert await crud.get_catalog_items_labels(db, org_id) == ["gke", "gcp"]
