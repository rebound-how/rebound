from sqlalchemy import Boolean, Column, DateTime, Index, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from reliably_app.database import Base

__all__ = ["User"]


class User(Base):
    __tablename__ = "users"
    __mapper_args__ = {"eager_defaults": True}
    __table_args__ = (
        Index(
            "ix_users_openid_profile", "openid_profile", postgresql_using="gin"
        ),
    )

    id = Column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=False, index=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    as_agent = Column(Boolean, nullable=True, default=False)
    openid_profile = Column(JSONB, nullable=False)
    password = Column(String, nullable=True)
