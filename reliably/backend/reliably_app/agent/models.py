from sqlalchemy import (
    Boolean,
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

__all__ = ["Agent"]


class Agent(Base):
    __tablename__ = "agents"
    __mapper_args__ = {"eager_defaults": True}
    __table_args__ = (
        Index("ix_agents_state", "state", postgresql_using="gin"),
        UniqueConstraint("name", "org_id"),
        UniqueConstraint("user_id", "org_id"),
        UniqueConstraint("token_id", "org_id"),
    )

    id = Column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    org_id = Column(UUID, nullable=False, index=True)
    user_id = Column(UUID, nullable=False, index=True)
    from_user_id = Column(UUID, nullable=True, index=True)
    token_id = Column(UUID, nullable=False, index=True)
    name = Column(String, nullable=False)
    internal = Column(Boolean, nullable=True, default=False)
    state = Column(JSONB, nullable=True)
