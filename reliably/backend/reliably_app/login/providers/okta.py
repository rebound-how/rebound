from typing import Dict

from authlib.oidc.core import UserInfo

from reliably_app.login.providers.base import OAuthBackend

__all__ = ["Okta", "map_userinfo"]


class Okta(OAuthBackend):  # pragma: no cover
    OAUTH_NAME = "okta"  # type: ignore
    OAUTH_CONFIG = {  # type: ignore
        "client_kwargs": {"scope": "openid profile email"},
    }


def map_userinfo(data: Dict[str, str]) -> UserInfo:
    params = {
        "sub": data["sub"],
        "name": data["name"],
        "email": data.get("email"),
        "preferred_username": data["preferred_username"],
        "profile": data.get("profile"),
        "picture": data.get("picture", ""),
        "website": "",
        "given_name": data.get("given_name"),
        "family_name": data.get("family_name"),
    }

    return UserInfo(params)
