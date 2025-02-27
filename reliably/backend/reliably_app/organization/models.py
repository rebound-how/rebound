import secrets

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Identity,
    Integer,
    String,
    UniqueConstraint,
    false,
    func,
    text,
    true,
)
from sqlalchemy.dialects.postgresql import BYTEA, UUID

from reliably_app.database import Base

__all__ = ["Organization", "OrganizationInvitation", "OrganizationUsers"]


class Organization(Base):
    __tablename__ = "organization"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    name = Column(String, nullable=False, index=True, unique=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    reset_date = Column(DateTime(timezone=True))
    experiments_count = Column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    executions_count = Column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    running_executions_count = Column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    plans_count = Column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    users_count = Column(
        Integer, nullable=False, default=1, server_default=text("1")
    )
    consumed_minutes = Column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    pending = Column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    blocked = Column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    deleted = Column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    service_account = Column(String, nullable=True)
    role = Column(String, nullable=True)


# we don't want strict foreignkey many-to-many relationships here.
# we just want to record the association in a loose way
class OrganizationUsers(Base):
    __tablename__ = "organization_users"
    __table_args__ = (UniqueConstraint("org_id", "user_id"),)

    id = Column(Integer, Identity(cycle=True), primary_key=True)
    org_id = Column("org_id", UUID, nullable=False, index=True)
    user_id = Column("user_id", UUID, nullable=False, index=True)
    owner = Column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    agent = Column(
        Boolean, nullable=False, default=False, server_default=false()
    )


class OrganizationInvitation(Base):
    __tablename__ = "organization_invitations"

    id = Column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    org_id = Column(UUID, nullable=False, index=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    active = Column(Boolean, server_default=true(), default=True, index=True)
    link_hash = Column(
        BYTEA, default=lambda: secrets.token_hex(16).encode("utf-8")
    )
