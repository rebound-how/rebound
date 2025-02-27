import asyncio
import json
import os
import platform
import random
from base64 import b64encode
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Generator, Tuple

import alembic
import docker
import itsdangerous
import pytest
import pytest_alembic
import pytest_asyncio
import respx
import uvloop
from _pytest.monkeypatch import MonkeyPatch
from alembic.config import Config as AlembicConfig
from asgi_lifespan import LifespanManager
from authlib.oidc.core import UserInfo
from faker import Faker
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient, Response
from pytest_alembic.config import Config
from sqlalchemy import text, engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine

from reliably_app import account, agent, login, migrations, organization, token
from reliably_app.main import create_app
from reliably_app.config import Settings
from reliably_app.database import SessionLocal, meta, _check_db_ready
from reliably_app.organization.tasks import create_default_organizations

pytestmark = pytest.mark.anyio

truncate_query = text('TRUNCATE {} RESTART IDENTITY;'.format(
                    ','.join(table.name 
                        for table in reversed(meta.sorted_tables))))


@pytest.fixture(scope="session", params=[
    pytest.param(('asyncio', {'use_uvloop': True}), id='asyncio+uvloop'),
])
def anyio_backend(request):
    return request.param


@pytest.fixture(scope="session")
def patcher(request):
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session")
def db_port() -> int:
    return random.randint(5433, 5450)


# Wait for the container to start
async def check(port: int) -> None:
    dsn = f"postgresql://test:secret@127.0.0.1:{port}/test"
    assert await _check_db_ready(dsn) is True, "PostgreSQL took too long to start"


def _create_container(db_port: int) -> None:
    client = docker.from_env()
    container = client.containers.run(
        image="postgres:17",
        auto_remove=True,
        environment=dict(
            POSTGRES_PASSWORD="secret",
            POSTGRES_USER="test",
            POSTGRES_DB="test"
        ),
        name=f"test_{db_port}",
        ports={"5432/tcp": ("127.0.0.1", db_port)},
        detach=True,
        remove=True,
    )

    return container


@pytest.fixture(scope="session")
async def dependencies(db_port: int):
    container = await asyncio.to_thread(_create_container, db_port)
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(check(db_port))

        yield
    finally:
        await asyncio.to_thread(container.stop, timeout=2)


@pytest.fixture(scope="session")
def default_org_name() -> str:
    return Faker().name()


@pytest.fixture(scope="session")
def envvars(db_port: int) -> bytes:
    return f"""RELIABLY_DOMAIN="example.com"
APPLICATION_LOG_STDOUT="false"
DATABASE_MODE="extern"
DATABASE_URL="postgresql+asyncpg://test:secret@127.0.0.1:{db_port}/test"
OTEL_ENABLED=false
CRYPTO_PROVIDER="cryptography"
CRYPTO_CRYPTOGRAPHY_SECRET_KEY="15kdIS1qZax5IKes+9MIdEtLpSKio27wF5Wi3a5lCdY="
OAUTH_GITHUB_ENABLED="true"
OAUTH_GITHUB_CLIENT_ID="abc"
OAUTH_GITHUB_CLIENT_SECRET="xyz"
FEATURE_CLOUD_DEPLOYMENT="true"
FEATURE_LOGIN_EMAIL="true"
DEPLOYMENT_STRATEGY="gcp"
ENVIRONMENT_STORE_STRATEGY="gcp"
DEFAULT_ORGANIZATIONS='["test"]'
FEATURE_POPULATE_NEW_ORG_WITH_DEFAULTS="false"
""".encode("utf-8")


@pytest.fixture(scope="session")
def envfile(envvars: bytes) -> Generator[str, None, None]:
    with NamedTemporaryFile() as f:
        f.write(envvars)
        f.seek(0)
        yield f.name


@pytest.fixture(scope="session")
def settings(envfile: str) -> Settings:
    return Settings(_env_file=envfile)


@pytest.fixture(scope="session")
def application(envfile: str) -> FastAPI:
    app = create_app(envfile)
    return app


@pytest.fixture(scope="session")
def alembic_engine(settings: Settings) -> Generator[AsyncEngine, None, None]:
    url = str(settings.DATABASE_URL)
    # async with alembic isn't straightforward from pytest
    # https://github.com/schireson/pytest-alembic/issues/119
    engine = engine_from_config({
        "sqlalchemy.url": url.replace("+asyncpg", "+psycopg2"),
        "sqlalchemy.echo": False,
        "sqlalchemy.future": True
    })
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def alembic_config(envfile: str) -> alembic.config.Config:
    c = AlembicConfig()
    d = Path(migrations.__file__).parent.resolve().absolute()
    c.set_main_option("script_location", str(d))
    c.set_main_option("prepend_sys_path", str(d.parent.absolute()))
    c.set_main_option("env_file", str(Path(envfile).resolve().absolute()))

    return c


@pytest.fixture(scope="session")
def alembic_runner(alembic_config, alembic_engine):
    config = Config.from_raw_config(alembic_config)
    with pytest_alembic.runner(config=config, engine=alembic_engine) as runner:
        yield runner


@pytest.fixture(scope="session")
def init_db(dependencies, alembic_engine, alembic_runner: pytest_alembic.MigrationContext) -> None:
    """
    Ensures the db migration is executed on each test that requires the db
    """
    alembic_runner.migrate_up_to("head")
    yield
    alembic_runner.migrate_down_to("base")


@pytest.fixture
async def stack_ready(
    init_db: None, application: FastAPI
) -> None:
    yield

    # clear all data from any of the tables for next test
    async with application.db_engine.connect() as connection:
        await connection.execute(truncate_query)
        await connection.commit()


@pytest.fixture
def fake() -> Faker:
    f = Faker()
    Faker.seed(0)
    return f


@pytest.fixture
async def client(stack_ready: None, application: FastAPI) -> AsyncClient:
    base_url = "http://127.0.0.1:8090"

    async with LifespanManager(application):
        async with AsyncClient(transport=ASGITransport(app=application), base_url=base_url) as client:
            yield client



@pytest.fixture
def mock_cloud_resources_creation() -> None:
    @contextmanager
    def inner():
        with respx.mock(assert_all_called=False) as respx_mock:
            respx_mock.get(
                url__regex="http://metadata.google.internal/computeMetadata/v1/instance*"  # noqa
            ).mock(return_value=Response(200, json={"access_token": "abc"}))

            respx_mock.get(
                "http://metadata.google.internal/computeMetadata/v1/project/project-id"  # noqa
            ).mock(return_value=Response(200, text="myproject"))

            respx_mock.get(
                "http://metadata.google.internal/computeMetadata/v1/project/numeric-project-id"  # noqa
            ).mock(return_value=Response(200, text="123456"))

            respx_mock.post(
                url__regex=r"https://cloudresourcemanager.googleapis.com/v1/projects/.*:getIamPolicy"  # noqa
            ).mock(return_value=Response(200, json={"bindings": []}))

            respx_mock.post(
                url__regex=r"https://.*.googleapis.com/.*"  # noqa
            ).mock(return_value=Response(200, json={}))

            respx_mock.get(
                url__regex=r"https://.*.googleapis.com/.*"  # noqa
            ).mock(return_value=Response(200, json={}))

            yield respx_mock
    return inner


@pytest.fixture
async def authed(
    stack_ready: None, fake: Faker
) -> Tuple[
    organization.models.Organization, account.models.User, token.models.Token
]:
    name = fake.name()

    await create_default_organizations([name])

    org, user = await login.tasks.new_org(
        name=name,
        info=UserInfo(
            preferred_username=name, email=fake.company_email()
        ),
    )

    async with SessionLocal() as db:
        tc = token.schemas.TokenCreate(name="hello")
        t = await token.crud.create_token(db, org.id, user.id, tc)
        yield org, user, t


@pytest.fixture
def session_cookie(authed) -> Dict[str, str]:
    _, authed_user, _ = authed

    data = b64encode(json.dumps({"user": str(authed_user.id)}).encode("utf-8"))
    signer = itsdangerous.TimestampSigner("secret")
    s = signer.sign(data)
    return {"session": s.decode("utf-8")}


@pytest.fixture
async def agent_token(authed) -> str:
    authed_org, authed_user, _ = authed

    async with SessionLocal() as db:
        agt = await agent.crud.get_from_real_user_id(db, authed_org.id, authed_user.id)
        tk = await token.crud.get_tokens(db, authed_org.id, agt.user_id, limit=1)
        return tk[0].token.decode('utf-8')
