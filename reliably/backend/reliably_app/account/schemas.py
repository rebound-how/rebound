from datetime import datetime
from typing import Any, Dict, List

from authlib.oidc.core import UserInfo
from pydantic import UUID4, ConfigDict, field_validator

from reliably_app.schemas import BaseSchema

__all__ = ["User", "UserCreate", "UserIdentifier", "Users", "UserProfile"]


class UserBase(BaseSchema):  # pragma: no cover
    username: str
    email: str | None = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    created_date: datetime


class UserCreate(UserBase):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    openid: dict | None = None
    as_agent: bool = False

    @field_validator("openid", mode="before")
    @classmethod
    def convert_to_openid(cls, v: Dict[str, str] | None) -> UserInfo | None:
        if v is None:
            return None

        return UserInfo(v)


class UserIdentifier(BaseSchema):  # pragma: no cover
    user_id: UUID4


class Users(BaseSchema):
    count: int
    items: List[User]


class UserProfile(UserBase):  # pragma: no cover
    id: UUID4
    openid_profile: Dict[str, Any]
