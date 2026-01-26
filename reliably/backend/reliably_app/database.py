import asyncio
import logging
import os
import ssl
import tempfile
from pathlib import Path
from typing import Callable

import asyncpg
import orjson
import uvloop
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import Bundle, registry, sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.schema import MetaData

from reliably_app.config import Settings

__all__ = [
    "create_db_engine",
    "create_ssl_context",
    "Base",
    "DictBundle",
    "check_db_ready",
]


SessionLocal = sessionmaker(  # type: ignore
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)
meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

mapper_registry = registry(metadata=meta)
logger = logging.getLogger("reliably_app")


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True
    registry = mapper_registry
    metadata = mapper_registry.metadata
    __init__ = mapper_registry.constructor


def _json_dumps(*args, **kwargs) -> str:  # type: ignore[no-untyped-def]
    return orjson.dumps(*args, **kwargs).decode("utf-8")


def create_db_engine(settings: Settings) -> AsyncEngine:
    """
    Initialize the SQLAlchemy engine and bind it to the session factory.
    """
    sslctx = create_ssl_context(settings)
    engine = create_async_engine(
        str(settings.DATABASE_URL),
        pool_pre_ping=True,
        future=True,
        echo=False,
        json_deserializer=orjson.loads,
        json_serializer=_json_dumps,
        connect_args={"ssl": sslctx},
    )

    SessionLocal.configure(bind=engine)
    return engine


def create_ssl_context(settings: Settings) -> ssl.SSLContext | None:
    """
    Create a SSL context if enabled with `DATABASE_WITH_SSL`, appropriate
    for the PotsgreSQL driver.
    """
    if not settings.DATABASE_WITH_SSL:
        return None

    chain_file = get_or_make_file(settings.DATABASE_SSL_SERVER_CA_FILE)
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=chain_file)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    crt_file = get_or_make_file(settings.DATABASE_SSL_CLIENT_CERT_FILE)
    key_file = get_or_make_file(settings.DATABASE_SSL_CLIENT_KEY_FILE)
    if crt_file and key_file:
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_cert_chain(certfile=crt_file, keyfile=key_file)
        ctx.check_hostname = False

    return ctx


def get_or_make_file(candidate: str | Path | None) -> str | None:
    """
    Candidate can be the path to a file or the content of the file. In that
    latter case, we create a temporary file, write the content and return
    its path.
    """
    if not candidate:
        return None

    if isinstance(candidate, Path):
        candidate = str(candidate.absolute())

    if not os.path.isfile(candidate):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(candidate.encode("utf-8"))
            f.seek(0)
            logger.info(f"Wrote file to {f.name}")
            return f.name

    return candidate


# https://docs.sqlalchemy.org/en/14/orm/loading_columns.html#column-bundles
class DictBundle(Bundle):
    def create_row_processor(  # type: ignore
        self, query, procs, labels
    ) -> Callable:
        def proc(row):  # type: ignore
            return dict(zip(labels, (proc(row) for proc in procs)))

        return proc


async def _check_db_ready(db_url: str, timeout: float = 0.1) -> bool:
    db_url = db_url.replace("+asyncpg", "")

    async def test_postgresql() -> bool:
        try:
            c = await asyncpg.connect(db_url, timeout=0.5)
            try:
                await c.close()
            finally:
                return True
        except Exception:
            return False

    count = 0
    while count <= 10:
        if await test_postgresql():
            return True

        timeout = timeout * 1.2
        await asyncio.sleep(timeout)
        count += 1

    return False


def check_db_ready(db_url: str) -> bool:
    """
    Loops, up to 10 times, until database can be connected to.
    """
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        return runner.run(_check_db_ready(db_url))


async def _get_current_revision_from_pgsql(db_url: str) -> str | None:
    db_url = db_url.replace("+asyncpg", "")
    c = await asyncpg.connect(db_url, timeout=0.5)
    try:
        v = await c.fetchrow("SELECT version_num FROM alembic_version")
        return v.get("version_num")  # type: ignore
    except Exception:
        return None
    finally:
        await c.close()


def get_current_revision(db_url: str) -> str | None:
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        return runner.run(_get_current_revision_from_pgsql(db_url))
