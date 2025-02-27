from sqlalchemy import Boolean, Column, DateTime, Index, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from reliably_app.database import Base

__all__ = ["Job"]


class Job(Base):
    __tablename__ = "jobs"
    __mapper_args__ = {"eager_defaults": True}
    __table_args__ = (
        Index("ix_jobs_definition", "definition", postgresql_using="gin"),
    )

    id = Column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    next_run_date = Column(DateTime(timezone=True), nullable=True)
    org_id = Column(UUID, nullable=False, index=True)
    user_id = Column(UUID, nullable=True, index=True)
    claimed = Column(Boolean, nullable=False, index=True)
    suspended = Column(Boolean, nullable=True)
    errored = Column(Boolean, nullable=True)
    pattern = Column(String, nullable=False)
    timezone = Column(String, nullable=True, default="Etc/UTC")
    error_message = Column(String, nullable=True)
    definition = Column(JSONB, nullable=False)
