from datetime import datetime, timezone
from typing import Any, Dict, List, Literal

import orjson
from pydantic import (
    UUID4,
    ConfigDict,
    Field,
    Json,
    RootModel,
    conint,
    field_validator,
)

from reliably_app.schemas import BaseSchema

__all__ = ["Execution", "ExecutionCreate", "Executions"]


class ExecutionPendingState(BaseSchema):
    current: Literal["pending"] = "pending"
    plan_id: UUID4 | None = None
    created_on: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )


class ExecutionRunningState(BaseSchema):
    current: Literal["running"] = "running"
    plan_id: UUID4 | None = None
    started_on: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )


class ExecutionFinishedState(BaseSchema):
    current: Literal["finished"] = "finished"
    plan_id: UUID4 | None = None
    finished_on: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    status: Literal["interrupted", "aborted", "completed", "failed"] | None = (
        None
    )
    deviated: bool = False


class ExecutionStateUser(BaseSchema):
    name: str
    id: UUID4


class ExecutionTerminateState(BaseSchema):
    current: Literal["terminate"] = "terminate"
    plan_id: UUID4 | None = None
    skip_rollbacks: bool = False
    user: ExecutionStateUser | None = None


class ExecutionPauseState(BaseSchema):
    current: Literal["pause"] = "pause"
    plan_id: UUID4 | None = None
    duration: conint(ge=0, le=3300, strict=True)  # type: ignore
    user: ExecutionStateUser | None = None


class ExecutionResumeState(BaseSchema):
    current: Literal["resume"] = "resume"
    plan_id: UUID4 | None = None
    user: ExecutionStateUser | None = None


class ExecutionBase(BaseSchema):  # pragma: no cover
    result: Json[Dict[str, Any]]

    @field_validator("result", mode="before")
    @classmethod
    def ensure_json_string(cls, v, **kwargs) -> Json:  # type: ignore
        if isinstance(v, dict):
            v = orjson.dumps(v)
        return v


class Execution(ExecutionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    org_id: UUID4
    experiment_id: UUID4
    plan_id: UUID4 | None = None
    user_id: UUID4 | None = None
    created_date: datetime
    user_state: (
        ExecutionTerminateState
        | ExecutionPauseState
        | ExecutionPendingState
        | ExecutionRunningState
        | ExecutionFinishedState
        | ExecutionResumeState
        | None
    ) = None


class ExecutionCreate(ExecutionBase):
    plan_id: UUID4 | None = None
    result: Json[Dict[str, Any]]
    log: str | None = None


class Executions(BaseSchema):
    count: int
    items: List[Execution]


class ExecutionStateSetter(BaseSchema):
    state: (
        ExecutionTerminateState
        | ExecutionPauseState
        | ExecutionPendingState
        | ExecutionRunningState
        | ExecutionFinishedState
        | ExecutionResumeState
    )


class ExecutionWithoutLogNorJournal(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    org_id: UUID4
    experiment_id: UUID4
    plan_id: UUID4 | None = None
    user_id: UUID4 | None = None
    created_date: datetime
    user_state: (
        ExecutionTerminateState
        | ExecutionPauseState
        | ExecutionPendingState
        | ExecutionRunningState
        | ExecutionFinishedState
        | ExecutionResumeState
        | None
    ) = None


ChaosToolkitResults = RootModel[Dict[str, Any]]
