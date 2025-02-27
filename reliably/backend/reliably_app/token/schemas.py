from datetime import datetime
from typing import List

from pydantic import UUID4, ConfigDict, SecretBytes, field_serializer

from reliably_app.schemas import BaseSchema

__all__ = ["Token", "TokenCreate", "TokenMeta", "Tokens"]


class Token(BaseSchema):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID4
    name: str
    created_date: datetime
    token: SecretBytes

    @field_serializer("token", when_used="json")
    def dump_token(self, v: SecretBytes) -> str | None:
        if not v:
            return None

        return v.get_secret_value().decode("utf-8")


class TokenMeta(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    name: str
    created_date: datetime


class TokenCreate(BaseSchema):
    name: str


class Tokens(BaseSchema):
    count: int
    items: List[Token]
