from datetime import datetime
import re
import uuid
from contextlib import contextmanager

import pytest
import respx
from faker import Faker
from httpx import Response

from reliably_app import environment
from reliably_app.integration import errors, schemas, tasks


@pytest.mark.anyio
async def test_store_integration_secrets_requires_an_environment(stack_ready, fake: Faker) -> None:
    i = schemas.IntegrationFull(
            id=uuid.uuid4(),
            org_id=uuid.uuid4(),
            name=fake.name(),
            provider="slack",
            vendor=None,
            environment=environment.schemas.Environment(
                id=uuid.uuid4(),
                org_id=uuid.uuid4(),
                name=fake.name(),
                created_date=datetime.utcnow(),
                envvars=environment.schemas.EnvironmentVars(root=[]),
                secrets=environment.schemas.EnvironmentSecrets(root=[])
            )
        )
    assert await tasks.store_integration_secrets(i) is None


@pytest.mark.anyio
async def test_store_integration_secrets(stack_ready, fake: Faker) -> None:
    i = schemas.IntegrationFull(
        id=uuid.uuid4(),
        org_id=uuid.uuid4(),
        name=fake.name(),
        provider="slack",
        vendor=None,
        environment=environment.schemas.Environment(
            id=uuid.uuid4(),
            org_id=uuid.uuid4(),
            name=fake.name(),
            created_date=datetime.utcnow(),
            envvars=environment.schemas.EnvironmentVars(root=[]),
            secrets=environment.schemas.EnvironmentSecrets(root=[{
                "key": "my-secret",
                "var_name": "MY_SECRET",
                "value": "hello"
            }])
        )
    )

    try:
        await tasks.store_integration_secrets(i)
    except:
        pytest.fail("creating integration should not fail")
