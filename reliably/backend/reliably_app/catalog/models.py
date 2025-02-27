from sqlalchemy import Column, DateTime, Index, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from reliably_app.database import Base

__all__ = ["Catalog"]


class Catalog(Base):
    __tablename__ = "catalogs"
    __mapper_args__ = {"eager_defaults": True}
    __table_args__ = (
        Index("ix_catalogs_manifest", "manifest", postgresql_using="gin"),
    )

    id = Column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    org_id = Column(UUID, nullable=False, index=True)
    user_id = Column(UUID, nullable=True, index=True)
    manifest = Column(JSONB, nullable=True)
