from sqlalchemy import Column, DateTime, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID

from reliably_app.database import Base

__all__ = ["Integration"]


class Integration(Base):
    __tablename__ = "integrations"
    __mapper_args__ = {"eager_defaults": True}
    __table_args__ = (
        UniqueConstraint("environment_id", "org_id"),
        UniqueConstraint("name", "org_id"),
    )

    id = Column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    name = Column(String, nullable=False, index=True, unique=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    org_id = Column(UUID, nullable=False, index=True)
    environment_id = Column(UUID, nullable=False, unique=True, index=True)
    provider = Column(String, nullable=False, unique=False, index=True)
    vendor = Column(String, nullable=True, unique=False)
