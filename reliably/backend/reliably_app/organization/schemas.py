from datetime import datetime
from typing import List

from pydantic import UUID4, ConfigDict, constr

from reliably_app import account
from reliably_app.schemas import BaseSchema

__all__ = [
    "Organization",
    "OrganizationCreate",
    "OrganizationInvite",
    "OrganizationUsers",
    "Organizations",
    "OrganizationNameCandidate",
]


class Organization(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    name: str
    created_date: datetime


class OrganizationUsers(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    org: Organization
    users: List[account.schemas.User]


class OrganizationCreate(BaseSchema):
    name: str


class OrganizationUserInvite(BaseSchema):
    user_id: UUID4


class Organizations(BaseSchema):
    count: int
    items: List[Organization]


class OrganizationInvite(BaseSchema):
    link: str | None


class OrganizationNameCandidate(BaseSchema):
    name: constr(  # type: ignore
        strip_whitespace=True, strict=True, min_length=3, max_length=64
    )


class OrganizationNameAvailable(BaseSchema):
    available: bool = False
