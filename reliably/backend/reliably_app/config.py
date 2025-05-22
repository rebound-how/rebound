import logging
from base64 import urlsafe_b64decode
from pathlib import Path
from typing import Annotated, Any, List, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    HttpUrl,
    PostgresDsn,
    SecretStr,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["get_settings", "Settings"]
logger = logging.getLogger("reliably_app")


def string2list(value: Any) -> Any:
    if not isinstance(value, list):
        return [value]
    else:
        return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(revalidate_instances="always")

    # Log settings
    LOG_LEVEL: Literal["INFO", "DEBUG", "ERROR", "WARNING"] = "INFO"
    LOG_FORMAT: Literal["plain", "json"] = "plain"
    ACCESS_LOG_LOG_LEVEL: Literal["INFO", "DEBUG", "ERROR", "WARNING"] = "INFO"
    ACCESS_LOG_LOG_FORMAT: Literal["plain", "json"] = "plain"
    ACCESS_LOG_FILE: Path | None = None
    APPLICATION_LOG_FILE: Path | None = None
    APPLICATION_LOG_FILE_LEVEL: Literal["INFO", "DEBUG", "ERROR", "WARNING"] = (
        "DEBUG"
    )
    ACCESS_LOG_STDOUT: bool = True
    APPLICATION_LOG_STDOUT: bool = True

    RELIABLY_DOMAIN: str

    # Frontend
    FRONTEND_DIR: Path | None = None

    # Database settings
    DATABASE_MODE: Literal["managed", "extern"] = "extern"
    DATABASE_URL: PostgresDsn | str
    DATABASE_WITH_SSL: bool = False
    DATABASE_SSL_CLIENT_CERT_FILE: str | None = None
    DATABASE_SSL_CLIENT_KEY_FILE: str | None = None
    DATABASE_SSL_SERVER_CA_FILE: str | None = None
    DATABASE_HOSTADDR: str | None = None

    # Configs of our observability stack
    OTEL_ENABLED: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: AnyUrl | None = None
    OTEL_EXPORTER_OTLP_HEADERS: str | None = None
    OTEL_GCP_EXPORTER: bool = False
    OTEL_SERVICE_NAME: str = "reliably"

    # org names to create and auto join
    DEFAULT_ORGANIZATIONS: Annotated[
        List[str], BeforeValidator(string2list)
    ] = []

    DEPLOYMENT_STRATEGY: Literal["gcp", "local", "k8s"] = "local"
    ENVIRONMENT_STORE_STRATEGY: Literal["gcp", "local", "aws"] = "local"

    # Crypto
    CRYPTO_PROVIDER: Literal["gcloud-kms", "cryptography", "none"]
    CRYPTO_GCLOUD_KMS_KEY_NAME: str | None = None
    CRYPTO_CRYPTOGRAPHY_SECRET_KEY: SecretStr | None = None

    CLI_RELIABLY_SERVICE_HOST: str | None = None
    CLI_RELIABLY_HOST: str | None = None
    CLI_RELIABLY_VERIFY_TLS: bool | None = None

    SESSION_SECRET_KEY: SecretStr = SecretStr(secret_value="secret")  # nosec

    # OAuth
    OAUTH_GITHUB_ENABLED: bool = False
    OAUTH_GITHUB_CLIENT_ID: str | None = None
    OAUTH_GITHUB_CLIENT_SECRET: SecretStr | None = None

    OAUTH_GOOGLE_ENABLED: bool = False
    OAUTH_GOOGLE_CLIENT_ID: str | None = None
    OAUTH_GOOGLE_CLIENT_SECRET: SecretStr | None = None

    OAUTH_OKTA_ENABLED: bool = False
    OAUTH_OKTA_CLIENT_ID: str | None = None
    OAUTH_OKTA_CLIENT_SECRET: SecretStr | None = None
    OAUTH_OKTA_BASE_URL: HttpUrl | None = None

    # GCP settings
    CLOUDRUN_JOB_SA: str | None = None
    PLAN_SCHEDULER_SA: str | None = None
    GCP_LOCATION: str = "europe-west1"
    GCP_PROJECT_ID: str | None = None
    JOB_CONTAINER_IMAGE: str = "ghcr.io/rebound-how/reliably-job:latest"

    # Kubernetes settings
    K8S_SERVICE_ACCOUNT_DIR: Path | None = Path("/home/svc/.config/rebound/sa")
    K8S_DEFAULT_JOB_NS: str = "reliably"
    K8S_DEFAULT_JOB_IMAGE: str = "ghcr.io/rebound-how/reliably-job:latest"

    # feat flags
    FEATURE_LOGIN_EMAIL: bool = False
    FEATURE_CONTAINER_DEPLOYMENT: bool = False
    FEATURE_CLOUD_DEPLOYMENT: bool = True
    FEATURE_K8S_JOB_DEPLOYMENT: bool = False
    FEATURE_NOTIFICATION_VIA_EMAIL: bool = False
    FEATURE_NOTIFICATION_VIA_WEBHOOK: bool = True
    FEATURE_NOTIFICATION_VIA_GITHUB: bool = True
    FEATURE_POPULATE_NEW_ORG_WITH_DEFAULTS: bool = True

    # assistant
    ASSISTANT_SCENARIO_ENABLED: bool = False
    OPENAI_API_KEY: str | None = None
    ASSISTANT_SCENARIO_MODEL: str = "gpt-4.1"
    ASSISTANT_MAX_TOKENS: int = 16384
    ASSISTANT_LIBRARY_FILE: Path | None = None

    # smtp
    SMTP_ADDR: str | None = None
    SMTP_PORT: int | None = None
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str | None = None

    # Additional sensitive settings secret provider
    SENSITIVE_SETTINGS_PROVIDER: (
        Literal["kubernetes", "docker-compose"] | None
    ) = None
    SENSITIVE_SETTINGS_KUBERNETES_SECRET_NAME: str | None = None
    SENSITIVE_SETTINGS_KUBERNETES_SECRET_NS: str = "default"
    SENSITIVE_SETTINGS_DOCKER_COMPOSE_SECRETS_FILENAME: Path | None = None


class KubernetesSecretSettings(BaseSettings):
    DATABASE_URL: PostgresDsn
    CRYPTO_CRYPTOGRAPHY_SECRET_KEY: SecretStr
    SESSION_SECRET_KEY: SecretStr
    OPENAI_API_KEY: str | None = None


class DockerComposeSecretSettings(BaseSettings):
    DATABASE_URL: PostgresDsn | None = None
    CRYPTO_CRYPTOGRAPHY_SECRET_KEY: SecretStr
    SESSION_SECRET_KEY: SecretStr
    OPENAI_API_KEY: str | None = None


_current: Settings | None = None


def get_settings(
    env_file_path: Path = Path(".env"),
) -> Settings:  # pragma: no cover
    """
    Read settings from the default `.env` file or from the process
    environment variables.

    Only load it once, no matter the provided file path on subsequent calls.
    """
    global _current

    if not _current:
        _current = Settings(_env_file=env_file_path)
        if _current.SENSITIVE_SETTINGS_PROVIDER is not None:
            _current = load_additional_sensitive_settings(_current)

    return _current


def load_additional_sensitive_settings(settings: Settings) -> Settings:
    provider = settings.SENSITIVE_SETTINGS_PROVIDER

    if provider == "kubernetes":
        from kubernetes import client, config

        secret_name = settings.SENSITIVE_SETTINGS_KUBERNETES_SECRET_NAME
        ns = settings.SENSITIVE_SETTINGS_KUBERNETES_SECRET_NS
        token_filename = settings.K8S_SERVICE_ACCOUNT_DIR / Path("token")  # type: ignore
        cert_filename = settings.K8S_SERVICE_ACCOUNT_DIR / Path("ca.crt")  # type: ignore

        logger.debug(
            f"Loading extra settings from Kubernetes secret {ns}/{secret_name}"
        )

        config.incluster_config.InClusterConfigLoader(
            token_filename=token_filename,
            cert_filename=cert_filename,
            try_refresh_token=True,
        ).load_and_set()

        v1 = client.CoreV1Api()
        secret = v1.read_namespaced_secret(secret_name, namespace=ns)

        data = {}
        for k, v in secret.data.items():
            v = v.strip()
            if v:
                data[k] = urlsafe_b64decode(v).decode("utf-8")

        k = KubernetesSecretSettings.model_validate(data)
        settings.DATABASE_URL = k.DATABASE_URL
        settings.CRYPTO_CRYPTOGRAPHY_SECRET_KEY = (
            k.CRYPTO_CRYPTOGRAPHY_SECRET_KEY
        )
        settings.SESSION_SECRET_KEY = k.SESSION_SECRET_KEY
        settings.OPENAI_API_KEY = k.OPENAI_API_KEY

        return settings

    elif provider == "docker-compose":
        p = settings.SENSITIVE_SETTINGS_DOCKER_COMPOSE_SECRETS_FILENAME
        if not p or not p.exists():
            logger.debug("No extra secrets provided")
            return settings

        dc = DockerComposeSecretSettings(_env_file=p)
        if dc.DATABASE_URL:
            settings.DATABASE_URL = dc.DATABASE_URL

        settings.CRYPTO_CRYPTOGRAPHY_SECRET_KEY = (
            dc.CRYPTO_CRYPTOGRAPHY_SECRET_KEY
        )
        settings.SESSION_SECRET_KEY = dc.SESSION_SECRET_KEY
        settings.OPENAI_API_KEY = dc.OPENAI_API_KEY

        return settings

    return settings
