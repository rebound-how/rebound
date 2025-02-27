from typing import Any, Dict, List

import orjson
from sqlalchemy import Column, DateTime, Index, LargeBinary, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.types import TypeDecorator

from reliably_app.config import get_settings
from reliably_app.crypto import decrypt, encrypt
from reliably_app.database import Base

__all__ = ["Environment"]


class EnvironmentSecretType(TypeDecorator):
    impl = LargeBinary

    cache_ok = False

    def process_bind_param(  # type: ignore
        self, value: Dict[str, Any], dialect: Any
    ) -> bytes | None:
        if value is not None:
            settings = get_settings()
            return encrypt(orjson.dumps(value).decode("utf-8"), settings)

        return None

    def process_result_value(
        self, value: bytes, dialect: Any
    ) -> List[Dict[str, Any]] | None:
        if value is not None:
            settings = get_settings()
            return orjson.loads(decrypt(value, settings))  # type: ignore

        return None


class Environment(Base):
    __tablename__ = "environments"
    __mapper_args__ = {"eager_defaults": True}
    __table_args__ = (
        Index("ix_environments_definition", "envvars", postgresql_using="gin"),
    )

    id = Column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    name = Column(String, index=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    org_id = Column(UUID, nullable=False, index=True)
    used_for = Column(String, nullable=False)
    envvars = Column(JSONB, nullable=False)
    secrets = Column(EnvironmentSecretType, nullable=True)
