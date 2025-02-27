from sqlalchemy import Boolean, Column, DateTime, Index, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from reliably_app.database import Base

__all__ = ["AssistantScenario"]


class AssistantScenario(Base):
    __tablename__ = "assitant_scenario"
    __mapper_args__ = {"eager_defaults": True}
    __table_args__ = (
        Index("ix_assitant_scenario_query", "query", postgresql_using="gin"),
        Index(
            "ix_assitant_scenario_suggestion",
            "suggestion",
            postgresql_using="gin",
        ),
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
    experiment_id = Column(UUID, nullable=True, index=True)
    plan_id = Column(UUID, nullable=True, index=True)
    integration_id = Column(UUID, nullable=True, index=True)
    completed = Column(Boolean, nullable=False, default=False)
    query = Column(JSONB, nullable=False)
    suggestion = Column(JSONB, nullable=True)
    meta = Column(JSONB, nullable=True)
