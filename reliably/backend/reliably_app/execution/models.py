from sqlalchemy import Column, DateTime, Index, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from reliably_app.database import Base

__all__ = ["Execution"]


class Execution(Base):
    __tablename__ = "executions"
    __mapper_args__ = {"eager_defaults": True}
    __table_args__ = (
        Index("ix_executions_result", "result", postgresql_using="gin"),
    )

    id = Column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    org_id = Column(UUID, nullable=False, index=True)
    experiment_id = Column(UUID, nullable=False, index=True)
    plan_id = Column(UUID, nullable=True, index=True)
    user_id = Column(UUID, nullable=True, index=True)
    user_state = Column(JSONB, nullable=True)
    result = Column(JSONB, nullable=False)
    log = Column(Text, nullable=True, index=False)
