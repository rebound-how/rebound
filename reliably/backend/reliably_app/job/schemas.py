from datetime import datetime
from typing import List, Literal

from pydantic import UUID4, ConfigDict, Field

from reliably_app.schemas import BaseSchema

__all__ = [
    "Job",
    "JobPlan",
    "JobCreate",
    "Jobs",
]


class JobPlan(BaseSchema):
    type: Literal["plan"] = "plan"
    plan_id: UUID4


class JobSnapshot(BaseSchema):
    type: Literal["snapshot"] = "snapshot"
    integration_id: UUID4
    agent_id: UUID4 | None


class JobCreate(BaseSchema):
    user_id: UUID4
    pattern: str
    timezone: str | None = "Etc/UTC"
    next_run_date: datetime | None = None
    definition: JobPlan | JobSnapshot = Field(..., discriminator="type")


class Job(JobCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    org_id: UUID4
    claimed: bool
    suspended: bool = False
    created_date: datetime


class Jobs(BaseSchema):
    count: int
    items: List[Job]
