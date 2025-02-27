import uuid

import pytest

from reliably_app.job import crud, schemas
from reliably_app.database import SessionLocal


@pytest.mark.anyio
async def test_create_jobs(stack_ready):
    org_id = uuid.uuid4()
    async with SessionLocal() as db:
        job = await crud.create_job(
            db,
            org_id,
            schemas.JobCreate(
                user_id=uuid.uuid4(),
                pattern="* * * * *",
                definition=schemas.JobPlan(
                    type="plan",
                    plan_id=uuid.uuid4(),
                )
            )
        )

        assert job is not None
