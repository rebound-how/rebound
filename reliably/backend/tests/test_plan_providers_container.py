import uuid
from datetime import datetime
import tempfile

import docker
import pytest
import respx
import ujson
from docker.errors import NotFound
from httpx import Response

from reliably_app import agent, deployment, environment, experiment, integration, job, organization, plan
from reliably_app.database import SessionLocal
from reliably_app.plan.errors import PlanFailedError
from reliably_app.plan.providers import container
from reliably_app.task import get_org_id_hash_prefix


@pytest.mark.anyio
async def test_container_execute_plan(stack_ready, application):
    with tempfile.TemporaryDirectory() as v:
        async with SessionLocal() as db:
            oc = organization.schemas.OrganizationCreate(name="hello")
            org = await organization.crud.create_org(db, oc)
            assert org.id is not None
        org_id = str(org.id)
        prefix = get_org_id_hash_prefix(org_id)

        d = deployment.schemas.DeploymentCreate(
            name="hello",
            definition=deployment.schemas.DeploymentContainerDefinition.model_validate(  # noqa
                dict(
                    image="ubuntu:rolling",
                    volumes={
                        v: {
                            "bind": "/tmp/b",
                        }
                    }
                )
            ),
        )

        async with SessionLocal() as db:
            dep = await deployment.crud.create_deployment(db, org.id, d)
            assert dep.id is not None

            d = deployment.schemas.Deployment.model_validate(
                dep, from_attributes=True
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
                deployment=plan.schemas.PlanDeployment(deployment_id=str(dep.id)),
                schedule=plan.schemas.PlanScheduleNow(),
                experiments=[str(exp.id)],
            ),
        )

        user_id = str(uuid.uuid4())
        async with SessionLocal() as db:
            agt = await agent.crud.create_user_agent(org, user_id, True)
            assert agt.id is not None

        secret_name = f"{prefix}_RAT_{str(plan_id)}"

        await container.execute_plan(
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
                        envint, from_attributes=True
                    )
                )
            ],
            org.id,
            user_id,
        )

        client = docker.from_env()
        ctns = client.containers.list(filters={"label": f"plan_id={plan_id}"})
        if not ctns:
            pytest.fail("Container should have been created")

        await container.delete_plan(
            p,
            d,
            environment.schemas.Environment.model_validate(env, from_attributes=True)
        )

        with pytest.raises(NotFound):
            client.containers.get(str(plan_id))


@pytest.mark.anyio
async def test_execute_plan_with_error(stack_ready, application):
    d = deployment.schemas.DeploymentCreate(
        name="hello",
        definition=deployment.schemas.DeploymentContainerDefinition.model_validate(  # noqa
            dict(
                image="ub786556tu:rolling"
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
        dep = await deployment.crud.create_deployment(db, org_id, d)
        assert dep.id is not None
    
        d = deployment.schemas.Deployment.model_validate(
            dep, from_attributes=True
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

    with pytest.raises(PlanFailedError):
        await container.execute_plan(
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
            user_id
        )


@pytest.mark.anyio
async def test_reliably_delete_plan(stack_ready, application):
    d = deployment.schemas.DeploymentCreate(
        name="hello",
        definition=deployment.schemas.DeploymentContainerDefinition.model_validate(  # noqa
            dict(
                image="ubuntu:rolling",
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


    await container.delete_plan(p, d, environment.schemas.Environment.model_validate(env, from_attributes=True))


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
        definition=deployment.schemas.DeploymentContainerDefinition.model_validate(  # noqa
            dict(
                image="ubuntu:rolling",
            )
        ),
    )

    async with SessionLocal() as db:
        depl = await deployment.crud.create_deployment(db, org_id, d)
        assert depl.id is not None

    dep = deployment.schemas.Deployment.model_validate(depl, from_attributes=True)

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
            deployment=plan.schemas.PlanDeployment(deployment_id=str(dep.id)),
            schedule=plan.schemas.PlanScheduleCron(pattern="* * * * *"),
            experiments=[str(exp.id)],
        ),
    )

    user_id = str(uuid.uuid4())
    async with SessionLocal() as db:
        agt = await agent.crud.create_user_agent(org, user_id, True)
        assert agt.id is not None


    await container.suspend_plan(p, dep)


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
        definition=deployment.schemas.DeploymentContainerDefinition.model_validate(  # noqa
            dict(
                image="ubuntu:rolling",
            )
        ),
    )

    async with SessionLocal() as db:
        depl = await deployment.crud.create_deployment(db, org_id, d)
        assert depl.id is not None

    dep = deployment.schemas.Deployment.model_validate(depl, from_attributes=True)

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
            deployment=plan.schemas.PlanDeployment(deployment_id=str(dep.id)),
            schedule=plan.schemas.PlanScheduleCron(pattern="* * * * *"),
            experiments=[str(exp.id)],
        ),
    )

    user_id = str(uuid.uuid4())
    async with SessionLocal() as db:
        agt = await agent.crud.create_user_agent(org, user_id, True)
        assert agt.id is not None

    await container.suspend_plan(p, dep)

    await container.resume_plan(p, dep)
