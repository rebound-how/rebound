import logging
from typing import List

from authlib.integrations.starlette_client import OAuth

from reliably_app.config import Settings
from reliably_app.login import tasks  # noqa
from reliably_app.login.providers.github import GitHub
from reliably_app.login.providers.google import Google
from reliably_app.login.providers.okta import Okta

__all__ = ["oauth", "register_oauth_providers", "has_provider"]

logger = logging.getLogger("reliably_app")
oauth = OAuth()
OAUTH_PROVIDERS: List[str] = []


def register_oauth_providers(settings: Settings) -> None:
    if settings.OAUTH_GITHUB_ENABLED:
        oauth.register(
            name="github",
            overwrite=True,
            client_id=settings.OAUTH_GITHUB_CLIENT_ID,
            client_secret=settings.OAUTH_GITHUB_CLIENT_SECRET.get_secret_value(),  # type: ignore  # noqa
            **GitHub.OAUTH_CONFIG,
        )
        OAUTH_PROVIDERS.append("github")

    if settings.OAUTH_GOOGLE_ENABLED:
        oauth.register(
            name="google",
            overwrite=True,
            client_id=settings.OAUTH_GOOGLE_CLIENT_ID,
            client_secret=settings.OAUTH_GOOGLE_CLIENT_SECRET.get_secret_value(),  # type: ignore  # noqa
            **Google.OAUTH_CONFIG,
        )
        OAUTH_PROVIDERS.append("google")

    if settings.OAUTH_OKTA_ENABLED:
        okta_base_url = settings.OAUTH_OKTA_BASE_URL
        oauth.register(
            name="okta",
            overwrite=True,
            client_id=settings.OAUTH_OKTA_CLIENT_ID,
            client_secret=settings.OAUTH_OKTA_CLIENT_SECRET.get_secret_value(),  # type: ignore  # noqa
            api_base_url=f"{okta_base_url}/oauth2/default",
            server_metadata_url=f"{okta_base_url}/oauth2/default/.well-known/oauth-authorization-server",  # noqa
            access_token_url=f"{okta_base_url}/oauth2/default/v1/token",
            authorize_url=f"{okta_base_url}/oauth2/default/v1/authorize",
            **Okta.OAUTH_CONFIG,
        )
        OAUTH_PROVIDERS.append("okta")


def has_provider(name: str) -> bool:
    return name in OAUTH_PROVIDERS
