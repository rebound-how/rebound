from datetime import datetime
from typing import Dict

from pydantic import UUID4, ConfigDict

from reliably_app.schemas import BaseSchema

__all__ = [
    "AuthFlow",
]


class AuthFlow(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    created_date: datetime
    provider: str
    state: Dict[str, str]
