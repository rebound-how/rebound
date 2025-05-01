from datetime import datetime
from enum import Enum
from typing import List, Literal, cast

import pytz
from cron_validator import CronValidator
from pydantic import UUID4, ConfigDict, RootModel, field_validator

from reliably_app.schemas import BaseSchema

__all__ = ["Plan", "PlanCreate", "Plans", "PlanStatus", "PlanNewStatus"]


class PlanStatus(str, Enum):
    creating = "creating"
    created = "created"
    deleted = "deleted"
    deleting = "deleting"
    creation_error = "creation error"
    deletion_error = "deletion error"
    running = "running"
    running_error = "error"
    completed = "completed"
    iteration_completed = "iteration completed"
    suspending = "suspending"
    suspended = "suspended"
    resuming = "resuming"
    suspend_error = "suspend_error"
    resuming_error = "resuming_error"


class PlanGitHubEnvironment(BaseSchema):
    provider: Literal["github"] = "github"
    name: str
    id: UUID4 | None = None


class PlanReliablyEnvironment(BaseSchema):
    provider: Literal["reliably_cloud"] = "reliably_cloud"
    id: UUID4 | None = None


class PlanDeployment(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    deployment_id: UUID4
    deployment_type: (
        Literal[
            "github",
            "reliably_cloud",
            "reliably_cli",
            "container",
            "k8s_job",
            "noop",
        ]
        | None
    ) = None


class PlanScheduleBase(BaseSchema):
    via_agent: bool = False


class PlanScheduleNow(PlanScheduleBase):
    type: Literal["now"] = "now"


class PlanScheduleCron(PlanScheduleBase):
    type: Literal["cron"] = "cron"
    pattern: str
    timezone: str | None = "Etc/UTC"

    @field_validator("pattern")
    @classmethod
    def ensure_valid_cron_pattern(cls, v, **kwargs) -> str:  # type: ignore
        # can also raise ValueError itself
        if not CronValidator.parse(v):
            raise ValueError("invalid cron pattern")
        return cast(str, v)

    @field_validator("timezone")
    @classmethod
    def allowed_domains(cls, v: str | None, **kwargs) -> str:  # type: ignore
        if not v:
            return "Etc/UTC"

        try:
            pytz.timezone(v)
        except pytz.UnknownTimeZoneError:
            raise ValueError()

        return v


class PlanBase(BaseSchema):  # pragma: no cover
    title: str | None = None
    environment: PlanGitHubEnvironment | PlanReliablyEnvironment | None = None
    deployment: PlanDeployment
    schedule: PlanScheduleNow | PlanScheduleCron
    integrations: List[UUID4] | None = None
    experiments: List[UUID4]


class PlanLastRunningExecutionInfo(BaseSchema):
    id: UUID4 | None = None
    timestamp: datetime | None = None


class PlanLastTerminatedExecutionInfo(BaseSchema):
    id: UUID4 | None = None
    timestamp: datetime | None = None


class PlanLastExecutionInfo(BaseSchema):
    running: PlanLastRunningExecutionInfo | None = None
    terminated: PlanLastTerminatedExecutionInfo | None = None


class Plan(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    org_id: UUID4
    created_date: datetime
    definition: PlanBase
    ref: str
    status: PlanStatus
    error: str | None = None
    executions_count: int | None = None
    last_executions_info: PlanLastExecutionInfo | None = None


class PlanCreate(PlanBase):
    pass


class PlanUpdate(PlanBase):
    pass


class Plans(BaseSchema):
    count: int
    items: List[Plan]


class PlanNewStatus(BaseSchema):
    status: PlanStatus
    error: str | None = None


PlanStatusResponse = RootModel[dict[str, bool]]
