import json
import secrets
import uuid
from base64 import b64decode, b64encode
from datetime import datetime
from unittest.mock import patch

import pytest
import respx
from fastapi import FastAPI
from httpx import Response
from ruamel.yaml import YAML

from reliably_app import deployment, plan
from reliably_app.config import Settings, get_settings
from reliably_app.database import SessionLocal
from reliably_app.plan.providers import github

BASE_URL = "https://api.github.com"


@pytest.mark.anyio
async def test_prepare_context(stack_ready, settings: Settings):
    org_id = uuid.uuid4()

    d = deployment.schemas.DeploymentCreate(
        name="hello",
        definition=deployment.schemas.DeploymentGitHubDefinition.model_validate(
            dict(
                repo="https://github.com/my/repo",
                token="secret",
                username="jane",
            )
        ),
    )

    with patch("reliably_app.deployment.schemas.get_settings") as s:
        s.return_value = settings
        async with SessionLocal() as db:
            dep = await deployment.crud.create_deployment(db, str(org_id), d)
            d = deployment.schemas.Deployment.model_validate(dep, from_attributes=True)

    exp_id = uuid.uuid4()
    plan_id = uuid.uuid4()
    p = plan.schemas.Plan(
        id=plan_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="myref",
        status=plan.schemas.PlanStatus.creating,
        definition=plan.schemas.PlanBase(
            environment=plan.schemas.PlanGitHubEnvironment(name="myenv"),
            deployment=plan.schemas.PlanDeployment(deployment_id=str(d.id)),
            schedule=plan.schemas.PlanScheduleNow(),
            experiments=[str(exp_id)],
        ),
    )

    with patch("reliably_app.plan.providers.github.get_settings", autospec=True) as m:
        m.return_value = settings
        with patch("reliably_app.deployment.schemas.get_settings") as s:
            s.return_value = settings
            context = github.prepare_context(p, d, org_id)

    assert context.token.get_secret_value() == "secret"
    assert str(context.api_host) == "https://api.github.com/"
    assert context.repo == "my/repo"
    assert context.ref == "main"
    assert context.actor == "jane"
    assert context.schedule is None
    assert context.email == "jane@users.noreply.github.com"
    assert context.env_name == "myenv"
    assert (
        str(context.dir_url)
        == f"https://github.com/my/repo/tree/main/plans/{str(plan_id)}"
    )  # noqa
    assert (
        str(context.content_base_url)
        == "https://api.github.com/repos/my/repo/contents"
    )
    assert context.plan_base_dir == f"plans/{str(plan_id)}"
    assert (
        str(context.experiment_url)
        == f"https://example.com/api/v1/organization/{org_id}/experiments/{exp_id}/raw"  # noqa: E501
    )


@pytest.mark.anyio
async def test_configure_workflow(stack_ready, settings: Settings):
    dep_id = uuid.uuid4()
    org_id = str(uuid.uuid4())

    d = deployment.schemas.DeploymentCreate(
        name="hello",
        definition=deployment.schemas.DeploymentGitHubDefinition.model_validate(
            dict(
                repo="https://github.com/my/repo",
                name="my env",
                token="secret",
                username="jane",
            )
        ),
    )

    with patch("reliably_app.deployment.schemas.get_settings") as s:
        s.return_value = settings
        async with SessionLocal() as db:
            dep = await deployment.crud.create_deployment(db, str(org_id), d)
            d = deployment.schemas.Deployment.model_validate(dep, from_attributes=True)

    exp_id = str(uuid.uuid4())
    plan_id = uuid.uuid4()
    p = plan.schemas.Plan(
        id=plan_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="myref",
        status=plan.schemas.PlanStatus.creating,
        definition=plan.schemas.PlanBase(
            environment=plan.schemas.PlanGitHubEnvironment(name="myenv"),
            deployment=plan.schemas.PlanDeployment(deployment_id=str(d.id)),
            schedule=plan.schemas.PlanScheduleNow(),
            experiments=[exp_id],
        ),
    )

    with respx.mock(base_url="https://api.github.com") as respx_mock:
        respx_mock.get(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan.yaml"
        ).mock(return_value=Response(200, json={
            "on": None,
            "jobs": {
                "execute-reliably-plan": {
                    "steps": [
                        {
                        },
                        {
                            "uses": "reliablyhq/actions/plan",
                        }
                    ]
                }
            }
        }))

        respx_mock.get(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan-{plan_id}.yaml"  # noqa: E501
        ).mock(return_value=Response(404, json={}))

        m = respx_mock.put(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan-{plan_id}.yaml"  # noqa: E501
        ).mock(return_value=Response(201, json={}))

        with patch("reliably_app.plan.providers.github.get_settings") as m:
            m.return_value = settings
            with patch("reliably_app.deployment.schemas.get_settings") as s:
                s.return_value = settings
                context = github.prepare_context(p, d, org_id)
                worflow_id = await github.configure_workflow(p, context)

        assert m.called
        assert worflow_id == f"reliably-plan-{plan_id}.yaml"

        req = respx_mock.calls.last.request
        c = json.loads(req.content.decode("utf-8"))
        assert c["message"] == f"Add workflow for Plan {plan_id}"
        assert c["committer"]["email"] == context.email
        assert c["committer"]["name"] == context.actor

        w = b64decode(c["content"].encode("utf-8")).decode("utf-8")
        yaml = YAML(typ="safe", pure=True)
        w = yaml.load(w)

        assert "schedule" not in w["on"]
        assert "workflow_dispatch" in w["on"]
        assert w["on"]["workflow_dispatch"] == {}

        assert (
            w["jobs"]["execute-reliably-plan"]["environment"]
            == context.env_name
        )  # noqa: E501

        j = w["jobs"]["execute-reliably-plan"]
        assert j["steps"][1]["with"]["working-dir"] == context.plan_base_dir
        assert j["steps"][1]["with"]["reliably-host"] == "example.com"
        assert j["steps"][1]["with"]["plan-id"] == str(plan_id)
        assert json.loads(
            j["steps"][1]["with"]["reliably-experiment-extra"]
        ) == [
            {
                "type": "url",
                "provider": "github",
                "topic": "commit",
                "value": f"https://github.com/my/repo/tree/main/plans/{str(plan_id)}",  # noqa: E501
            }
        ]
        assert (
            j["steps"][1]["with"]["reliably-service-token"]
            == r"${{ secrets.RELIABLY_SERVICE_TOKEN }}"
        )
        assert (
            j["steps"][1]["with"]["github-token"]
            == r"${{ secrets.GITHUB_TOKEN }}"
        )


@pytest.mark.anyio
async def test_configure_workflow_with_cron_schedule(stack_ready, settings: Settings):
    dep_id = uuid.uuid4()
    org_id = str(uuid.uuid4())

    d = deployment.schemas.DeploymentCreate(
        name="hello",
        definition=deployment.schemas.DeploymentGitHubDefinition.model_validate(
            dict(
                repo="https://github.com/my/repo",
                name="my env",
                token="secret",
                username="jane",
            )
        ),
    )

    with patch("reliably_app.deployment.schemas.get_settings") as s:
        s.return_value = settings
        async with SessionLocal() as db:
            dep = await deployment.crud.create_deployment(db, str(org_id), d)
            d = deployment.schemas.Deployment.model_validate(dep, from_attributes=True)

    exp_id = str(uuid.uuid4())
    plan_id = uuid.uuid4()
    p = plan.schemas.Plan(
        id=plan_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="myref",
        status=plan.schemas.PlanStatus.creating,
        definition=plan.schemas.PlanBase(
            environment=plan.schemas.PlanGitHubEnvironment(name="myenv"),
            deployment=plan.schemas.PlanDeployment(deployment_id=str(d.id)),
            schedule=plan.schemas.PlanScheduleCron(pattern="* * * * *"),
            experiments=[exp_id],
        ),
    )

    with respx.mock(base_url="https://api.github.com") as respx_mock:
        respx_mock.get(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan.yaml"
        ).mock(return_value=Response(200, json={
            "on": None,
            "jobs": {
                "execute-reliably-plan": {
                    "steps": [
                        {
                        },
                        {
                            "uses": "reliablyhq/actions/plan",
                        }
                    ]
                }
            }
        }))

        respx_mock.get(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan-{plan_id}.yaml"  # noqa: E501
        ).mock(return_value=Response(404, json={}))

        m = respx_mock.put(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan-{plan_id}.yaml"  # noqa: E501
        ).mock(return_value=Response(201, json={}))

        with patch("reliably_app.plan.providers.github.get_settings") as s:
            s.return_value = settings
            with patch("reliably_app.deployment.schemas.get_settings") as s:
                s.return_value = settings
                context = github.prepare_context(p, d, org_id)
                worflow_id = await github.configure_workflow(p, context)

        assert m.called
        assert worflow_id == f"reliably-plan-{plan_id}.yaml"

        req = respx_mock.calls.last.request
        c = json.loads(req.content.decode("utf-8"))
        assert c["message"] == f"Add workflow for Plan {plan_id}"
        assert c["committer"]["email"] == context.email
        assert c["committer"]["name"] == context.actor
        assert c["sha"] is None

        w = b64decode(c["content"].encode("utf-8")).decode("utf-8")
        yaml = YAML(typ="safe", pure=True)
        w = yaml.load(w)

        assert "workflow_dispatch" not in w["on"]
        assert "schedule" in w["on"]
        assert w["on"]["schedule"] == [{"cron": "* * * * *"}]

        assert (
            w["jobs"]["execute-reliably-plan"]["environment"]
            == context.env_name
        )  # noqa: E501

        j = w["jobs"]["execute-reliably-plan"]
        assert j["steps"][1]["with"]["working-dir"] == context.plan_base_dir
        assert j["steps"][1]["with"]["reliably-host"] == "example.com"
        assert j["steps"][1]["with"]["plan-id"] == str(plan_id)
        assert (
            j["steps"][1]["with"]["reliably-service-token"]
            == r"${{ secrets.RELIABLY_SERVICE_TOKEN }}"
        )
        assert (
            j["steps"][1]["with"]["github-token"]
            == r"${{ secrets.GITHUB_TOKEN }}"
        )


@pytest.mark.anyio
async def test_trigger_workflow(settings: Settings):
    dep_id = uuid.uuid4()
    org_id = str(uuid.uuid4())

    d = deployment.schemas.Deployment(
        id=dep_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        name="hello",
        definition=deployment.schemas.DeploymentGitHubDefinition.model_validate(
            dict(
                repo="https://github.com/my/repo",
                name="my env",
                token="secret",
                username="jane",
            )
        ),
    )

    with patch("reliably_app.deployment.schemas.get_settings") as s:
        s.return_value = settings
        async with SessionLocal() as db:
            dep = await deployment.crud.create_deployment(db, str(org_id), d)
            dep_id = str(dep.id)
            d = deployment.schemas.Deployment.model_validate(dep, from_attributes=True)

    exp_id = str(uuid.uuid4())
    plan_id = uuid.uuid4()
    p = plan.schemas.Plan(
        id=plan_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="myref",
        status=plan.schemas.PlanStatus.creating,
        definition=plan.schemas.PlanBase(
            environment=plan.schemas.PlanGitHubEnvironment(name="myenv"),
            deployment=plan.schemas.PlanDeployment(deployment_id=str(dep_id)),
            schedule=plan.schemas.PlanScheduleNow(),
            experiments=[exp_id],
        ),
    )

    with respx.mock(base_url="https://api.github.com") as respx_mock:
        m = respx_mock.post(
            f"/repos/my/repo/actions/workflows/reliably-plan-{plan_id}.yaml/dispatches"  # noqa: E501
        ).mock(return_value=Response(204))

        with patch("reliably_app.plan.providers.github.get_settings") as s:
            s.return_value = settings
            context = github.prepare_context(p, d, org_id)
            await github.trigger_workflow(
                p, context, f"reliably-plan-{plan_id}.yaml"
            )

            assert m.called


@pytest.mark.anyio
async def test_execute_plan(stack_ready, settings: Settings):
    dep_id = uuid.uuid4()
    org_id = uuid.uuid4()

    d = deployment.schemas.Deployment(
        id=dep_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        name="hello",
        definition=deployment.schemas.DeploymentGitHubDefinition.model_validate(
            dict(
                repo="https://github.com/my/repo",
                name="my env",
                token="secret",
                username="jane",
            )
        ),
    )

    with patch("reliably_app.deployment.schemas.get_settings") as s:
        s.return_value = settings
        async with SessionLocal() as db:
            dep = await deployment.crud.create_deployment(db, str(org_id), d)
            dep_id = str(dep.id)
            d = deployment.schemas.Deployment.model_validate(dep, from_attributes=True)

    exp_id = str(uuid.uuid4())
    p = plan.schemas.PlanCreate(
        environment=plan.schemas.PlanGitHubEnvironment(name="myenv"),
        deployment=plan.schemas.PlanDeployment(deployment_id=str(dep_id)),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[exp_id],
    )

    async with SessionLocal() as db:
        pl = await plan.crud.create_plan(db, str(org_id), p)
        plan_id = str(pl.id)
        p = plan.schemas.Plan.model_validate(pl, from_attributes=True)

    with respx.mock(base_url="https://api.github.com") as respx_mock:
        respx_mock.get(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan.yaml"
        ).mock(return_value=Response(200, json={
            "on": None,
            "jobs": {
                "plan": {
                    "steps": [
                        {
                            "uses": "reliablyhq/actions/plan",
                        }
                    ]
                }
            }
        }))

        respx_mock.get(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan-{plan_id}.yaml"  # noqa: E501
        ).mock(return_value=Response(404, json={}))

        respx_mock.put(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan-{plan_id}.yaml"  # noqa: E501
        ).mock(return_value=Response(201, json={}))

        respx_mock.post(
            f"/repos/my/repo/actions/workflows/reliably-plan-{plan_id}.yaml/dispatches"  # noqa: E501
        ).mock(return_value=Response(204))

        with patch("reliably_app.plan.providers.github.get_settings") as s:
            s.return_value = settings
            await github.execute_plan(p, d, org_id)


@pytest.mark.anyio
async def test_configure_workflow_from_existing_one(stack_ready, settings: Settings):
    dep_id = uuid.uuid4()
    org_id = str(uuid.uuid4())

    d = deployment.schemas.DeploymentCreate(
        name="hello",
        definition=deployment.schemas.DeploymentGitHubDefinition.model_validate(
            dict(
                repo="https://github.com/my/repo",
                name="my env",
                token="secret",
                username="jane",
            )
        ),
    )

    with patch("reliably_app.deployment.schemas.get_settings") as s:
        s.return_value = settings
        async with SessionLocal() as db:
            dep = await deployment.crud.create_deployment(db, str(org_id), d)
            d = deployment.schemas.Deployment.model_validate(dep, from_attributes=True)

    exp_id = str(uuid.uuid4())
    plan_id = uuid.uuid4()
    p = plan.schemas.Plan(
        id=plan_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="myref",
        status=plan.schemas.PlanStatus.creating,
        definition=plan.schemas.PlanBase(
            environment=plan.schemas.PlanGitHubEnvironment(name="myenv"),
            deployment=plan.schemas.PlanDeployment(deployment_id=str(d.id)),
            schedule=plan.schemas.PlanScheduleNow(),
            experiments=[exp_id],
        ),
    )

    with respx.mock(base_url="https://api.github.com") as respx_mock:
        w_sha = secrets.token_hex(8)

        respx_mock.get(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan-{plan_id}.yaml"  # noqa: E501
        ).mock(return_value=Response(200, json={
            "encoding": "base64",
            "sha": w_sha,
            "content": b64encode(github.DEFAULT_WORKFLOW).decode("utf-8")
        }))

        m = respx_mock.put(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan-{plan_id}.yaml"  # noqa: E501
        ).mock(return_value=Response(201, json={}))

        with patch("reliably_app.plan.providers.github.get_settings") as m:
            m.return_value = settings
            with patch("reliably_app.deployment.schemas.get_settings") as s:
                s.return_value = settings
                context = github.prepare_context(p, d, org_id)
                worflow_id = await github.configure_workflow(p, context)

        assert m.called
        assert worflow_id == f"reliably-plan-{plan_id}.yaml"

        req = respx_mock.calls.last.request
        c = json.loads(req.content.decode("utf-8"))
        assert c["message"] == f"Add workflow for Plan {plan_id}"
        assert c["committer"]["email"] == context.email
        assert c["committer"]["name"] == context.actor
        assert c["sha"] == w_sha

        w = b64decode(c["content"].encode("utf-8")).decode("utf-8")
        yaml = YAML(typ="safe", pure=True)
        w = yaml.load(w)

        assert "schedule" not in w["on"]
        assert "workflow_dispatch" in w["on"]
        assert w["on"]["workflow_dispatch"] == {}

        assert (
            w["jobs"]["execute-reliably-plan"]["environment"]
            == context.env_name
        )  # noqa: E501

        j = w["jobs"]["execute-reliably-plan"]
        assert j["steps"][1]["with"]["working-dir"] == context.plan_base_dir
        assert j["steps"][1]["with"]["reliably-host"] == "example.com"
        assert j["steps"][1]["with"]["plan-id"] == str(plan_id)
        assert json.loads(
            j["steps"][1]["with"]["reliably-experiment-extra"]
        ) == [
            {
                "type": "url",
                "provider": "github",
                "topic": "commit",
                "value": f"https://github.com/my/repo/tree/main/plans/{str(plan_id)}",  # noqa: E501
            }
        ]
        assert (
            j["steps"][1]["with"]["reliably-service-token"]
            == r"${{ secrets.RELIABLY_SERVICE_TOKEN }}"
        )
        assert (
            j["steps"][1]["with"]["github-token"]
            == r"${{ secrets.GITHUB_TOKEN }}"
        )


@pytest.mark.anyio
async def test_suspend_plan(stack_ready, settings: Settings):
    dep_id = uuid.uuid4()
    org_id = uuid.uuid4()

    d = deployment.schemas.Deployment(
        id=dep_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        name="hello",
        definition=deployment.schemas.DeploymentGitHubDefinition.model_validate(
            dict(
                repo="https://github.com/my/repo",
                name="my env",
                token="secret",
                username="jane",
            )
        ),
    )

    with patch("reliably_app.deployment.schemas.get_settings") as s:
        s.return_value = settings
        async with SessionLocal() as db:
            dep = await deployment.crud.create_deployment(db, str(org_id), d)
            dep_id = str(dep.id)
            d = deployment.schemas.Deployment.model_validate(dep, from_attributes=True)

    exp_id = str(uuid.uuid4())
    p = plan.schemas.PlanCreate(
        environment=plan.schemas.PlanGitHubEnvironment(name="myenv"),
        deployment=plan.schemas.PlanDeployment(deployment_id=str(dep_id)),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[exp_id],
    )

    async with SessionLocal() as db:
        pl = await plan.crud.create_plan(db, str(org_id), p)
        plan_id = str(pl.id)
        p = plan.schemas.Plan.model_validate(pl, from_attributes=True)

    with respx.mock(base_url="https://api.github.com") as respx_mock:
        respx_mock.get(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan.yaml"
        ).mock(return_value=Response(200, json={
            "on": None,
            "jobs": {
                "plan": {
                    "steps": [
                        {
                            "uses": "reliablyhq/actions/plan",
                        }
                    ]
                }
            }
        }))

        respx_mock.get(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan-{plan_id}.yaml"  # noqa: E501
        ).mock(return_value=Response(404, json={}))

        respx_mock.put(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan-{plan_id}.yaml"  # noqa: E501
        ).mock(return_value=Response(201, json={}))

        respx_mock.post(
            f"/repos/my/repo/actions/workflows/reliably-plan-{plan_id}.yaml/dispatches"  # noqa: E501
        ).mock(return_value=Response(204))

        respx_mock.put(
            f"/repos/my/repo/actions/workflows/reliably-plan-{plan_id}.yaml/disable"  # noqa: E501
        ).mock(return_value=Response(204))

        with patch("reliably_app.plan.providers.github.get_settings") as s:
            s.return_value = settings
            await github.execute_plan(p, d, org_id)
            await github.suspend_plan(p, d)


@pytest.mark.anyio
async def test_resume_plan(stack_ready, settings: Settings):
    dep_id = uuid.uuid4()
    org_id = uuid.uuid4()

    d = deployment.schemas.Deployment(
        id=dep_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        name="hello",
        definition=deployment.schemas.DeploymentGitHubDefinition.model_validate(
            dict(
                repo="https://github.com/my/repo",
                name="my env",
                token="secret",
                username="jane",
            )
        ),
    )

    with patch("reliably_app.deployment.schemas.get_settings") as s:
        s.return_value = settings
        async with SessionLocal() as db:
            dep = await deployment.crud.create_deployment(db, str(org_id), d)
            dep_id = str(dep.id)
            d = deployment.schemas.Deployment.model_validate(dep, from_attributes=True)

    exp_id = str(uuid.uuid4())
    p = plan.schemas.PlanCreate(
        environment=plan.schemas.PlanGitHubEnvironment(name="myenv"),
        deployment=plan.schemas.PlanDeployment(deployment_id=str(dep_id)),
        schedule=plan.schemas.PlanScheduleNow(),
        experiments=[exp_id],
    )

    async with SessionLocal() as db:
        pl = await plan.crud.create_plan(db, str(org_id), p)
        plan_id = str(pl.id)
        p = plan.schemas.Plan.model_validate(pl, from_attributes=True)

    with respx.mock(base_url="https://api.github.com") as respx_mock:
        respx_mock.get(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan.yaml"
        ).mock(return_value=Response(200, json={
            "on": None,
            "jobs": {
                "plan": {
                    "steps": [
                        {
                            "uses": "reliablyhq/actions/plan",
                        }
                    ]
                }
            }
        }))

        respx_mock.get(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan-{plan_id}.yaml"  # noqa: E501
        ).mock(return_value=Response(404, json={}))

        respx_mock.put(
            f"/repos/my/repo/contents/.github/workflows/reliably-plan-{plan_id}.yaml"  # noqa: E501
        ).mock(return_value=Response(201, json={}))

        respx_mock.post(
            f"/repos/my/repo/actions/workflows/reliably-plan-{plan_id}.yaml/dispatches"  # noqa: E501
        ).mock(return_value=Response(204))

        respx_mock.put(
            f"/repos/my/repo/actions/workflows/reliably-plan-{plan_id}.yaml/enable"  # noqa: E501
        ).mock(return_value=Response(204))

        respx_mock.put(
            f"/repos/my/repo/actions/workflows/reliably-plan-{plan_id}.yaml/disable"  # noqa: E501
        ).mock(return_value=Response(204))

        with patch("reliably_app.plan.providers.github.get_settings") as s:
            s.return_value = settings
            await github.execute_plan(p, d, org_id)
            await github.suspend_plan(p, d)
            await github.resume_plan(p, d)
