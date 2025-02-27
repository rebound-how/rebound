from typing import Dict

from authlib.oidc.core import UserInfo

from reliably_app.login.providers.base import OAuthBackend

__all__ = ["Google", "map_userinfo"]


class Google(OAuthBackend):  # pragma: no cover
    OAUTH_NAME = "google"  # type: ignore
    OAUTH_CONFIG = {  # type: ignore
        "api_base_url": "https://www.googleapis.com/",
        "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",  # noqa
        "client_kwargs": {"scope": "openid email profile"},
    }


def map_userinfo(data: Dict[str, str]) -> UserInfo:
    params = {
        "sub": data["sub"],
        "name": data["name"],
        "email": data.get("email"),
        "preferred_username": data["given_name"],
        "profile": data.get("profile"),
        "picture": data.get("picture"),
        "website": "",
        "given_name": data.get("given_name"),
        "family_name": data.get("family_name"),
    }

    return UserInfo(params)
