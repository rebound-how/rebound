from datetime import datetime, timezone
from typing import Literal

from pydantic import UUID4, AwareDatetime, Field

from reliably_app import deployment, experiment, plan
from reliably_app.schemas import BaseSchema

__all__ = ["Event", "PlanEvent", "WebHookNotification"]


class Event(BaseSchema):
    org_id: UUID4
    kind: str
    start_date: AwareDatetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )


class PlanEvent(Event):
    kind: Literal["plan-phases"]
    plan: plan.schemas.Plan
    experiment: experiment.schemas.ExperimentSummary
    deployment: deployment.schemas.Deployment | None
    execution_id: UUID4 | None = None
    deviated: bool = False
    status: str | None = None


class Notification(BaseSchema):
    event: Event


class WebHookMeta(BaseSchema):
    org_id: UUID4
    triggered: AwareDatetime
    event: Literal["plan-phases"]


class WebHookExecution(BaseSchema):
    execution_id: UUID4 | None = None
    verified: bool = False
    status: str | None = None


class WebHookNotification(BaseSchema):
    meta: WebHookMeta
    plan: plan.schemas.Plan
    experiment: experiment.schemas.ExperimentSummary
    execution: WebHookExecution | None = None
