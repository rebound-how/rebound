from sqlalchemy import Column, DateTime, Index, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from reliably_app.database import Base

__all__ = ["Series"]


class Series(Base):
    __tablename__ = "series"
    __mapper_args__ = {"eager_defaults": True}
    __table_args__ = (Index("ix_series_data", "data", postgresql_using="gin"),)

    id = Column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    kind = Column(String, nullable=False, index=True)
    org_id = Column(UUID, nullable=False, index=True)
    experiment_id = Column(UUID, nullable=True, index=True)
    execution_id = Column(UUID, nullable=True, index=True)
    plan_id = Column(UUID, nullable=True, index=True)
    data = Column(JSONB, nullable=False)
