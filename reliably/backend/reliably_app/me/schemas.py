from typing import List

from pydantic import ConfigDict, RootModel

from reliably_app import account, organization, token
from reliably_app.schemas import BaseSchema

__all__ = ["Info", "Tokens"]


class Info(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    profile: account.schemas.UserProfile
    orgs: List[organization.schemas.Organization]


class Tokens(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    org: organization.schemas.Organization
    tokens: List[token.schemas.TokenMeta]


MyTokens = RootModel[List[Tokens]]
