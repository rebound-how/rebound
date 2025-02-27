import uuid
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from starlette.requests import Request

from reliably_app import agent, deployment, plan
from reliably_app.database import SessionLocal
from reliably_app.plan import providers


@pytest.mark.anyio
@patch("reliably_app.plan.providers.github", autospec=True)
async def test_schedule_github_plan(github: Mock, stack_ready) -> None:
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    d = deployment.schemas.Deployment(
        id=uuid.uuid4(),
        created_date=datetime.utcnow(),
        org_id=org_id,
        name="hello",
        definition=deployment.schemas.DeploymentGitHubDefinition.model_validate(
            dict(
                repo="https://github.com/my/repo", name="my env", token="secret"
            )
        ),
    )

    plan_id = uuid.uuid4()
    p = plan.schemas.Plan(
        id=plan_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="myref",
        status=plan.schemas.PlanStatus.creating,
        definition=plan.schemas.PlanBase(
            environment=plan.schemas.PlanGitHubEnvironment(name="myenv"),
            deployment=plan.schemas.PlanDeployment(deployment_id=uuid.uuid4()),
            schedule=plan.schemas.PlanScheduleNow(),
            experiments=[str(uuid.uuid4())],
        ),
    )

    ep = AsyncMock()
    github.execute_plan = ep

    with patch(
        "reliably_app.plan.providers.get_deployment_from_plan", new_callable=AsyncMock
    ) as f:
        f.return_value = d
        await providers.schedule_plan(
            p, org_id, user_id, Request(scope={"type": "http"})
        )
        ep.assert_awaited_once()


@pytest.mark.anyio
@patch("reliably_app.plan.providers.github", autospec=True)
async def test_schedule_github_plan_using_agent(
    github: Mock, stack_ready
) -> None:
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    token_id = str(uuid.uuid4())

    a = agent.schemas.AgentCreate(user_id=user_id, token_id=token_id, sub="xyz")
    async with SessionLocal() as db:
        ag = await agent.crud.create_agent(
            db, org_id=org_id, agent=a, from_user_id=user_id
        )
        agent_id = ag.id

    d = deployment.schemas.Deployment(
        id=uuid.uuid4(),
        created_date=datetime.utcnow(),
        org_id=org_id,
        name="hello",
        definition=deployment.schemas.DeploymentGitHubDefinition.model_validate(
            dict(
                repo="https://github.com/my/repo", name="my env", token="secret"
            )
        ),
    )

    pc = plan.schemas.PlanCreate(
        environment=plan.schemas.PlanGitHubEnvironment(name="myenv"),
        deployment=plan.schemas.PlanDeployment(deployment_id=uuid.uuid4()),
        schedule=plan.schemas.PlanScheduleNow(via_agent=True),
        experiments=[str(uuid.uuid4())],
    )

    async with SessionLocal() as db:
        p = await plan.crud.create_plan(db, org_id, pc)
        p = plan.schemas.Plan.model_validate(p, from_attributes=True)
        plan_id = str(p.id)

    ep = AsyncMock()
    github.execute_plan = ep

    with patch(
        "reliably_app.plan.providers.get_deployment_from_plan", new_callable=AsyncMock
    ) as f:
        f.return_value = d
        await providers.schedule_plan(
            p, org_id, user_id, Request(scope={"type": "http"})
        )
        ep.assert_not_awaited()

        async with SessionLocal() as db:
            p = await plan.crud.get_next_schedulable_plan(
                db, org_id, agent_id, "github"
            )
            assert p.id == plan_id


@pytest.mark.anyio
@patch("reliably_app.plan.providers.noop", autospec=True)
async def test_schedule_noop_plan(noop: Mock, stack_ready) -> None:
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    d = deployment.schemas.Deployment(
        id=uuid.uuid4(),
        created_date=datetime.utcnow(),
        org_id=org_id,
        name="hello",
        definition=deployment.schemas.DeploymentNoopDefinition(),
    )

    plan_id = uuid.uuid4()
    p = plan.schemas.Plan(
        id=plan_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="myref",
        status=plan.schemas.PlanStatus.creating,
        definition=plan.schemas.PlanBase(
            environment=plan.schemas.PlanGitHubEnvironment(name="myenv"),
            deployment=plan.schemas.PlanDeployment(deployment_id=uuid.uuid4()),
            schedule=plan.schemas.PlanScheduleNow(),
            experiments=[str(uuid.uuid4())],
        ),
    )

    ep = AsyncMock()
    noop.execute_plan = ep

    with patch(
        "reliably_app.plan.providers.get_deployment_from_plan", new_callable=AsyncMock
    ) as f:
        f.return_value = d
        await providers.schedule_plan(
            p, org_id, user_id, Request(scope={"type": "http"})
        )
        ep.assert_awaited_once()
