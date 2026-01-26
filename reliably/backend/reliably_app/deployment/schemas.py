import base64
import pathlib
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Literal, cast

import orjson
from pydantic import (
    UUID4,
    ConfigDict,
    Field,
    HttpUrl,
    RootModel,
    SecretStr,
    field_validator,
)
from ruamel.yaml import YAML

from reliably_app.config import get_settings
from reliably_app.crypto import decrypt, encrypt
from reliably_app.schemas import BaseSchema

__all__ = ["Deployment", "DeploymentCreate", "Deployments"]
ALLOWED_DOMAINS = ("github.com",)


def get_cloud_job_image() -> str:
    settings = get_settings()
    return settings.JOB_CONTAINER_IMAGE


class DeploymentNoopDefinition(BaseSchema):
    type: Literal["noop"] = "noop"


class DeploymentGitHubDefinition(BaseSchema):
    type: Literal["github"] = "github"
    repo: HttpUrl | None = None
    token: SecretStr | None = (
        None  # optional GH token when launched without agent
    )
    username: str | None = (
        None  # optional GH username when launched without agent
    )
    ref: str = "main"  # optional GH branch ref when launched without agent
    base_dir: str = "plans"

    @field_validator("repo")
    @classmethod
    def allowed_domains(cls, v: HttpUrl, **kwargs) -> HttpUrl:  # type: ignore
        if v.host not in ALLOWED_DOMAINS:
            raise ValueError("not a github.com URL")
        return v

    @property
    def clear_token(self) -> str | None:
        if not self.token:
            return None

        settings = get_settings()
        return decrypt(
            base64.b64decode(self.token.get_secret_value().encode("utf-8")),
            settings,
        )


class DeploymentReliablyCloudSecret(BaseSchema):
    env: str
    name: str
    version: str = "latest"


class DeploymentReliablyCloudDefinition(BaseSchema):
    type: Literal["reliably_cloud"] = "reliably_cloud"
    image: str = Field(default_factory=get_cloud_job_image)
    location: str = "europe-west1"


class DeploymentCLIDefinition(BaseSchema):
    type: Literal["reliably_cli"] = "reliably_cli"
    mode: Literal["managed", "manual"] = "manual"
    base_dir: pathlib.Path | None = None
    py_version: str | None = None
    py_dependencies: str | None = None


class DeploymentContainerVolume(BaseSchema):
    model_config = ConfigDict(
        json_encoders={
            pathlib.Path: lambda v: str(v.absolute()),
        }
    )

    bind: str
    mode: Literal["ro", "rw"] = "ro"


class DeploymentContainerDefinition(BaseSchema):
    type: Literal["container"] = "container"
    image: str
    working_dir: str = tempfile.gettempdir()
    volumes: Dict[pathlib.Path, DeploymentContainerVolume] | None = None

    @field_validator("volumes")
    @classmethod
    def volumes_must_exist(  # type: ignore
        cls, v: Dict[pathlib.Path, DeploymentContainerVolume] | None, **kwargs
    ) -> Dict[str, DeploymentContainerVolume] | None:
        if v is None:
            return None

        vols = {}
        for k, i in v.items():
            if not k.exists():
                raise ValueError(f"volume {k} does not exists on your host")
            vols[str(k.absolute())] = i
        return vols


class DeploymentKubernetesJobDefinition(BaseSchema):
    type: Literal["k8s_job"] = "k8s_job"
    use_default_manifest: bool = True
    image: str | None = None
    namespace: str
    manifest: str | None = None
    credentials: SecretStr | None = None
    use_in_cluster_credentials: bool = False

    @property
    def clear_credentials(self) -> str | None:
        if not self.credentials:
            return None

        settings = get_settings()
        return decrypt(
            base64.b64decode(
                self.credentials.get_secret_value().encode("utf-8")
            ),
            settings,
        )

    @property
    def parsed_manifest(self) -> Dict[str, Any] | None:
        if not self.manifest:
            return None

        yaml = YAML(typ="safe")
        return cast(dict[str, Any], yaml.load(self.manifest))


class DeploymentBase(BaseSchema):  # pragma: no cover
    name: str
    definition: (
        DeploymentGitHubDefinition
        | DeploymentReliablyCloudDefinition
        | DeploymentCLIDefinition
        | DeploymentContainerDefinition
        | DeploymentKubernetesJobDefinition
        | DeploymentNoopDefinition
    ) = Field(..., discriminator="type")  # noqa


class Deployment(DeploymentBase):
    id: UUID4
    org_id: UUID4
    created_date: datetime


class DeploymentCreate(DeploymentBase):
    pass


class Deployments(BaseSchema):
    count: int
    items: List[Deployment]


def dump_to_dict(dep: Deployment | DeploymentCreate) -> Dict[str, Any]:
    settings = get_settings()
    dump = orjson.loads(dep.model_dump_json())
    c: str | None = None

    match dep.definition.type:
        case "k8s_job":
            if dep.definition.credentials:
                c = dep.definition.credentials.get_secret_value()
                dump["definition"]["credentials"] = base64.b64encode(
                    encrypt(c, settings)  # type: ignore
                ).decode("utf-8")
            else:
                dump["definition"]["credentials"] = None
        case "github":
            if dep.definition.token:
                c = dep.definition.token.get_secret_value()
                dump["definition"]["token"] = base64.b64encode(
                    encrypt(c, settings)  # type: ignore
                ).decode("utf-8")
            else:
                dump["definition"]["token"] = None

    return cast(dict[str, Any], dump)


DeploymentIds = RootModel[list[UUID4]]
