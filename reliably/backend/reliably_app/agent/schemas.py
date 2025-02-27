from datetime import datetime
from typing import List

from pydantic import UUID4, ConfigDict

from reliably_app.schemas import BaseSchema

__all__ = [
    "Agent",
    "AgentCreate",
    "Agents",
    "AgentState",
]


class AgentBase(BaseSchema):  # pragma: no cover
    user_id: UUID4
    token_id: UUID4


class AgentState(BaseSchema):
    status: str
    scheduled_plans: int = 0
    received_time: datetime | None = None


class Agent(AgentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    org_id: UUID4
    created_date: datetime
    state: AgentState | None = None


class AgentCreate(AgentBase):
    sub: str


class Agents(BaseSchema):
    count: int
    items: List[Agent]
