import uuid

import pytest
import ujson
from faker import Faker

from reliably_app import execution
from reliably_app.database import SessionLocal
from reliably_app.experiment import crud, schemas


@pytest.mark.anyio
async def test_get_experiments_returns_nothing_when_no_experiments_exist(
    stack_ready,
):
    org_id = uuid.uuid4()
    async with SessionLocal() as db:
        assert await crud.get_experiments(db, org_id) == []


@pytest.mark.anyio
async def test_get_experiments_return_all_experiments(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())

    dc = schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        exp = await crud.create_experiment(db, org_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        exps = await crud.get_experiments(db, org_id)

    assert len(exps) == 1
    assert exps[0].id == exp.id
    assert str(exps[0].org_id) == org_id
    assert exps[0].definition == exp.definition


@pytest.mark.anyio
async def test_count_experiments(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())

    dc = schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        exp = await crud.create_experiment(db, org_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        count = await crud.count_experiments(db, org_id)

    assert count == 1


@pytest.mark.anyio
async def test_get_experiment(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    dc = schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        exp = await crud.create_experiment(db, org_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        db_exp = await crud.get_experiment(db, exp.id)

    assert db_exp.id == exp.id
    assert db_exp.org_id == org_id
    assert db_exp.definition == exp.definition
    assert "controls" in db_exp.definition
    assert db_exp.definition["controls"][0]["name"] == "reliably"


@pytest.mark.anyio
async def test_get_user_returns_nothing_when_user_not_found(stack_ready):
    async with SessionLocal() as db:
        assert await crud.get_experiment(db, uuid.uuid4()) is None


@pytest.mark.anyio
async def test_delete_experiment(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())

    dc = schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        exp = await crud.create_experiment(db, org_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        exp = await crud.get_experiment(db, exp.id)
        assert exp is not None

    async with SessionLocal() as db:
        exps = await crud.get_experiments(db, org_id)
        assert len(exps) == 1

    async with SessionLocal() as db:
        await crud.delete_experiment(db, exp.id)

    async with SessionLocal() as db:
        exp = await crud.get_experiment(db, exp.id)
        assert exp is None

    async with SessionLocal() as db:
        exps = await crud.get_experiments(db, org_id)
        assert len(exps) == 0


@pytest.mark.anyio
async def test_does_experiment_belong_to_org(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())

    dc = schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        exp = await crud.create_experiment(db, org_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        assert (
            await crud.does_experiment_belong_to_org(db, org_id, exp.id) is True
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_experiment_belong_to_org(db, org_id, uuid.uuid4())
            is False
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_experiment_belong_to_org(db, uuid.uuid4(), exp.id)
            is False
        )


@pytest.mark.anyio
async def test_get_all_experiments(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())

    dc = schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        exp = await crud.create_experiment(db, org_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        exps = await crud.get_all_experiments(db, org_id)

    assert len(exps) == 1
    assert exps[0]["id"] == exp.id
    assert exps[0]["title"] == "hello world"


@pytest.mark.anyio
async def test_get_all_experiments_are_ordered_by_title(
    stack_ready, fake: Faker
):
    org_id = str(uuid.uuid4())

    dc = schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        exp = await crud.create_experiment(db, org_id, dc)
        assert exp.id is not None

    dc = schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "a beautiful morning"})
    )

    async with SessionLocal() as db:
        exp = await crud.create_experiment(db, org_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        exps = await crud.get_all_experiments(db, org_id)

    assert len(exps) == 2
    assert exps[0]["title"] == "a beautiful morning"
    assert exps[1]["title"] == "hello world"


@pytest.mark.anyio
async def test_get_experiments_and_executions_summary(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    dc = schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        exp = await crud.create_experiment(db, org_id, dc)
        assert exp.id is not None
        x1_id = str(exp.id)

    dc = schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "bonjour monde"})
    )

    async with SessionLocal() as db:
        exp = await crud.create_experiment(db, org_id, dc)
        assert exp.id is not None
        x2_id = str(exp.id)

    dc = execution.schemas.ExecutionCreate(
        result=ujson.dumps({"status": "deviated"})
    )

    async with SessionLocal() as db:
        exec = await execution.crud.create_execution(db, org_id, x1_id, user_id, dc)
        assert exec.id is not None

    dc = execution.schemas.ExecutionCreate(
        result=ujson.dumps({"status": "failed"})
    )

    async with SessionLocal() as db:
        exec = await execution.crud.create_execution(db, org_id, x1_id, user_id, dc)
        assert exec.id is not None

    dc = execution.schemas.ExecutionCreate(
        result=ujson.dumps({"status": "running"})
    )

    async with SessionLocal() as db:
        exec = await execution.crud.create_execution(db, org_id, x2_id, user_id, dc)
        assert exec.id is not None

    async with SessionLocal() as db:
        results = await crud.get_experiments_summary(db, org_id)
        assert len(results) == 2
        for r in results:
            assert r["id"] in (x1_id, x2_id)
            assert r["title"] in ("bonjour monde", "hello world")
            assert r["last_statuses"] in (["running"], ["failed", "deviated"])
