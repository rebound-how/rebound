import uuid

from cryptography.fernet import Fernet
import pytest
from sqlalchemy import asc, delete, func, select

from reliably_app import environment
from reliably_app.config import Settings
from reliably_app.database import SessionLocal


@pytest.mark.anyio
async def test_secret_type_encryption(stack_ready, settings: Settings) -> None:

    secret_key = Fernet.generate_key()
    _settings = settings.model_copy(deep=True)
    _settings.CRYPTO_PROVIDER = "cryptography"
    _settings.CRYPTO_CRYPTOGRAPHY_SECRET_KEY = secret_key

    s = [
        {
            "key": "message",
            "var_name": "MESSAGE",
            "value": "try to catch me"
        }
    ]

    e = environment.models.Environment(
        name="test",
        org_id=str(uuid.uuid4()),
        envvars=[],
        secrets=s,
        used_for="plan",
    )

    async with SessionLocal() as db:
        db.add(e)
        await db.commit()

    async with SessionLocal() as db:
        r = await db.get(environment.models.Environment, e.id)
        assert r.secrets == s


@pytest.mark.anyio
async def test_secret_type_encryption_on_no_secrets(stack_ready, settings: Settings) -> None:

    secret_key = Fernet.generate_key()
    _settings = settings.model_copy(deep=True)
    _settings.CRYPTO_PROVIDER = "cryptography"
    _settings.CRYPTO_CRYPTOGRAPHY_SECRET_KEY = secret_key

    e = environment.models.Environment(
        name="test",
        org_id=str(uuid.uuid4()),
        envvars=[],
        secrets=None,
        used_for="plan",
    )

    async with SessionLocal() as db:
        db.add(e)
        await db.commit()

    async with SessionLocal() as db:
        r = await db.get(environment.models.Environment, e.id)
        assert r.secrets is None
