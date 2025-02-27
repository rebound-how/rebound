import uuid
from datetime import datetime, timedelta

import pytest
from faker import Faker
from lueur.models import Discovery, Meta

from reliably_app.database import SessionLocal
from reliably_app.snapshot import crud, schemas


@pytest.mark.anyio
async def test_get_snapshots_returns_nothing_when_no_snapshots_exist(
    stack_ready,
):
    org_id = uuid.uuid4()
    async with SessionLocal() as db:
        assert await crud.get_snapshots(db, org_id) == []


@pytest.mark.anyio
async def test_get_snapshots_return_all_snapshots(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    agent_id = str(uuid.uuid4())

    pl = schemas.SnapshotBase(
        org_id=org_id,
        user_id=user_id,
        agent_id=agent_id,
        snapshot=Discovery(
            id="test",
            meta=Meta(
                name="test",
                display="Test",
                kind="aws",
                category="loadbalancer"
            ),
            resources=[]
        )
    )

    async with SessionLocal() as db:
        snapshot = await crud.create_snapshot(db, org_id, user_id, agent_id, pl)
        assert snapshot.id is not None

    async with SessionLocal() as db:
        snapshots = await crud.get_snapshots(db, org_id)

    assert len(snapshots) == 1
    assert snapshots[0].id == snapshot.id
    assert str(snapshots[0].org_id) == org_id


@pytest.mark.anyio
async def test_count_snapshots(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    agent_id = str(uuid.uuid4())

    pl = schemas.SnapshotBase(
        org_id=org_id,
        user_id=user_id,
        agent_id=agent_id,
        snapshot=Discovery(
            id="test",
            meta=Meta(
                name="test",
                display="Test",
                kind="aws",
                category="loadbalancer"
            ),
            resources=[]
        )
    )

    async with SessionLocal() as db:
        snapshot = await crud.create_snapshot(db, org_id, user_id, agent_id, pl)
        assert snapshot.id is not None

    async with SessionLocal() as db:
        count = await crud.count_snapshots(db, org_id)

    assert count == 1


@pytest.mark.anyio
async def test_get_snapshot(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    agent_id = str(uuid.uuid4())

    pl = schemas.SnapshotBase(
        org_id=org_id,
        user_id=user_id,
        agent_id=agent_id,
        snapshot=Discovery(
            id="test",
            meta=Meta(
                name="test",
                display="Test",
                kind="aws",
                category="loadbalancer"
            ),
            resources=[]
        )
    )

    async with SessionLocal() as db:
        snapshot = await crud.create_snapshot(db, org_id, user_id, agent_id, pl)
        assert snapshot.id is not None

    async with SessionLocal() as db:
        pl = await crud.get_snapshot(db, snapshot.id)

    assert pl.id == snapshot.id
    assert str(pl.org_id) == org_id


@pytest.mark.anyio
async def test_get_snapshot_returns_nothing_when_snapshot_not_found(
    stack_ready,
):
    async with SessionLocal() as db:
        assert await crud.get_snapshot(db, uuid.uuid4()) is None


@pytest.mark.anyio
async def test_delete_snapshot(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    agent_id = str(uuid.uuid4())

    pl = schemas.SnapshotBase(
        org_id=org_id,
        user_id=user_id,
        agent_id=agent_id,
        snapshot=Discovery(
            id="test",
            meta=Meta(
                name="test",
                display="Test",
                kind="aws",
                category="loadbalancer"
            ),
            resources=[]
        )
    )

    async with SessionLocal() as db:
        snapshot = await crud.create_snapshot(db, org_id, user_id, agent_id, pl)
        assert snapshot.id is not None

    async with SessionLocal() as db:
        snapshot = await crud.get_snapshot(db, snapshot.id)
        assert snapshot is not None

    async with SessionLocal() as db:
        snapshots = await crud.get_snapshots(db, org_id)
        assert len(snapshots) == 1

    async with SessionLocal() as db:
        await crud.delete_snapshot(db, snapshot.id)

    async with SessionLocal() as db:
        snapshot = await crud.get_snapshot(db, snapshot.id)
        assert snapshot is None

    async with SessionLocal() as db:
        snapshots = await crud.get_snapshots(db, org_id)
        assert len(snapshots) == 0


@pytest.mark.anyio
async def test_does_snapshot_belong_to_org(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    agent_id = str(uuid.uuid4())

    pl = schemas.SnapshotBase(
        org_id=org_id,
        user_id=user_id,
        agent_id=agent_id,
        snapshot=Discovery(
            id="test",
            meta=Meta(
                name="test",
                display="Test",
                kind="aws",
                category="loadbalancer"
            ),
            resources=[]
        )
    )

    async with SessionLocal() as db:
        snapshot = await crud.create_snapshot(db, org_id, user_id, agent_id, pl)
        assert snapshot.id is not None

    async with SessionLocal() as db:
        assert (
            await crud.does_snapshot_belong_to_org(db, org_id, snapshot.id)
            is True
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_snapshot_belong_to_org(db, org_id, uuid.uuid4())
            is False
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_snapshot_belong_to_org(
                db, uuid.uuid4(), snapshot.id
            )
            is False
        )


@pytest.mark.anyio
async def test_set_snapshot(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    agent_id = str(uuid.uuid4())

    pl = schemas.SnapshotBase(
        org_id=org_id,
        user_id=user_id,
        agent_id=agent_id,
        snapshot=Discovery(
            id="test",
            meta=Meta(
                name="test",
                display="Test",
                kind="aws",
                category="loadbalancer"
            ),
            resources=[]
        )
    )

    async with SessionLocal() as db:
        snapshot = await crud.create_snapshot(db, org_id, user_id, agent_id, pl)
        assert snapshot.id is not None

    pl = schemas.SnapshotBase(
        org_id=org_id,
        user_id=user_id,
        agent_id=agent_id,
        snapshot=Discovery(
            id="test",
            meta=Meta(
                name="test",
                display="Test",
                kind="aws",
                category="loadbalancer"
            ),
            resources=[]
        )
    )

    async with SessionLocal() as db:
        snapshot = await crud.create_snapshot(db, org_id, user_id, agent_id, pl)
        assert snapshot.id is not None

    async with SessionLocal() as db:
        snapshot = await crud.get_latest_snapshot(db, org_id)
        assert snapshot is not None
