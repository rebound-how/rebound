from datetime import datetime
from typing import Any, Dict, List, Literal

from pydantic import UUID4

from reliably_app.schemas import BaseSchema

__all__ = [
    "Scenario",
    "Scenarios",
    "ScenarioItem",
    "ScenarioQuery",
    "ScenarioSuggestion",
    "ScenarioLight",
]


class ScenarioItemParameter(BaseSchema):
    key: str
    title: str
    type: str
    required: bool
    default: Any | None = None


class ScenarioItemRelated(BaseSchema):
    block: str
    name: str


class ScenarioItem(BaseSchema):
    name: str
    ref: str
    type: Literal["action", "probe"]
    tags: List[str]
    purpose: str
    background: bool = False
    parameters: List[ScenarioItemParameter]
    related: List[ScenarioItemRelated] | None = None


class ScenarioSuggestion(BaseSchema):
    items: List[ScenarioItem]


class ScenarioQuery(BaseSchema):
    question: str
    tags: List[str]
    integration_id: UUID4


class ScenarioMetaError(BaseSchema):
    message: str


class ScenarioMeta(BaseSchema):
    error: ScenarioMetaError | None = None


class ScenarioExperiment(BaseSchema):
    experiment_id: UUID4


class ScenarioItemCreateParameter(BaseSchema):
    name: str
    type: Literal["string", "number", "integer", "float", "boolean", "object"]
    value: Any


class ScenarioCreateItem(BaseSchema):
    name: str
    parameters: List[ScenarioItemCreateParameter]
    target: Literal["method", "rollbacks", "hypothesis"]


class ScenarioExperimentCreate(BaseSchema):
    title: str
    description: str
    tags: List[str]
    contributions: (
        Dict[str, Literal["none", "low", "medium", "high"]] | None
    ) = None
    items: List[ScenarioCreateItem]


class ScenarioLight(BaseSchema):
    id: UUID4
    org_id: UUID4
    user_id: UUID4
    experiment_id: UUID4 | None = None
    plan_id: UUID4 | None = None
    integration_id: UUID4 | None = None
    created_date: datetime
    completed: bool = False
    query: ScenarioQuery
    meta: ScenarioMeta | None = None


class Scenario(BaseSchema):
    id: UUID4
    org_id: UUID4
    user_id: UUID4
    experiment_id: UUID4 | None = None
    plan_id: UUID4 | None = None
    integration_id: UUID4 | None = None
    created_date: datetime
    completed: bool = False
    query: ScenarioQuery
    suggestion: ScenarioSuggestion
    meta: ScenarioMeta | None = None


class Scenarios(BaseSchema):
    count: int
    items: List[Scenario]
