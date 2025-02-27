import uuid
from datetime import datetime

import pytest
import ujson
from starlette.requests import Request

from reliably_app import deployment, environment, experiment, plan
from reliably_app.database import SessionLocal
from reliably_app.plan.providers import utils


@pytest.mark.anyio
async def test_get_deployment_from_plan(stack_ready):
    org_id = str(uuid.uuid4())

    dc = deployment.schemas.DeploymentCreate(
        name="test",
        definition=deployment.schemas.DeploymentNoopDefinition(),
    )

    async with SessionLocal() as db:
        dep = await deployment.crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    base = plan.schemas.PlanBase(
        environment=plan.schemas.PlanGitHubEnvironment(name="test"),
        deployment=plan.schemas.PlanDeployment(deployment_id=dep.id),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, base)
        assert p.id is not None

    d = await utils.get_deployment_from_plan(plan.schemas.Plan.model_validate(p, from_attributes=True))
    assert str(d.id) == str(dep.id)


@pytest.mark.anyio
async def test_get_deployment_not_found_from_plan(stack_ready):
    org_id = str(uuid.uuid4())

    base = plan.schemas.PlanBase(
        environment=plan.schemas.PlanGitHubEnvironment(name="test"),
        deployment=plan.schemas.PlanDeployment(deployment_id=str(uuid.uuid4())),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, base)
        assert p.id is not None

    with pytest.raises(deployment.errors.DeploymentNotFoundError):
        await utils.get_deployment_from_plan(plan.schemas.Plan.model_validate(p, from_attributes=True))


def test_get_experiment_direct_url(application):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())

    base = plan.schemas.PlanBase(
        environment=plan.schemas.PlanGitHubEnvironment(name="test"),
        deployment=plan.schemas.PlanDeployment(deployment_id=str(uuid.uuid4())),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[exp_id],
    )

    p = plan.schemas.Plan(
        id=uuid.uuid4(),
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="abc",
        status=plan.schemas.PlanStatus.completed,
        definition=base,
    )

    r = Request(
        scope={
            "type": "http",
            "headers": [],
            "router": application.router,
        }
    )

    url = utils.get_experiment_direct_url(p, org_id, r)
    assert (
        url == f"http:///api/v1/organization/{org_id}/experiments/{exp_id}/raw"
    )


@pytest.mark.anyio
async def test_get_experiment(stack_ready):
    org_id = str(uuid.uuid4())

    dc = experiment.schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        exp = await experiment.crud.create_experiment(db, org_id, dc)
        assert exp.id is not None

    base = plan.schemas.PlanBase(
        environment=plan.schemas.PlanGitHubEnvironment(name="test"),
        deployment=plan.schemas.PlanDeployment(deployment_id=str(uuid.uuid4())),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[exp.id],
    )

    p = plan.schemas.Plan(
        id=uuid.uuid4(),
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="abc",
        status=plan.schemas.PlanStatus.completed,
        definition=base,
    )

    x = await utils.get_experiment(p)

    assert x["title"] == "hello world"
    assert x["controls"][0]["name"] == "reliably"
    provider = x["controls"][0]["provider"]
    assert provider["module"] == "chaosreliably.controls.experiment"
    assert provider["type"] == "python"
    assert provider["arguments"] == {"exp_id": str(exp.id), "org_id": org_id}


@pytest.mark.anyio
async def test_get_experiment_fails(stack_ready):
    org_id = str(uuid.uuid4())
    exp_id = str(uuid.uuid4())

    dc = experiment.schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        exp = await experiment.crud.create_experiment(db, org_id, dc)
        assert exp.id is not None

    base = plan.schemas.PlanBase(
        environment=plan.schemas.PlanGitHubEnvironment(name="test"),
        deployment=plan.schemas.PlanDeployment(deployment_id=str(uuid.uuid4())),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[exp_id],
    )

    p = plan.schemas.Plan(
        id=uuid.uuid4(),
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="abc",
        status=plan.schemas.PlanStatus.completed,
        definition=base,
    )

    with pytest.raises(plan.errors.PlanFailedError):
        await utils.get_experiment(p)


@pytest.mark.anyio
async def test_get_environment_from_plan(stack_ready):
    org_id = str(uuid.uuid4())

    e = environment.schemas.EnvironmentCreate(
        name="test",
        envvars=[],
        secrets=[],
    )

    async with SessionLocal() as db:
        env = await environment.crud.create_environment(db, org_id, e)
        assert env.id is not None

    dc = deployment.schemas.DeploymentCreate(
        name="test",
        definition=deployment.schemas.DeploymentNoopDefinition(),
    )

    async with SessionLocal() as db:
        dep = await deployment.crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    base = plan.schemas.PlanBase(
        environment=plan.schemas.PlanReliablyEnvironment(id=env.id),
        deployment=plan.schemas.PlanDeployment(deployment_id=dep.id),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, base)
        assert p.id is not None

    d = await utils.get_environment_from_plan(plan.schemas.Plan.model_validate(p, from_attributes=True))
    assert str(d.id) == str(env.id)


@pytest.mark.anyio
async def test_get_environment_from_plan_may_not_be_set(stack_ready):
    org_id = str(uuid.uuid4())

    dc = deployment.schemas.DeploymentCreate(
        name="test",
        definition=deployment.schemas.DeploymentNoopDefinition(),
    )

    async with SessionLocal() as db:
        dep = await deployment.crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    base = plan.schemas.PlanBase(
        environment=plan.schemas.PlanReliablyEnvironment(id=None),
        deployment=plan.schemas.PlanDeployment(deployment_id=dep.id),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, base)
        assert p.id is not None

    d = await utils.get_environment_from_plan(plan.schemas.Plan.model_validate(p, from_attributes=True))
    assert d is None


@pytest.mark.anyio
async def test_get_environment_from_plan_fails_when_not_found(stack_ready):
    org_id = str(uuid.uuid4())

    dc = deployment.schemas.DeploymentCreate(
        name="test",
        definition=deployment.schemas.DeploymentNoopDefinition(),
    )

    async with SessionLocal() as db:
        dep = await deployment.crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    base = plan.schemas.PlanBase(
        environment=plan.schemas.PlanReliablyEnvironment(id=uuid.uuid4()),
        deployment=plan.schemas.PlanDeployment(deployment_id=dep.id),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, base)
        assert p.id is not None

    with pytest.raises(environment.errors.EnvironmentNotFoundError):
        await utils.get_environment_from_plan(plan.schemas.Plan.model_validate(p, from_attributes=True))
