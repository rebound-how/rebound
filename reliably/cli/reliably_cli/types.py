from datetime import datetime
from enum import Enum
from typing import Any, Dict, Iterator, List, Literal

from pydantic import UUID4, BaseModel, RootModel, SecretStr

__all__ = ["Plan", "FormatOption", "Organization", "Environment"]


class FormatOption(Enum):
    json = "json"
    yaml = "yaml"


class BaseSchema(BaseModel):
    pass


class PlanReliablyEnvironment(BaseSchema):
    provider: Literal["reliably_cloud"] = "reliably_cloud"
    id: UUID4


class PlanGitHubEnvironment(BaseSchema):
    provider: Literal["github"] = "github"
    name: str
    id: UUID4 | None = None


class PlanGCPEnvironment(BaseSchema):
    provider: Literal["gcp"] = "gcp"


class PlanDeployment(BaseSchema):
    deployment_id: UUID4


class PlanScheduleNow(BaseSchema):
    type: Literal["now"] = "now"


class PlanScheduleCron(BaseSchema):
    type: Literal["cron"] = "cron"
    pattern: str


class PlanBase(BaseSchema):  # pragma: no cover
    environment: (
        PlanGitHubEnvironment
        | PlanReliablyEnvironment
        | PlanGCPEnvironment
        | None
    ) = None
    deployment: PlanDeployment
    schedule: PlanScheduleNow | PlanScheduleCron
    experiments: List[UUID4]
    integrations: List[UUID4]


class Plan(BaseSchema):
    id: UUID4
    created_date: datetime
    definition: PlanBase
    ref: str
    status: str
    error: str | None = None


class IntegrationControlPythonProvider(BaseSchema):
    type: Literal["python"] = "python"
    module: str
    secrets: List[str] | None = None
    arguments: Dict[str, Any] | None = None


class IntegrationControl(BaseSchema):
    name: str
    provider: IntegrationControlPythonProvider


class Organization(BaseSchema):
    id: UUID4
    name: str
    created_date: datetime


class Organizations(BaseSchema):
    count: int
    items: list[Organization]


class EnvironmentVar(BaseSchema):
    var_name: str
    value: str


class EnvironmentVars(RootModel):
    root: List[EnvironmentVar]

    def __iter__(self) -> Iterator[EnvironmentVar]:
        return iter(self.root)

    def __getitem__(self, item) -> EnvironmentVar:
        return self.root[item]


class EnvironmentSecret(BaseSchema):
    key: str
    var_name: str
    value: SecretStr


class EnvironmentSecretAsFile(BaseSchema):
    key: str
    value: SecretStr
    path: str


class EnvironmentSecrets(RootModel):
    root: List[EnvironmentSecretAsFile | EnvironmentSecret]

    def __iter__(self) -> Iterator[EnvironmentSecretAsFile | EnvironmentSecret]:
        return iter(self.root)

    def __getitem__(self, item) -> EnvironmentSecretAsFile | EnvironmentSecret:
        return self.root[item]


class Environment(BaseSchema):
    id: UUID4
    org_id: UUID4
    created_date: datetime
    name: str
    envvars: EnvironmentVars
    secrets: EnvironmentSecrets
