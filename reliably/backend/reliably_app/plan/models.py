from sqlalchemy import (
    Column,
    DateTime,
    Identity,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from reliably_app.database import Base

__all__ = ["Schedulable", "Plan"]


class Plan(Base):
    __tablename__ = "plans"
    __mapper_args__ = {"eager_defaults": True}
    __table_args__ = (
        Index("ix_plans_definition", "definition", postgresql_using="gin"),
    )

    id = Column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    org_id = Column(UUID, nullable=False, index=True)
    ref = Column(String, nullable=False, index=True, unique=True)
    status = Column(String, nullable=False, index=True)
    executions_count = Column(Integer, nullable=True, default=0)
    error = Column(String)
    definition = Column(JSONB, nullable=False)
    last_executions_info = Column(JSONB, nullable=True)


class Schedulable(Base):
    __tablename__ = "schedulables"
    __table_args__ = (UniqueConstraint("org_id", "plan_id"),)

    id = Column(Integer, Identity(cycle=True), primary_key=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    scheduled_date = Column(DateTime(timezone=True))
    org_id = Column(UUID, nullable=False, index=True)
    plan_id = Column(UUID, nullable=False, index=True)
    agent_id = Column(UUID, nullable=True, index=True)
    deployment_type = Column(String, nullable=False)
