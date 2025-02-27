from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    LargeBinary,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from reliably_app.database import Base

__all__ = ["Token"]


class Token(Base):
    __tablename__ = "tokens"
    __table_args__ = (UniqueConstraint("org_id", "user_id", "name"),)
    __mapper_args__ = {"eager_defaults": True}

    id = Column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    org_id = Column("org_id", UUID, nullable=False, index=True)
    user_id = Column("user_id", UUID, nullable=False, index=True)
    name = Column(String, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    token = Column(LargeBinary, nullable=False)
