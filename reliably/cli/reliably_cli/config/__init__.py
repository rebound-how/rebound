import functools

import typer

from ..log import err_console
from .types import Settings

__all__ = ["get_settings", "ensure_config_is_set"]


@functools.lru_cache
def get_settings() -> Settings:
    return Settings()


def ensure_config_is_set(token_only: bool = False) -> None:
    settings = get_settings()

    if settings.service.token is None:
        err_console.print(
            "Please set the service token in the configuration or as "
            "RELIABLY_SERVICE_TOKEN.\n"
            "You can get or create a token on your profile page here: "
            "https://app.reliably.dev/settings/tokens/",
        )
        raise typer.Exit(code=1)

    elif not token_only and (
        settings.organization is None or settings.organization.id is None
    ):
        err_console.print(
            "Please set the organization id in the configuration or as "
            "RELIABLY_ORGANIZATION_ID.\n"
            "You can find this identifier on your profile page here: "
            "https://app.reliably.dev/settings/profile/",
        )
        raise typer.Exit(code=1)
