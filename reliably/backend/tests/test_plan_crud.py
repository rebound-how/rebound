import uuid

import pytest
from faker import Faker

from reliably_app.database import SessionLocal
from reliably_app.plan import crud, schemas


@pytest.mark.anyio
async def test_get_plans_returns_nothing_when_no_plans_exist(stack_ready):
    org_id = uuid.uuid4()
    async with SessionLocal() as db:
        assert await crud.get_plans(db, org_id) == []


@pytest.mark.anyio
async def test_get_plans_return_all_plans(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    dep_id = str(uuid.uuid4())
    env_name = fake.name()

    pl = schemas.PlanCreate(
        environment=schemas.PlanGitHubEnvironment(name=env_name),
        deployment=schemas.PlanDeployment(deployment_id=dep_id),
        schedule=schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        plan = await crud.create_plan(db, org_id, pl)
        assert plan.id is not None

    async with SessionLocal() as db:
        plans = await crud.get_plans(db, org_id)

    assert len(plans) == 1
    assert plans[0].id == plan.id
    assert str(plans[0].org_id) == org_id


@pytest.mark.anyio
async def test_count_plans(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    dep_id = str(uuid.uuid4())
    env_name = fake.name()

    pl = schemas.PlanCreate(
        environment=schemas.PlanGitHubEnvironment(name=env_name),
        deployment=schemas.PlanDeployment(deployment_id=dep_id),
        schedule=schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        plan = await crud.create_plan(db, org_id, pl)
        assert plan.id is not None

    async with SessionLocal() as db:
        count = await crud.count_plans(db, org_id)

    assert count == 1


@pytest.mark.anyio
async def test_get_plan(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    dep_id = str(uuid.uuid4())
    env_name = fake.name()

    pl = schemas.PlanCreate(
        environment=schemas.PlanGitHubEnvironment(name=env_name),
        deployment=schemas.PlanDeployment(deployment_id=dep_id),
        schedule=schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        plan = await crud.create_plan(db, org_id, pl)
        assert plan.id is not None

    async with SessionLocal() as db:
        pl = await crud.get_plan(db, plan.id)

    assert pl.id == plan.id
    assert str(pl.org_id) == org_id


@pytest.mark.anyio
async def test_get_plan_returns_nothing_when_plan_not_found(stack_ready):
    async with SessionLocal() as db:
        assert await crud.get_plan(db, uuid.uuid4()) is None


@pytest.mark.anyio
async def test_delete_plan(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    dep_id = str(uuid.uuid4())
    env_name = fake.name()

    pl = schemas.PlanCreate(
        environment=schemas.PlanGitHubEnvironment(name=env_name),
        deployment=schemas.PlanDeployment(deployment_id=dep_id),
        schedule=schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        plan = await crud.create_plan(db, org_id, pl)
        assert plan.id is not None

    async with SessionLocal() as db:
        plan = await crud.get_plan(db, plan.id)
        assert plan is not None

    async with SessionLocal() as db:
        plans = await crud.get_plans(db, org_id)
        assert len(plans) == 1

    async with SessionLocal() as db:
        await crud.delete_plan(db, plan.id)

    async with SessionLocal() as db:
        plan = await crud.get_plan(db, plan.id)
        assert plan is None

    async with SessionLocal() as db:
        plans = await crud.get_plans(db, org_id)
        assert len(plans) == 0


@pytest.mark.anyio
async def test_does_plan_belong_to_org(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    dep_id = str(uuid.uuid4())
    env_name = fake.name()

    pl = schemas.PlanCreate(
        environment=schemas.PlanGitHubEnvironment(name=env_name),
        deployment=schemas.PlanDeployment(deployment_id=dep_id),
        schedule=schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        plan = await crud.create_plan(db, org_id, pl)
        assert plan.id is not None

    async with SessionLocal() as db:
        assert await crud.does_plan_belong_to_org(db, org_id, plan.id) is True

    async with SessionLocal() as db:
        assert (
            await crud.does_plan_belong_to_org(db, org_id, uuid.uuid4())
            is False
        )

    async with SessionLocal() as db:
        assert (
            await crud.does_plan_belong_to_org(db, uuid.uuid4(), plan.id)
            is False
        )


@pytest.mark.anyio
async def test_get_plan_by_ref(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    dep_id = str(uuid.uuid4())
    env_name = fake.name()

    pl = schemas.PlanCreate(
        environment=schemas.PlanGitHubEnvironment(name=env_name),
        deployment=schemas.PlanDeployment(deployment_id=dep_id),
        schedule=schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        plan = await crud.create_plan(db, org_id, pl)
        assert plan.id is not None

    async with SessionLocal() as db:
        pl = await crud.get_plan_by_ref(db, org_id, plan.ref)

    assert pl.id == plan.id

    async with SessionLocal() as db:
        assert await crud.get_plan_by_ref(db, org_id, "xwyz") is None


@pytest.mark.anyio
async def test_get_plans_using_deployment(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    dep_id = str(uuid.uuid4())
    env_name = fake.name()

    pl = schemas.PlanCreate(
        environment=schemas.PlanGitHubEnvironment(name=env_name),
        deployment=schemas.PlanDeployment(deployment_id=dep_id),
        schedule=schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        plan = await crud.create_plan(db, org_id, pl)
        assert plan.id is not None

    async with SessionLocal() as db:
        plans = await crud.get_plans_using_deployment(db, org_id, dep_id)

        assert len(plans) == 1
        assert str(plans[0]) == str(plan.id)

    async with SessionLocal() as db:
        await crud.set_status(db, plan.id, schemas.PlanStatus.deleted)

    async with SessionLocal() as db:
        plans = await crud.get_plans_using_deployment(db, org_id, dep_id)

        assert len(plans) == 0


@pytest.mark.anyio
async def test_is_deployment_used_by_any_plan(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    dep_id = str(uuid.uuid4())
    env_name = fake.name()

    pl = schemas.PlanCreate(
        environment=schemas.PlanGitHubEnvironment(name=env_name),
        deployment=schemas.PlanDeployment(deployment_id=dep_id),
        schedule=schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        plan = await crud.create_plan(db, org_id, pl)
        assert plan.id is not None

    async with SessionLocal() as db:
        used = await crud.is_deployment_used_by_any_plan(db, org_id, dep_id)
        assert used is True

    async with SessionLocal() as db:
        await crud.set_status(db, plan.id, schemas.PlanStatus.deleted)

    async with SessionLocal() as db:
        used = await crud.is_deployment_used_by_any_plan(db, org_id, dep_id)
        assert used is False


@pytest.mark.anyio
async def test_get_plans_using_experiment(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    dep_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    exp2_id = str(uuid.uuid4())
    env_name = fake.name()

    pl = schemas.PlanCreate(
        environment=schemas.PlanGitHubEnvironment(name=env_name),
        deployment=schemas.PlanDeployment(deployment_id=dep_id),
        schedule=schemas.PlanScheduleNow(),
        experiments=[exp_id, exp2_id],
    )

    async with SessionLocal() as db:
        plan = await crud.create_plan(db, org_id, pl)
        assert plan.id is not None

    async with SessionLocal() as db:
        plans = await crud.get_plans_using_experiment(db, org_id, exp_id)

        assert len(plans) == 1
        assert str(plans[0]) == str(plan.id)

    async with SessionLocal() as db:
        await crud.set_status(db, plan.id, schemas.PlanStatus.deleted)

    async with SessionLocal() as db:
        plans = await crud.get_plans_using_experiment(db, org_id, exp_id)

        assert len(plans) == 0


@pytest.mark.anyio
async def test_is_experiment_used_by_any_plans(stack_ready, fake: Faker):
    org_id = str(uuid.uuid4())
    dep_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())
    exp2_id = str(uuid.uuid4())
    env_name = fake.name()

    pl = schemas.PlanCreate(
        environment=schemas.PlanGitHubEnvironment(name=env_name),
        deployment=schemas.PlanDeployment(deployment_id=dep_id),
        schedule=schemas.PlanScheduleNow(),
        experiments=[exp_id, exp2_id],
    )

    async with SessionLocal() as db:
        plan = await crud.create_plan(db, org_id, pl)
        assert plan.id is not None

    async with SessionLocal() as db:
        used = await crud.is_experiment_used_by_any_plans(db, org_id, exp_id)
        assert used is True

    async with SessionLocal() as db:
        await crud.set_status(db, plan.id, schemas.PlanStatus.deleted)

    async with SessionLocal() as db:
        used = await crud.is_experiment_used_by_any_plans(db, org_id, exp_id)
        assert used is False
