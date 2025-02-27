from sqlalchemy import (
    Column,
    DateTime,
    Index,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from reliably_app.database import Base

__all__ = ["Deployment"]


class Deployment(Base):
    __tablename__ = "deployments"
    __mapper_args__ = {"eager_defaults": True}
    __table_args__ = (
        Index(
            "ix_deployments_definition", "definition", postgresql_using="gin"
        ),
        UniqueConstraint("name", "org_id"),
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
    definition = Column(JSONB, nullable=False)
