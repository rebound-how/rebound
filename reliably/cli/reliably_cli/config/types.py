import os
from pathlib import Path
from typing import Any, Dict, Literal, Tuple, Type

import typer
from pydantic import UUID4, BaseModel, HttpUrl, SecretStr
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    InitSettingsSource,
    PydanticBaseSettingsSource,
    SecretsSettingsSource,
    SettingsConfigDict,
)

try:
    import tomllib  # noqa
except ImportError:
    import tomli as tomllib


__all__ = ["Settings", "get_settings_directory_path"]


class PlanProviderGitHubSection(BaseModel):
    enabled: bool = False
    token: SecretStr | None = None
    api_url: HttpUrl = "https://api.github.com"
    repo: str | None = None
    workflow_id: str = "plan.yaml"
    ref: str = "main"


class PlanProvidersSection(BaseModel):
    github: PlanProviderGitHubSection | None = None


class PlanSection(BaseModel):
    fetch_frequency: float = 0
    providers: PlanProvidersSection | None = None


class OrgSection(BaseModel):
    id: UUID4 | None = None


class AgentSection(BaseModel):
    token: SecretStr | None = None


class ServiceSection(BaseModel):
    host: str = "https://app.reliably.com"
    token: SecretStr | None = None


class LogSection(BaseModel):
    level: Literal["debug", "info", "error", "warn", "notset"] = "info"
    as_json: bool = False


class TOMLConfigSettingsSource(PydanticBaseSettingsSource):
    def __init__(
        self,
        settings_cls: type[BaseSettings],
    ) -> None:
        super().__init__(settings_cls)
        self.env_vars = self._load_toml()

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        field_value = self.env_vars.get(field_name)
        return field_value, field_name, False

    def prepare_field_value(
        self,
        field_name: str,
        field: FieldInfo,
        value: Any,
        value_is_complex: bool,
    ) -> Any:
        return value

    def __call__(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                d[field_key] = field_value

        return d

    def _load_toml(self) -> Dict[str, Any]:
        toml_file = os.getenv("RELIABLY_CLI_CONFIG")
        if not toml_file:
            toml_file = self.config.get("toml_file")

        if not Path(toml_file).exists():
            return {}

        encoding = self.config.get("env_file_encoding")
        return tomllib.loads(Path(toml_file).read_text(encoding=encoding))


class Settings(BaseSettings):
    service: ServiceSection | None = ServiceSection()
    organization: OrgSection | None = None
    agent: AgentSection | None = None
    plan: PlanSection | None = None
    log: LogSection = LogSection(level="info", as_json=False)

    model_config = SettingsConfigDict(
        env_prefix="reliably_",
        env_nested_delimiter="_",
        env_file_encoding="utf-8",
        toml_file=Path(typer.get_app_dir("reliably")) / "config.toml",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: InitSettingsSource,
        env_settings: EnvSettingsSource,
        dotenv_settings: DotEnvSettingsSource,
        file_secret_settings: SecretsSettingsSource,
    ) -> Tuple[
        InitSettingsSource,
        EnvSettingsSource,
        DotEnvSettingsSource,
        TOMLConfigSettingsSource,
        SecretsSettingsSource,
    ]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            TOMLConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


def get_settings_directory_path() -> Path:
    cfg_path = os.getenv("RELIABLY_CLI_CONFIG")
    if not cfg_path:
        cfg_path = Settings.config.get("toml_file")

    p = Path(cfg_path).parent
    if not p.exists() and not p.is_dir():
        p.mkdir()

    return p.absolute()
