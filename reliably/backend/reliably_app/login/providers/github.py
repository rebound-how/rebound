from typing import Dict

from authlib.oidc.core import UserInfo

from reliably_app.login.providers.base import OAuthBackend

__all__ = ["GitHub", "map_userinfo"]


class GitHub(OAuthBackend):  # pragma: no cover
    OAUTH_TYPE = "2.0"  # type: ignore
    OAUTH_NAME = "github"  # type: ignore
    OAUTH_CONFIG = {  # type: ignore
        "api_base_url": "https://api.github.com/",
        "access_token_url": "https://github.com/login/oauth/access_token",
        "authorize_url": "https://github.com/login/oauth/authorize",
        "userinfo_endpoint": "https://api.github.com/user",
        "client_kwargs": {"scope": "user:email"},
    }


def map_userinfo(data: Dict[str, str]) -> UserInfo:
    params = {
        "sub": str(data["id"]),
        "name": data["name"],
        "email": data.get("email"),
        "preferred_username": data["login"],
        "profile": data["html_url"],
        "picture": data["avatar_url"],
        "website": data.get("blog"),
        "given_name": None,
        "family_name": None,
    }

    return UserInfo(params)
