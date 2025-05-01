from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Literal, cast

import orjson
from pydantic import UUID4, ConfigDict, RootModel, SecretStr, field_validator

from reliably_app.schemas import BaseSchema

__all__ = [
    "EnvironmentSecret",
    "EnvironmentSecrets",
    "Environment",
    "EnvironmentCreate",
    "Environments",
    "EnvironmentClear",
    "dump_environment_in_clear",
]

TRUTHY = ("1", "true", "True", "TRUE")


class EnvironmentVar(BaseSchema):
    var_name: str
    value: str


class EnvironmentVars(RootModel):
    root: List[EnvironmentVar]

    def __iter__(self) -> Iterator[EnvironmentVar]:  # type: ignore
        return iter(self.root)

    def __getitem__(self, item: int) -> EnvironmentVar:
        return self.root[item]

    def get(self, varname: str) -> str | None:
        for envvar in self:
            if envvar.var_name == varname:
                return envvar.value

        return None

    def is_truthy(self, varname: str) -> bool:
        for envvar in self:
            if envvar.var_name == varname:
                return envvar.value in TRUTHY

        return False


class EnvironmentSecret(BaseSchema):
    key: str
    var_name: str
    value: SecretStr


class EnvironmentSecretAsFile(BaseSchema):
    key: str
    value: SecretStr
    path: str

    @field_validator("path")
    @classmethod
    def path_is_compliant(cls, v: str, **kwargs) -> str:  # type: ignore
        if not v.startswith("/"):
            raise ValueError("secret path must start with a forward slash")
        return v

    @property
    def mount(self) -> str:
        return str(Path(self.path).parent)

    @property
    def file(self) -> str:
        return str(Path(self.path).name)


class EnvironmentSecrets(RootModel):
    root: List[EnvironmentSecretAsFile | EnvironmentSecret]

    def __iter__(self) -> Iterator[EnvironmentSecretAsFile | EnvironmentSecret]:  # type: ignore  # noqa
        return iter(self.root)

    def __getitem__(
        self, item: int
    ) -> EnvironmentSecretAsFile | EnvironmentSecret:  # noqa
        return self.root[item]

    def get(self, varname_or_path: str) -> str | None:
        for secretvar in self:
            if isinstance(secretvar, EnvironmentSecret):
                if secretvar.var_name == varname_or_path:
                    return secretvar.value.get_secret_value()
            elif isinstance(secretvar, EnvironmentSecretAsFile):
                if secretvar.path == varname_or_path:
                    return secretvar.value.get_secret_value()

        return None

    def is_truthy(self, varname_or_path: str) -> bool:
        for secretvar in self:
            if isinstance(secretvar, EnvironmentSecret):
                if secretvar.var_name == varname_or_path:
                    return secretvar.value.get_secret_value() in TRUTHY
            elif isinstance(secretvar, EnvironmentSecretAsFile):
                if secretvar.path == varname_or_path:
                    return secretvar.value.get_secret_value() in TRUTHY

        return False


class EnvironmentBase(BaseSchema):
    name: str
    envvars: EnvironmentVars
    secrets: EnvironmentSecrets
    used_for: (
        Literal["plan", "notification", "integration", "snapshot"] | None
    ) = "plan"


class Environment(EnvironmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    org_id: UUID4
    created_date: datetime


class EnvironmentClear(Environment):
    pass


class EnvironmentCreate(EnvironmentBase):
    pass


class Environments(BaseSchema):
    count: int
    items: List[Environment]


class SimpleEnvironment(BaseSchema):
    id: UUID4
    name: str


class SimpleEnvironments(RootModel):
    root: List[SimpleEnvironment]

    def __iter__(self) -> Iterator[SimpleEnvironment]:  # type: ignore
        return iter(self.root)

    def __getitem__(self, item: int) -> SimpleEnvironment:
        return self.root[item]


def dump_environment_in_clear(
    environment: Environment | EnvironmentCreate,
) -> Dict[str, Any]:
    dump = orjson.loads(environment.model_dump_json())

    for s in environment.secrets:
        sk = s.key
        for ds in dump["secrets"]:
            if ds["key"] == sk:
                v = s.value.get_secret_value()
                ds["value"] = v
                break

    return cast(dict[str, Any], dump)


PlanIds = RootModel[List[UUID4]]
