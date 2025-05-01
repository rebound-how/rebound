from datetime import datetime
from typing import Any, Dict, List, Literal

from pydantic import UUID4, ConfigDict, RootModel

from reliably_app import environment
from reliably_app.schemas import BaseSchema

__all__ = [
    "Integration",
    "IntegrationCreate",
    "Integrations",
    "IntegrationFull",
    "IntegrationControl",
]


class IntegrationBase(BaseSchema):
    name: str
    provider: Literal[
        "opentelemetry",
        "slack",
        "prechecks",
        "safeguards",
        "autopause",
        "chatgpt",
        "assistant",
        "snapshot",
        "notification",
    ]
    vendor: (
        Literal[
            "dynatrace",
            "honeycomb",
            "gcp",
            "slack",
            "reliably",
            "openai",
            "grafana",
            "gcp",
        ]
        | None
    ) = None


class Integration(IntegrationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    org_id: UUID4
    created_date: datetime
    environment_id: UUID4


class IntegrationFull(IntegrationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    org_id: UUID4
    environment: environment.schemas.Environment


class IntegrationCreate(IntegrationBase):
    environment: environment.schemas.EnvironmentCreate


class Integrations(BaseSchema):
    count: int
    items: List[Integration]


class IntegrationControlPythonProvider(BaseSchema):
    type: Literal["python"] = "python"
    module: str
    secrets: List[str] | None = None
    arguments: Dict[str, Any] | None = None


class IntegrationControl(BaseSchema):
    name: str
    provider: IntegrationControlPythonProvider


IntegrationIds = RootModel[List[UUID4]]
