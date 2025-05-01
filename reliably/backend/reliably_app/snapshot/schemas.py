from datetime import datetime, timezone
from typing import Any, List

from lueur.models import Discovery, Resource, Meta, GCPMeta, AWSMeta, K8SMeta
from pydantic import UUID4, ConfigDict, RootModel

from reliably_app.schemas import BaseSchema
from reliably_app.environment.schemas import Environment

__all__ = [
    "SnapshotBase",
    "Snapshot",
    "SnapshotCreate",
    "Snapshots",
    "SnapshotConfig",
    "SnapshotTask",
    "LinkInfo",
    "ResourceCandidates",
]


def now() -> datetime:
    return datetime.now().astimezone(timezone.utc)


class SnapshotBase(BaseSchema):
    org_id: UUID4
    user_id: UUID4
    agent_id: UUID4 | None = None
    snapshot: Discovery


class Snapshot(SnapshotBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    created_date: datetime


class SnapshotCreate(BaseSchema):
    integration_id: UUID4
    pattern: str = "*/5 * * * *"
    agent_id: UUID4 | None = None


class Snapshots(BaseSchema):
    count: int
    items: List[Resource]


class SnapshotConfig(BaseSchema):
    name: str | None = None
    integration_id: UUID4 | None = None
    env: Environment


class SnapshotTask(BaseSchema):
    id: UUID4


class LinkInfo(BaseSchema):
    id: str
    meta: Meta | GCPMeta | AWSMeta | K8SMeta


class LinkInfos(BaseSchema):
    count: int
    items: List[LinkInfo]


class ResourceCandidate(BaseSchema):
    val: str
    label: str


class ResourceCandidates(BaseSchema):
    count: int
    items: List[ResourceCandidate]


ResourceValue = RootModel[List[Any]]
