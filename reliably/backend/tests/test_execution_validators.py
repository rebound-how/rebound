import uuid

import pytest
from faker import Faker
from fastapi import HTTPException

from reliably_app import execution, experiment, organization
from reliably_app.database import SessionLocal


@pytest.mark.anyio
async def test_valid_execution(stack_ready, fake: Faker):
    user_id = str(uuid.uuid4())

    async with SessionLocal() as db:
        org = await organization.crud.create_org(
            db, organization.schemas.OrganizationCreate(name=fake.name())
        )

        exp = await experiment.crud.create_experiment(
            db, org.id, experiment.schemas.ExperimentCreate(definition={})
        )

        exec = await execution.crud.create_execution(
            db, org.id, exp.id, user_id, execution.schemas.ExecutionCreate(result={})
        )

    async with SessionLocal() as db:
        x = await execution.validators.valid_execution(exec.id, exp, db)
        assert x.id == exec.id
        assert x.org_id == org.id
        assert x.experiment_id == exp.id


@pytest.mark.anyio
async def test_valid_execution_requires_execution_to_belong_to_org(
    stack_ready, fake: Faker
):
    user_id = str(uuid.uuid4())

    async with SessionLocal() as db:
        org = await organization.crud.create_org(
            db, organization.schemas.OrganizationCreate(name=fake.name())
        )

        exp = await experiment.crud.create_experiment(
            db, org.id, experiment.schemas.ExperimentCreate(definition={})
        )

        exp2 = await experiment.crud.create_experiment(
            db, org.id, experiment.schemas.ExperimentCreate(definition={})
        )

        exec = await execution.crud.create_execution(
            db, org.id, exp.id, user_id, execution.schemas.ExecutionCreate(result={})
        )

    async with SessionLocal() as db:
        with pytest.raises(HTTPException):
            await execution.validators.valid_execution(exec.id, exp2, db)


@pytest.mark.anyio
async def test_valid_execution_requires_execution_to_exist(
    stack_ready, fake: Faker
):
    async with SessionLocal() as db:
        org = await organization.crud.create_org(
            db, organization.schemas.OrganizationCreate(name=fake.name())
        )

        exp = await experiment.crud.create_experiment(
            db, org.id, experiment.schemas.ExperimentCreate(definition={})
        )

    async with SessionLocal() as db:
        with pytest.raises(HTTPException):
            await execution.validators.valid_execution(
                str(uuid.uuid4()), exp, db
            )
