from sqlalchemy import Column, DateTime, Index, Integer, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from reliably_app.database import Base

__all__ = ["Experiment"]


class Experiment(Base):
    __tablename__ = "experiments"
    __mapper_args__ = {"eager_defaults": True}
    __table_args__ = (
        Index(
            "ix_experiments_definition", "definition", postgresql_using="gin"
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
    template_id = Column(UUID, nullable=True, index=True)
    executions_count = Column(Integer, nullable=True, default=0)
    definition = Column(JSONB, nullable=False)
