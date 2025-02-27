from sqlalchemy import Boolean, Column, DateTime, String, func, text, true
from sqlalchemy.dialects.postgresql import JSONB, UUID

from reliably_app.database import Base

__all__ = ["AuthFlow"]


class AuthFlow(Base):
    __tablename__ = "auth_flow"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    active = Column(Boolean, server_default=true(), default=True)
    provider = Column(String, index=True, nullable=False)
    nonce = Column(String, unique=True, index=True, nullable=False)
    state = Column(JSONB, nullable=False)
