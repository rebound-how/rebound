import uuid

import pytest
import ujson
from faker import Faker

from reliably_app import account, agent, organization, plan, series
from reliably_app.database import SessionLocal
from reliably_app.execution import crud, schemas


@pytest.mark.anyio
async def test_get_executions_by_org_returns_nothing_when_no_executions_exist(
    stack_ready,
):
    org_id = uuid.uuid4()
    async with SessionLocal() as db:
        assert await crud.get_executions_by_org(db, org_id) == []


@pytest.mark.anyio
async def test_get_executions_by_exp_returns_nothing_when_no_executions_exist(
    stack_ready,
):
    exp_id = uuid.uuid4()
    async with SessionLocal() as db:
        assert await crud.get_executions_by_experiment(db, exp_id) == []


@pytest.mark.anyio
async def test_get_executions_by_experiment_returns_nothing_when_none_exists(
    stack_ready,
):
    plan_id = uuid.uuid4()
    async with SessionLocal() as db:
        assert await crud.get_executions_by_plan(db, plan_id) == []


@pytest.mark.anyio
async def test_get_executions_by_org_return_all_executions(
    stack_ready, fake: Faker
):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    dc = schemas.ExecutionCreate(result=ujson.dumps({"title": "hello world"}))

    async with SessionLocal() as db:
        exp = await crud.create_execution(db, org_id, exp_id, user_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        exps = await crud.get_executions_by_org(db, org_id)

    assert len(exps) == 1
    assert exps[0].id == exp.id
    assert str(exps[0].org_id) == org_id
    assert str(exps[0].experiment_id) == exp_id
    assert exps[0].plan_id is None
    assert exps[0].result == exp.result


@pytest.mark.anyio
async def test_get_executions_by_plan_return_all_executions(
    stack_ready, fake: Faker
):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    plan_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    dc = schemas.ExecutionCreate(
        result=ujson.dumps({"title": "hello world"}), plan_id=plan_id
    )

    async with SessionLocal() as db:
        exp = await crud.create_execution(db, org_id, exp_id, user_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        exps = await crud.get_executions_by_plan(db, plan_id)

    assert len(exps) == 1
    assert exps[0].id == exp.id
    assert str(exps[0].org_id) == org_id
    assert str(exps[0].experiment_id) == exp_id
    assert str(exps[0].plan_id) == plan_id
    assert exps[0].result == exp.result


@pytest.mark.anyio
async def test_get_executions_by_experiment_return_all_executions(
    stack_ready, fake: Faker
):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    dc = schemas.ExecutionCreate(result=ujson.dumps({"title": "hello world"}))

    async with SessionLocal() as db:
        exp = await crud.create_execution(db, org_id, exp_id, user_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        exps = await crud.get_executions_by_experiment(db, exp_id)

    assert len(exps) == 1
    assert exps[0].id == exp.id
    assert str(exps[0].org_id) == org_id
    assert str(exps[0].experiment_id) == exp_id
    assert exps[0].plan_id is None
    assert exps[0].result == exp.result


@pytest.mark.anyio
async def test_count_executions_by_org(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    dc = schemas.ExecutionCreate(result=ujson.dumps({"title": "hello world"}))

    async with SessionLocal() as db:
        exp = await crud.create_execution(db, org_id, exp_id, user_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        count = await crud.count_executions_by_org(db, org_id)

    assert count == 1


@pytest.mark.anyio
async def test_count_executions_by_plan(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    plan_id = str(uuid.uuid4())

    dc = schemas.ExecutionCreate(
        result=ujson.dumps({"title": "hello world"}), plan_id=plan_id
    )

    async with SessionLocal() as db:
        exp = await crud.create_execution(db, org_id, exp_id, user_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        count = await crud.count_executions_by_plan(db, plan_id)

    assert count == 1


@pytest.mark.anyio
async def test_count_executions_by_experiment(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    dc = schemas.ExecutionCreate(result=ujson.dumps({"title": "hello world"}))

    async with SessionLocal() as db:
        exp = await crud.create_execution(db, org_id, exp_id, user_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        count = await crud.count_executions_by_experiment(db, exp_id)

    assert count == 1


@pytest.mark.anyio
async def test_get_execution(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    dc = schemas.ExecutionCreate(result=ujson.dumps({"title": "hello world"}))

    async with SessionLocal() as db:
        exp = await crud.create_execution(db, org_id, exp_id, user_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        db_exp = await crud.get_execution(db, exp.id)

    assert db_exp.id == exp.id
    assert db_exp.org_id == org_id
    assert db_exp.result == exp.result


@pytest.mark.anyio
async def test_get_execution_returns_nothing_when_user_not_found(stack_ready):
    async with SessionLocal() as db:
        assert await crud.get_execution(db, uuid.uuid4()) is None


@pytest.mark.anyio
async def test_delete_execution(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    dc = schemas.ExecutionCreate(result=ujson.dumps({"title": "hello world"}))

    async with SessionLocal() as db:
        exp = await crud.create_execution(db, org_id, exp_id, user_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        exp = await crud.get_execution(db, exp.id)
        assert exp is not None

    async with SessionLocal() as db:
        exps = await crud.get_executions_by_org(db, org_id)
        assert len(exps) == 1

    async with SessionLocal() as db:
        await crud.delete_execution(db, exp.id)

    async with SessionLocal() as db:
        exp = await crud.get_execution(db, exp.id)
        assert exp is None

    async with SessionLocal() as db:
        exps = await crud.get_executions_by_org(db, org_id)
        assert len(exps) == 0


@pytest.mark.anyio
async def test_does_execution_belong_to_org(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    dc = schemas.ExecutionCreate(result=ujson.dumps({"title": "hello world"}))

    async with SessionLocal() as db:
        exp = await crud.create_execution(db, org_id, exp_id, user_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        assert (
            await crud.does_execution_belong_to_org(db, org_id, exp.id) is True
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_execution_belong_to_org(db, org_id, uuid.uuid4())
            is False
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_execution_belong_to_org(db, uuid.uuid4(), exp.id)
            is False
        )


@pytest.mark.anyio
async def test_is_execution_linked_to_experiment(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    dc = schemas.ExecutionCreate(result=ujson.dumps({"title": "hello world"}))

    async with SessionLocal() as db:
        exec = await crud.create_execution(db, org_id, exp_id, user_id, dc)
        assert exec.id is not None

    async with SessionLocal() as db:
        assert (
            await crud.is_execution_linked_to_experiment(db, exp_id, exec.id)
            is True
        )

    async with SessionLocal() as db:
        assert (
            await crud.is_execution_linked_to_experiment(
                db, uuid.uuid4(), exec.id
            )
            is False
        )

    async with SessionLocal() as db:
        assert (
            await crud.is_execution_linked_to_experiment(
                db, exp_id, uuid.uuid4()
            )
            is False
        )


@pytest.mark.anyio
async def test_set_user_state(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    plan_id = str(uuid.uuid4())

    dc = schemas.ExecutionCreate(
        result=ujson.dumps({"title": "hello world"}), plan_id=plan_id
    )

    async with SessionLocal() as db:
        xc = await crud.create_execution(db, org_id, exp_id, user_id, dc)
        assert xc.id is not None

    assert xc.user_state["current"] == "pending"

    s = {
        "current": "terminate",
        "skip_rollbacks": True,
    }
    async with SessionLocal() as db:
        await crud.set_user_state(db, org_id, xc.id, s)

    async with SessionLocal() as db:
        xc = await crud.get_execution(db, xc.id)
        assert xc.user_state == s


@pytest.mark.anyio
async def test_get_user_state(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    plan_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    dc = schemas.ExecutionCreate(
        result=ujson.dumps({"title": "hello world"}), plan_id=plan_id
    )

    async with SessionLocal() as db:
        xc = await crud.create_execution(db, org_id, exp_id, user_id, dc)
        assert xc.id is not None

    assert xc.user_state["current"] == "pending"

    s = {
        "current": "terminate",
        "skip_rollbacks": True,
    }
    async with SessionLocal() as db:
        state = await crud.get_user_state(db, org_id, xc.id)
        assert state["current"] == "pending"

    async with SessionLocal() as db:
        await crud.set_user_state(db, org_id, xc.id, s)

    async with SessionLocal() as db:
        state = await crud.get_user_state(db, org_id, xc.id)
        assert state == s


@pytest.mark.anyio
async def test_get_execution_without_log(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    dc = schemas.ExecutionCreate(result=ujson.dumps({"title": "hello world"}))

    async with SessionLocal() as db:
        exp = await crud.create_execution(db, org_id, exp_id, user_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        db_exp = await crud.get_execution_without_log(db, exp.id)

    assert db_exp.id == exp.id
    assert db_exp.org_id == org_id
    assert db_exp.result == exp.result

    with pytest.raises(AttributeError):
        db_exp.log


@pytest.mark.anyio
async def test_get_execution_without_log_nor_journal(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    dc = schemas.ExecutionCreate(result=ujson.dumps({"title": "hello world"}))

    async with SessionLocal() as db:
        exp = await crud.create_execution(db, org_id, exp_id, user_id, dc)
        assert exp.id is not None

    async with SessionLocal() as db:
        db_exp = await crud.get_execution_without_log_nor_journal(db, exp.id)

    assert db_exp.id == exp.id
    assert db_exp.org_id == org_id

    with pytest.raises(AttributeError):
        db_exp.log

    with pytest.raises(AttributeError):
        db_exp.result


@pytest.mark.anyio
async def test_compute_execution_metrics(stack_ready, fake: Faker):
    exp_id = str(uuid.uuid4())
    dep_id = str(uuid.uuid4())

    name = fake.company()
    o = organization.schemas.OrganizationCreate(name=name)

    async with SessionLocal() as d2:
        org = await organization.crud.create_org(d2, o)

    org_id = org.id

    username = fake.name()
    email = fake.company_email()

    u = account.schemas.UserCreate(
        username=username, email=email, openid=account.schemas.UserInfo({"sub": "xyz"})
    )

    async with SessionLocal() as db:
        user = await account.crud.create_user(db, u)
        assert user.id is not None

    agt = await agent.crud.create_user_agent(org, user.id, True)

    pl = plan.schemas.PlanCreate(
        title=fake.sentence(nb_words=5),
        environment=plan.schemas.PlanGitHubEnvironment(name="myenv"),
        deployment=plan.schemas.PlanDeployment(deployment_id=dep_id),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, pl)
        assert p.id is not None

    dc = schemas.ExecutionCreate(result=ujson.dumps({"title": "hello world"}), plan_id=p.id)

    async with SessionLocal() as db:
        xc = await crud.create_execution(db, org_id, exp_id, user.id, dc)
        assert xc.id is not None

    s = schemas.ExecutionCreate(
        result={
            "status": "completed",
            "deviated": True,
            "duration": 1.78,
            "experiment": {
                "contributions": {
                    "availability": "high",
                    "latency": "low"
                }
            }
        },
        plan_id=p.id
    )
    async with SessionLocal() as db:
        await crud.update_execution_result(db, org_id, exp_id, xc.id, s)

    async with SessionLocal() as db:
        metrics = await crud.compute_metrics(db, org_id)
        series.schemas.ExecutionMetrics(distributions=metrics)

    print(metrics)