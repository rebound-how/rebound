import uuid
from contextlib import contextmanager
import json
import pytest
import respx
import ujson
from datetime import datetime
from httpx import Response
from starlette.requests import Request

from reliably_app import agent, deployment, environment, experiment, integration, organization, plan
from reliably_app.database import SessionLocal
from reliably_app.plan.errors import PlanFailedError
from reliably_app.plan.providers import rbly
from reliably_app.task import get_org_id_hash_prefix


@contextmanager
def mock_gcp_calls(with_delete: bool = False, plan_id: str = None) -> None:
    with respx.mock() as respx_mock:

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"  # noqa
        ).mock(return_value=Response(200, json={"access_token": "abc"}))

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id"  # noqa
        ).mock(return_value=Response(200, text="my-project"))

        if with_delete:
            respx_mock.delete(
                f"https://europe-west-1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/my-project/jobs/plan-{plan_id}"  # noqa
            ).mock(return_value=Response(200, json={}))


        yield respx_mock


@pytest.mark.anyio
async def test_reliably_execute_plan(stack_ready, application):
    d = deployment.schemas.DeploymentCreate(
        name="hello",
        definition=deployment.schemas.DeploymentReliablyCloudDefinition.model_validate(  # noqa
            dict(
                location="europe-west-1",
            )
        ),
    )

    async with SessionLocal() as db:
        oc = organization.schemas.OrganizationCreate(name="hello")
        org = await organization.crud.create_org(db, oc)
        assert org.id is not None
    org_id = str(org.id)
    prefix = get_org_id_hash_prefix(org_id)

    dc = experiment.schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        exp = await experiment.crud.create_experiment(db, org.id, dc)
        assert exp.id is not None

    e = environment.schemas.EnvironmentCreate(
        name="my-env",
        envvars=environment.schemas.EnvironmentVars(
            root=[{"var_name": "MY_VAR", "value": "hi"}]
        ),
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )
    async with SessionLocal() as db:
        env = await environment.crud.create_environment(db, org.id, e)
        assert env.id is not None

    ei = environment.schemas.EnvironmentCreate(
        name="my-integration-env",
        envvars=[],
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_SEC_VAR", "value": "hey", "key": "boom"}]
        )
    )
    async with SessionLocal() as db:
        envint = await environment.crud.create_environment(db, org.id, ei)
        assert envint.id is not None

    i = integration.schemas.IntegrationCreate(
        name="slack",
        provider="slack",
        environment=ei
    )
    async with SessionLocal() as db:
        intg = await integration.crud.create_integration(db, org.id, i, envint.id)
        assert intg.id is not None

    plan_id = uuid.uuid4()
    p = plan.schemas.Plan(
        id=plan_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="myref",
        status=plan.schemas.PlanStatus.creating,
        definition=plan.schemas.PlanBase(
            environment=plan.schemas.PlanReliablyEnvironment(id=str(env.id)),
            deployment=plan.schemas.PlanDeployment(deployment_id=uuid.uuid4()),
            schedule=plan.schemas.PlanScheduleNow(),
            experiments=[str(exp.id)],
        ),
    )

    user_id = str(uuid.uuid4())
    async with SessionLocal() as db:
        agt = await agent.crud.create_user_agent(org, user_id, True)
        assert agt.id is not None

    secret_name = f"{prefix}_RAT_{str(plan_id)}"

    with respx.mock() as respx_mock:
        respx_mock.post(
            "https://europe-west-1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/my-project/jobs?alt=json"  # noqa
        ).mock(return_value=Response(200, json={}))

        respx_mock.get(
            f"https://europe-west-1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/my-project/jobs/plan-{plan_id}",  # noqa
        ).mock(
            side_effect=[
                Response(404),
                Response(
                    200,
                    json={
                        "status": {
                            "conditions": [{"type": "Ready", "status": "True"}]
                        }
                    },
                )
            ]
        )

        respx_mock.post(
            f"https://europe-west-1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/my-project/jobs/plan-{plan_id}:run"  # noqa
        ).mock(return_value=Response(200, json={}))

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"  # noqa
        ).mock(return_value=Response(200, json={"access_token": "abc"}))

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id"  # noqa
        ).mock(return_value=Response(200, text="my-project"))

        await rbly.execute_plan(
            p,
            d,
            environment.schemas.Environment.model_validate(env, from_attributes=True),
            [
                integration.schemas.IntegrationFull(
                    id=str(intg.id),
                    org_id=org_id,
                    name=i.name,
                    provider=i.provider,
                    environment=environment.schemas.Environment.model_validate(
                        envint,
                        from_attributes=True
                    )
                )
            ],
            org.id,
            user_id,
            None
        )


@pytest.mark.anyio
async def test_execute_plan_with_error(stack_ready, application):
    d = deployment.schemas.DeploymentCreate(
        name="hello",
        definition=deployment.schemas.DeploymentReliablyCloudDefinition.model_validate(  # noqa
            dict(
                location="europe-west-1",
            )
        ),
    )

    dc = experiment.schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        oc = organization.schemas.OrganizationCreate(name="hello")
        org = await organization.crud.create_org(db, oc)
        assert org.id is not None
    org_id = str(org.id)
    prefix = get_org_id_hash_prefix(org_id)

    async with SessionLocal() as db:
        exp = await experiment.crud.create_experiment(db, org.id, dc)
        assert exp.id is not None

    e = environment.schemas.EnvironmentCreate(
        name="my-env",
        envvars=environment.schemas.EnvironmentVars(
            root=[{"var_name": "MY_VAR", "value": "hi"}]
        ),
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )
    async with SessionLocal() as db:
        env = await environment.crud.create_environment(db, org.id, e)
        assert env.id is not None

    ei = environment.schemas.EnvironmentCreate(
        name="my-integration-env",
        envvars=[],
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_SEC_VAR", "value": "hey", "key": "boom"}]
        )
    )
    async with SessionLocal() as db:
        envint = await environment.crud.create_environment(db, org.id, ei)
        assert envint.id is not None

    i = integration.schemas.IntegrationCreate(
        name="slack",
        provider="slack",
        environment=ei
    )
    async with SessionLocal() as db:
        intg = await integration.crud.create_integration(db, org.id, i, envint.id)
        assert intg.id is not None

    plan_id = uuid.uuid4()
    p = plan.schemas.Plan(
        id=plan_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="myref",
        status=plan.schemas.PlanStatus.creating,
        definition=plan.schemas.PlanBase(
            environment=plan.schemas.PlanReliablyEnvironment(id=str(env.id)),
            deployment=plan.schemas.PlanDeployment(deployment_id=uuid.uuid4()),
            schedule=plan.schemas.PlanScheduleNow(),
            experiments=[str(exp.id)],
        ),
    )

    user_id = str(uuid.uuid4())
    async with SessionLocal() as db:
        agt = await agent.crud.create_user_agent(org, user_id, True)
        assert agt.id is not None

    secret_name = f"{prefix}_RAT_{str(plan_id)}"

    with respx.mock() as respx_mock:
        respx_mock.post(
            "https://europe-west-1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/my-project/jobs?alt=json"  # noqa
        ).mock(return_value=Response(400, json={}))

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"  # noqa
        ).mock(return_value=Response(200, json={"access_token": "abc"}))

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id"  # noqa
        ).mock(return_value=Response(200, text="my-project"))

        respx_mock.get(
            f"https://europe-west-1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/my-project/jobs/plan-{plan_id}",  # noqa
        ).mock(
            return_value=Response(404),
        )

        with pytest.raises(PlanFailedError):
            await rbly.execute_plan(
                p,
                d,
                environment.schemas.Environment.model_validate(env, from_attributes=True),
                [
                    integration.schemas.IntegrationFull(
                        id=str(intg.id),
                        org_id=org_id,
                        name=i.name,
                        provider=i.provider,
                        environment=environment.schemas.Environment.model_validate(
                            envint,
                            from_attributes=True
                        )
                    )
                ],
                org.id,
                user_id,
                None,
            )


@pytest.mark.anyio
async def test_reliably_delete_plan(stack_ready, application):
    d = deployment.schemas.DeploymentCreate(
        name="hello",
        definition=deployment.schemas.DeploymentReliablyCloudDefinition.model_validate(  # noqa
            dict(
                location="europe-west-1",
            )
        ),
    )

    async with SessionLocal() as db:
        oc = organization.schemas.OrganizationCreate(name="hello")
        org = await organization.crud.create_org(db, oc)
        assert org.id is not None
    org_id = str(org.id)

    dc = experiment.schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        exp = await experiment.crud.create_experiment(db, org.id, dc)
        assert exp.id is not None

    e = environment.schemas.EnvironmentCreate(
        name="my-env",
        envvars=environment.schemas.EnvironmentVars(
            root=[{"var_name": "MY_VAR", "value": "hi"}]
        ),
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )
    async with SessionLocal() as db:
        env = await environment.crud.create_environment(db, org.id, e)
        assert env.id is not None

    plan_id = uuid.uuid4()
    p = plan.schemas.Plan(
        id=plan_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="myref",
        status=plan.schemas.PlanStatus.creating,
        definition=plan.schemas.PlanBase(
            environment=plan.schemas.PlanReliablyEnvironment(id=str(env.id)),
            deployment=plan.schemas.PlanDeployment(deployment_id=uuid.uuid4()),
            schedule=plan.schemas.PlanScheduleNow(),
            experiments=[str(exp.id)],
        ),
    )

    user_id = str(uuid.uuid4())
    async with SessionLocal() as db:
        agt = await agent.crud.create_user_agent(org, user_id, True)
        assert agt.id is not None
    
    with mock_gcp_calls(with_delete=True, plan_id=str(plan_id)):
        await rbly.delete_plan(p, d, environment.schemas.Environment.model_validate(env, from_attributes=True))


@pytest.mark.anyio
async def test_reliably_rerun_plan(stack_ready, application):
    d = deployment.schemas.DeploymentCreate(
        name="hello",
        definition=deployment.schemas.DeploymentReliablyCloudDefinition.model_validate(  # noqa
            dict(
                location="europe-west-1",
            )
        ),
    )

    async with SessionLocal() as db:
        oc = organization.schemas.OrganizationCreate(name="hello")
        org = await organization.crud.create_org(db, oc)
        assert org.id is not None
    org_id = str(org.id)
    prefix = get_org_id_hash_prefix(org_id)

    dc = experiment.schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        exp = await experiment.crud.create_experiment(db, org.id, dc)
        assert exp.id is not None

    e = environment.schemas.EnvironmentCreate(
        name="my-env",
        envvars=environment.schemas.EnvironmentVars(
            root=[{"var_name": "MY_VAR", "value": "hi"}]
        ),
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )
    async with SessionLocal() as db:
        env = await environment.crud.create_environment(db, org.id, e)
        assert env.id is not None

    ei = environment.schemas.EnvironmentCreate(
        name="my-integration-env",
        envvars=[],
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_SEC_VAR", "value": "hey", "key": "boom"}]
        )
    )
    async with SessionLocal() as db:
        envint = await environment.crud.create_environment(db, org.id, ei)
        assert envint.id is not None

    i = integration.schemas.IntegrationCreate(
        name="slack",
        provider="slack",
        environment=ei
    )
    async with SessionLocal() as db:
        intg = await integration.crud.create_integration(db, org.id, i, envint.id)
        assert intg.id is not None

    plan_id = uuid.uuid4()
    p = plan.schemas.Plan(
        id=plan_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="myref",
        status=plan.schemas.PlanStatus.creating,
        definition=plan.schemas.PlanBase(
            environment=plan.schemas.PlanReliablyEnvironment(id=str(env.id)),
            deployment=plan.schemas.PlanDeployment(deployment_id=uuid.uuid4()),
            schedule=plan.schemas.PlanScheduleNow(),
            experiments=[str(exp.id)],
        ),
    )

    user_id = str(uuid.uuid4())
    async with SessionLocal() as db:
        agt = await agent.crud.create_user_agent(org, user_id, True)
        assert agt.id is not None

    secret_name = f"{prefix}_RAT_{str(plan_id)}"

    job = {
        "metadata": {},
        "status": {
            "conditions": [{"type": "Ready", "status": "True"}]
        },
        "spec": {
            "template": {
                "metadata": {},
                "spec": {
                    "template": {
                        "spec": {
                            "containers": [{}]
                        }
                    }
                }
            }
        }
    }

    with respx.mock() as respx_mock:
        update_route = respx_mock.put(
            f"https://europe-west-1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/my-project/jobs/plan-{plan_id}"  # noqa
        ).mock(return_value=Response(200, json={}))

        respx_mock.get(
            f"https://europe-west-1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/my-project/jobs/plan-{plan_id}",  # noqa
        ).mock(
            side_effect=[
                Response(
                    200,
                    json=job,
                ),
                Response(
                    200,
                    json=job,
                ),
            ]
        )

        respx_mock.post(
            f"https://europe-west-1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/my-project/jobs/plan-{plan_id}:run"  # noqa
        ).mock(return_value=Response(200, json={}))

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"  # noqa
        ).mock(return_value=Response(200, json={"access_token": "abc"}))

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id"  # noqa
        ).mock(return_value=Response(200, text="my-project"))

        d.definition.image = "ubuntu/rolling"

        await rbly.execute_plan(
            p,
            d,
            environment.schemas.Environment.model_validate(env, from_attributes=True),
            [
                integration.schemas.IntegrationFull(
                    id=str(intg.id),
                    org_id=org_id,
                    name=i.name,
                    provider=i.provider,
                    environment=environment.schemas.Environment.model_validate(
                        envint,
                        from_attributes=True
                    )
                )
            ],
            org.id,
            user_id,
            None
        )

        ct = update_route.calls.last.request.content.decode("utf-8")
        job = json.loads(ct)
        assert job["metadata"]["annotations"]["client.knative.dev/user-image"] == d.definition.image


@pytest.mark.anyio
async def test_reliably_suspend_plan(stack_ready, application):
    async with SessionLocal() as db:
        oc = organization.schemas.OrganizationCreate(name="hello")
        org = await organization.crud.create_org(db, oc)
        assert org.id is not None
    org_id = str(org.id)
    prefix = get_org_id_hash_prefix(org_id)

    d = deployment.schemas.DeploymentCreate(
        name="hello",
        definition=deployment.schemas.DeploymentReliablyCloudDefinition.model_validate(  # noqa
            dict(
                location="europe-west-1",
            )
        ),
    )

    dc = experiment.schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        exp = await experiment.crud.create_experiment(db, org.id, dc)
        assert exp.id is not None

    e = environment.schemas.EnvironmentCreate(
        name="my-env",
        envvars=environment.schemas.EnvironmentVars(
            root=[{"var_name": "MY_VAR", "value": "hi"}]
        ),
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )
    async with SessionLocal() as db:
        env = await environment.crud.create_environment(db, org.id, e)
        assert env.id is not None

    ei = environment.schemas.EnvironmentCreate(
        name="my-integration-env",
        envvars=[],
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_SEC_VAR", "value": "hey", "key": "boom"}]
        )
    )
    async with SessionLocal() as db:
        envint = await environment.crud.create_environment(db, org.id, ei)
        assert envint.id is not None

    i = integration.schemas.IntegrationCreate(
        name="slack",
        provider="slack",
        environment=ei
    )
    async with SessionLocal() as db:
        intg = await integration.crud.create_integration(db, org.id, i, envint.id)
        assert intg.id is not None

    plan_id = uuid.uuid4()
    p = plan.schemas.Plan(
        id=plan_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="myref",
        status=plan.schemas.PlanStatus.creating,
        definition=plan.schemas.PlanBase(
            environment=plan.schemas.PlanReliablyEnvironment(id=str(env.id)),
            deployment=plan.schemas.PlanDeployment(deployment_id=uuid.uuid4()),
            schedule=plan.schemas.PlanScheduleCron(pattern="* * * * *"),
            experiments=[str(exp.id)],
        ),
    )

    user_id = str(uuid.uuid4())
    async with SessionLocal() as db:
        agt = await agent.crud.create_user_agent(org, user_id, True)
        assert agt.id is not None

    secret_name = f"{prefix}_RAT_{str(plan_id)}"

    with respx.mock() as respx_mock:
        respx_mock.post(
            "https://europe-west-1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/my-project/jobs?alt=json"  # noqa
        ).mock(return_value=Response(200, json={}))

        respx_mock.get(
            f"https://europe-west-1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/my-project/jobs/plan-{plan_id}",  # noqa
        ).mock(
            side_effect=[
                Response(
                    200,
                    json={
                        "status": {
                            "conditions": [{"type": "Ready", "status": "True"}]
                        }
                    },
                )
            ]
        )

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"  # noqa
        ).mock(return_value=Response(200, json={"access_token": "abc"}))

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id"  # noqa
        ).mock(return_value=Response(200, text="my-project"))

        respx_mock.post(
            f"https://cloudscheduler.googleapis.com/v1/projects/my-project/locations/europe-west-1/jobs"  # noqa
        ).mock(return_value=Response(200, json={}))

        await rbly.execute_plan(
            p,
            d,
            environment.schemas.Environment.model_validate(env, from_attributes=True),
            [
                integration.schemas.IntegrationFull(
                    id=str(intg.id),
                    org_id=org_id,
                    name=i.name,
                    provider=i.provider,
                    environment=environment.schemas.Environment.model_validate(
                        envint,
                        from_attributes=True
                    )
                )
            ],
            org.id,
            user_id,
            None
        )

        respx_mock.post(
            f"https://cloudscheduler.googleapis.com/v1/projects/my-project/locations/europe-west-1/jobs/plan-{plan_id}:pause"  # noqa
        ).mock(return_value=Response(200, json={}))

        await rbly.suspend_plan(
            p,
            d,
        )


@pytest.mark.anyio
async def test_reliably_resume_plan(stack_ready, application):
    async with SessionLocal() as db:
        oc = organization.schemas.OrganizationCreate(name="hello")
        org = await organization.crud.create_org(db, oc)
        assert org.id is not None
    org_id = str(org.id)
    prefix = get_org_id_hash_prefix(org_id)

    d = deployment.schemas.DeploymentCreate(
        name="hello",
        definition=deployment.schemas.DeploymentReliablyCloudDefinition.model_validate(  # noqa
            dict(
                location="europe-west-1",
            )
        ),
    )

    dc = experiment.schemas.ExperimentCreate(
        definition=ujson.dumps({"title": "hello world"})
    )

    async with SessionLocal() as db:
        exp = await experiment.crud.create_experiment(db, org.id, dc)
        assert exp.id is not None

    e = environment.schemas.EnvironmentCreate(
        name="my-env",
        envvars=environment.schemas.EnvironmentVars(
            root=[{"var_name": "MY_VAR", "value": "hi"}]
        ),
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_VAR", "value": "hi", "key": "blah"}]
        )
    )
    async with SessionLocal() as db:
        env = await environment.crud.create_environment(db, org.id, e)
        assert env.id is not None

    ei = environment.schemas.EnvironmentCreate(
        name="my-integration-env",
        envvars=[],
        secrets=environment.schemas.EnvironmentSecrets(
            root=[{"var_name": "MY_SEC_VAR", "value": "hey", "key": "boom"}]
        )
    )
    async with SessionLocal() as db:
        envint = await environment.crud.create_environment(db, org.id, ei)
        assert envint.id is not None

    i = integration.schemas.IntegrationCreate(
        name="slack",
        provider="slack",
        environment=ei
    )
    async with SessionLocal() as db:
        intg = await integration.crud.create_integration(db, org.id, i, envint.id)
        assert intg.id is not None

    plan_id = uuid.uuid4()
    p = plan.schemas.Plan(
        id=plan_id,
        org_id=org_id,
        created_date=datetime.utcnow(),
        ref="myref",
        status=plan.schemas.PlanStatus.creating,
        definition=plan.schemas.PlanBase(
            environment=plan.schemas.PlanReliablyEnvironment(id=str(env.id)),
            deployment=plan.schemas.PlanDeployment(deployment_id=uuid.uuid4()),
            schedule=plan.schemas.PlanScheduleCron(pattern="* * * * *"),
            experiments=[str(exp.id)],
        ),
    )

    user_id = str(uuid.uuid4())
    async with SessionLocal() as db:
        agt = await agent.crud.create_user_agent(org, user_id, True)
        assert agt.id is not None

    secret_name = f"{prefix}_RAT_{str(plan_id)}"

    with respx.mock() as respx_mock:
        respx_mock.post(
            "https://europe-west-1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/my-project/jobs?alt=json"  # noqa
        ).mock(return_value=Response(200, json={}))

        respx_mock.get(
            f"https://europe-west-1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/my-project/jobs/plan-{plan_id}",  # noqa
        ).mock(
            side_effect=[
                Response(
                    200,
                    json={
                        "status": {
                            "conditions": [{"type": "Ready", "status": "True"}]
                        }
                    },
                )
            ]
        )

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"  # noqa
        ).mock(return_value=Response(200, json={"access_token": "abc"}))

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id"  # noqa
        ).mock(return_value=Response(200, text="my-project"))

        respx_mock.post(
            f"https://cloudscheduler.googleapis.com/v1/projects/my-project/locations/europe-west-1/jobs"  # noqa
        ).mock(return_value=Response(200, json={}))

        respx_mock.post(
            f"https://cloudscheduler.googleapis.com/v1/projects/my-project/locations/europe-west-1/jobs/plan-{plan_id}:pause"  # noqa
        ).mock(return_value=Response(200, json={}))

        respx_mock.post(
            f"https://cloudscheduler.googleapis.com/v1/projects/my-project/locations/europe-west-1/jobs/plan-{plan_id}:resume"  # noqa
        ).mock(return_value=Response(200, json={}))

        await rbly.execute_plan(
            p,
            d,
            environment.schemas.Environment.model_validate(env, from_attributes=True),
            [
                integration.schemas.IntegrationFull(
                    id=str(intg.id),
                    org_id=org_id,
                    name=i.name,
                    provider=i.provider,
                    environment=environment.schemas.Environment.model_validate(
                        envint,
                        from_attributes=True
                    )
                )
            ],
            org.id,
            user_id,
            None
        )

        await rbly.suspend_plan(
            p,
            d,
        )

        await rbly.resume_plan(
            p,
            d,
        )