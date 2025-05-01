from datetime import datetime
from typing import Any, Dict, List

import orjson
from pydantic import UUID4, ConfigDict, Json, RootModel, field_validator

from reliably_app.schemas import BaseSchema

__all__ = [
    "Experiment",
    "ExperimentCreate",
    "Experiments",
    "ExperimentImport",
    "ExperimentsBasic",
    "ExperimentsSummary",
    "ExperimentEdit",
]


class ExperimentBase(BaseSchema):  # pragma: no cover
    definition: Json[Dict[str, Any]]

    @field_validator("definition", mode="before")
    @classmethod
    def ensure_json_string(cls, v, **kwargs) -> Json:  # type: ignore
        if isinstance(v, dict):
            v = orjson.dumps(v)
        return v


class Experiment(ExperimentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    org_id: UUID4
    template_id: UUID4 | None = None
    created_date: datetime
    executions_count: int | None = None


class ExperimentBasic(BaseSchema):
    id: str | UUID4
    template_id: UUID4 | None = None
    title: str
    executions_count: int | None = None


class ExperimentSummary(BaseSchema):
    id: str | UUID4
    title: str
    desc: str | None = None
    created_by: str | None = None
    created_date: datetime
    org_id: UUID4
    template_id: UUID4 | None = None
    last_statuses: List[str | None]
    last_execution: datetime | None = None
    score: float | None = None
    trend: List[tuple[UUID4, str, float]] | None = None
    executions_count: int | None = None


class ExperimentCreate(ExperimentBase):
    template_id: UUID4 | None = None


class Experiments(BaseSchema):
    count: int
    items: List[Experiment]


class ExperimentsBasic(BaseSchema):
    count: int
    items: List[ExperimentBasic]


class ExperimentsSummary(BaseSchema):
    count: int
    items: List[ExperimentSummary]


class ExperimentImport(BaseSchema):
    experiment: Json[Dict[str, Any]]

    @field_validator("experiment")
    @classmethod
    def valid_chaostoolkit_experiment(cls, v, **kwargs) -> Json:  # type: ignore
        extensions = v.get("extensions", [])
        for extension in extensions:
            if extension.get("name") == "reliably":
                extensions.remove(extension)
                break

        controls = v.get("controls", [])
        for c in controls:
            if c["name"] == "reliably":
                controls.remove(c)
                break

        return v


class ExperimentEdit(BaseSchema):
    experiment: Json[Dict[str, Any]]


ExperimentIds = RootModel[List[UUID4]]

ChaosToolkitExperiment = RootModel[Dict[str, Any]]
