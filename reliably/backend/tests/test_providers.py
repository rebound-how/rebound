import uuid
from unittest.mock import patch

import pytest
from starlette.requests import Request

from reliably_app import deployment, plan
from reliably_app.database import SessionLocal
from reliably_app.plan.providers import delete_plan, schedule_plan


@pytest.mark.anyio
async def test_schedule_plan_missing_deployment(stack_ready, application):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    dep_id = str(uuid.uuid4())

    base = plan.schemas.PlanBase(
        environment=plan.schemas.PlanGitHubEnvironment(name="test"),
        deployment=plan.schemas.PlanDeployment(deployment_id=dep_id),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, base)
        assert p.id is not None

    r = Request(
        scope={
            "type": "http",
            "headers": [],
            "router": application.router,
        }
    )

    with pytest.raises(deployment.errors.DeploymentNotFoundError):
        await schedule_plan(plan.schemas.Plan.model_validate(p, from_attributes=True), org_id, user_id, r)

    async with SessionLocal() as db:
        p = await plan.crud.get_plan(db, p.id)
        assert p.status == plan.schemas.PlanStatus.creation_error


@pytest.mark.anyio
async def test_schedule_plan_via_agent_is_noop(stack_ready, application):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

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
        schedule=plan.schemas.PlanScheduleNow(via_agent=True),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, base)
        assert p.id is not None

    r = Request(
        scope={
            "type": "http",
            "headers": [],
            "router": application.router,
        }
    )

    await schedule_plan(plan.schemas.Plan.model_validate(p, from_attributes=True), org_id, user_id, r)

    async with SessionLocal() as db:
        p = await plan.crud.get_plan(db, p.id)
        assert p.status == plan.schemas.PlanStatus.creating


@pytest.mark.anyio
async def test_schedule_github_plan(stack_ready, application):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    dc = deployment.schemas.DeploymentCreate(
        name="test",
        definition=deployment.schemas.DeploymentGitHubDefinition(
            repo="https://github.com/my/repo", token="abc"
        ),
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

    r = Request(
        scope={
            "type": "http",
            "headers": [],
            "router": application.router,
        }
    )

    with patch("reliably_app.plan.providers.github", autospec=True):
        await schedule_plan(plan.schemas.Plan.model_validate(p, from_attributes=True), org_id, user_id, r)

    async with SessionLocal() as db:
        p = await plan.crud.get_plan(db, p.id)
        assert p.status == plan.schemas.PlanStatus.created


@pytest.mark.anyio
async def test_schedule_github_plan_fails(stack_ready, application):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    dc = deployment.schemas.DeploymentCreate(
        name="test",
        definition=deployment.schemas.DeploymentGitHubDefinition(
            repo="https://github.com/my/repo", token="abc"
        ),
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

    r = Request(
        scope={
            "type": "http",
            "headers": [],
            "router": application.router,
        }
    )

    with patch("reliably_app.plan.providers.github", autospec=True) as m:
        m.execute_plan.side_effect = plan.errors.PlanFailedError(
            str(p.id), "kaboom"
        )
        with pytest.raises(plan.errors.PlanFailedError):
            await schedule_plan(
                plan.schemas.Plan.model_validate(p, from_attributes=True), org_id, user_id, r
            )

    async with SessionLocal() as db:
        p = await plan.crud.get_plan(db, p.id)
        assert p.status == plan.schemas.PlanStatus.creation_error
        assert p.error == "kaboom"


@pytest.mark.anyio
async def test_schedule_reliably_plan(stack_ready, application):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    dc = deployment.schemas.DeploymentCreate(
        name="test",
        definition=deployment.schemas.DeploymentReliablyCloudDefinition(),
    )

    async with SessionLocal() as db:
        dep = await deployment.crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    base = plan.schemas.PlanBase(
        deployment=plan.schemas.PlanDeployment(deployment_id=dep.id),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, base)
        assert p.id is not None

    r = Request(
        scope={
            "type": "http",
            "headers": [],
            "router": application.router,
        }
    )

    with patch("reliably_app.plan.providers.rbly", autospec=True):
        await schedule_plan(plan.schemas.Plan.model_validate(p, from_attributes=True), org_id, user_id, r)

    async with SessionLocal() as db:
        p = await plan.crud.get_plan(db, p.id)
        assert p.status == plan.schemas.PlanStatus.created


@pytest.mark.anyio
async def test_schedule_reliably_plan_fails(stack_ready, application):
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    dc = deployment.schemas.DeploymentCreate(
        name="test",
        definition=deployment.schemas.DeploymentReliablyCloudDefinition(),
    )

    async with SessionLocal() as db:
        dep = await deployment.crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    base = plan.schemas.PlanBase(
        deployment=plan.schemas.PlanDeployment(deployment_id=dep.id),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, base)
        assert p.id is not None

    r = Request(
        scope={
            "type": "http",
            "headers": [],
            "router": application.router,
        }
    )

    with patch("reliably_app.plan.providers.rbly", autospec=True) as m:
        m.execute_plan.side_effect = plan.errors.PlanFailedError(
            str(p.id), "kaboom"
        )
        with pytest.raises(plan.errors.PlanFailedError):
            await schedule_plan(
                plan.schemas.Plan.model_validate(p, from_attributes=True), org_id, user_id, r
            )

    async with SessionLocal() as db:
        p = await plan.crud.get_plan(db, p.id)
        assert p.status == plan.schemas.PlanStatus.creation_error
        assert p.error == "kaboom"


@pytest.mark.anyio
async def test_delete_plan_missing_deployment_is_noop(stack_ready, application):
    org_id = str(uuid.uuid4())
    dep_id = str(uuid.uuid4())

    base = plan.schemas.PlanBase(
        environment=plan.schemas.PlanGitHubEnvironment(name="test"),
        deployment=plan.schemas.PlanDeployment(deployment_id=dep_id),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, base)
        assert p.id is not None

    await delete_plan(plan.schemas.Plan.model_validate(p, from_attributes=True), org_id)

    async with SessionLocal() as db:
        p = await plan.crud.get_plan(db, p.id, status=None)
        assert p.status == plan.schemas.PlanStatus.deleted


@pytest.mark.anyio
async def test_delete_plan_via_agent_is_noop(stack_ready, application):
    org_id = str(uuid.uuid4())

    dc = deployment.schemas.DeploymentCreate(
        name="test",
        definition=deployment.schemas.DeploymentReliablyCloudDefinition(),
    )

    async with SessionLocal() as db:
        dep = await deployment.crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    base = plan.schemas.PlanBase(
        environment=plan.schemas.PlanGitHubEnvironment(name="test"),
        deployment=plan.schemas.PlanDeployment(deployment_id=dep.id),
        schedule=plan.schemas.PlanScheduleNow(via_agent=True),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, base)
        assert p.id is not None

    await delete_plan(plan.schemas.Plan.model_validate(p, from_attributes=True), org_id)

    async with SessionLocal() as db:
        p = await plan.crud.get_plan(db, p.id, status=None)
        assert p.status == plan.schemas.PlanStatus.deleted


@pytest.mark.anyio
async def test_delete_reliably_plan(stack_ready, application):
    org_id = str(uuid.uuid4())

    dc = deployment.schemas.DeploymentCreate(
        name="test",
        definition=deployment.schemas.DeploymentReliablyCloudDefinition(),
    )

    async with SessionLocal() as db:
        dep = await deployment.crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    base = plan.schemas.PlanBase(
        deployment=plan.schemas.PlanDeployment(deployment_id=dep.id),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, base)
        assert p.id is not None

    with patch("reliably_app.plan.providers.rbly", autospec=True):
        await delete_plan(plan.schemas.Plan.model_validate(p, from_attributes=True), org_id)

    async with SessionLocal() as db:
        p = await plan.crud.get_plan(db, p.id, status=None)
        assert p.status == plan.schemas.PlanStatus.deleted


@pytest.mark.anyio
async def test_delete_reliably_plan_fails(stack_ready, application):
    org_id = str(uuid.uuid4())

    dc = deployment.schemas.DeploymentCreate(
        name="test",
        definition=deployment.schemas.DeploymentReliablyCloudDefinition(),
    )

    async with SessionLocal() as db:
        dep = await deployment.crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    base = plan.schemas.PlanBase(
        deployment=plan.schemas.PlanDeployment(deployment_id=dep.id),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, base)
        assert p.id is not None

    with patch("reliably_app.plan.providers.rbly", autospec=True) as m:
        m.delete_plan.side_effect = plan.errors.PlanFailedError(
            str(p.id), "kaboom"
        )
        with pytest.raises(plan.errors.PlanFailedError):
            await delete_plan(plan.schemas.Plan.model_validate(p, from_attributes=True), org_id)

    async with SessionLocal() as db:
        p = await plan.crud.get_plan(db, p.id, status=None)
        assert p.status == plan.schemas.PlanStatus.deleted
        assert p.error == "kaboom"


@pytest.mark.anyio
async def test_delete_reliably_plan_fails_on_exception(
    stack_ready, application
):
    org_id = str(uuid.uuid4())

    dc = deployment.schemas.DeploymentCreate(
        name="test",
        definition=deployment.schemas.DeploymentReliablyCloudDefinition(),
    )

    async with SessionLocal() as db:
        dep = await deployment.crud.create_deployment(db, org_id, dc)
        assert dep.id is not None

    base = plan.schemas.PlanBase(
        deployment=plan.schemas.PlanDeployment(deployment_id=dep.id),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, base)
        assert p.id is not None

    with patch("reliably_app.plan.providers.rbly", autospec=True) as m:
        m.delete_plan.side_effect = Exception("stuff")
        with pytest.raises(Exception):
            await delete_plan(plan.schemas.Plan.model_validate(p, from_attributes=True), org_id)

    async with SessionLocal() as db:
        p = await plan.crud.get_plan(db, p.id, status=None)
        assert p.status == plan.schemas.PlanStatus.deleted
        assert p.error.startswith(f"failed to delete plan '{p.id}'")


@pytest.mark.anyio
async def test_delete_github_plan(stack_ready, application):
    org_id = str(uuid.uuid4())

    dc = deployment.schemas.DeploymentCreate(
        name="test",
        definition=deployment.schemas.DeploymentGitHubDefinition(
            repo="https://github.com/my/repo", token="abc"
        ),
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

    with patch("reliably_app.plan.providers.github", autospec=True):
        await delete_plan(plan.schemas.Plan.model_validate(p, from_attributes=True), org_id)

    async with SessionLocal() as db:
        p = await plan.crud.get_plan(db, p.id, status=None)
        assert p.status == plan.schemas.PlanStatus.deleted


@pytest.mark.anyio
async def test_delete_github_plan_fails(stack_ready, application):
    org_id = str(uuid.uuid4())

    dc = deployment.schemas.DeploymentCreate(
        name="test",
        definition=deployment.schemas.DeploymentGitHubDefinition(
            repo="https://github.com/my/repo", token="abc"
        ),
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

    with patch("reliably_app.plan.providers.github", autospec=True) as m:
        m.delete_plan.side_effect = plan.errors.PlanFailedError(
            str(p.id), "kaboom"
        )
        with pytest.raises(plan.errors.PlanFailedError):
            await delete_plan(plan.schemas.Plan.model_validate(p, from_attributes=True), org_id)

    async with SessionLocal() as db:
        p = await plan.crud.get_plan(db, p.id, status=None)
        assert p.status == plan.schemas.PlanStatus.deleted
        assert p.error == "kaboom"


@pytest.mark.anyio
async def test_delete_github_plan_fails_on_exception(stack_ready, application):
    org_id = str(uuid.uuid4())

    dc = deployment.schemas.DeploymentCreate(
        name="test",
        definition=deployment.schemas.DeploymentGitHubDefinition(
            repo="https://github.com/my/repo", token="abc"
        ),
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

    with patch("reliably_app.plan.providers.github", autospec=True) as m:
        m.delete_plan.side_effect = Exception("stuff")
        with pytest.raises(Exception):
            await delete_plan(plan.schemas.Plan.model_validate(p, from_attributes=True), org_id)

    async with SessionLocal() as db:
        p = await plan.crud.get_plan(db, p.id, status=None)
        assert p.status == plan.schemas.PlanStatus.deleted
        assert p.error.startswith(f"failed to delete plan '{p.id}'")
