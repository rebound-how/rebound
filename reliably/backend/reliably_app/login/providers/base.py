from authlib.integrations.base_client.async_app import AsyncOAuth2Mixin

__all__ = ["OAuthBackend"]


class OAuthBackend(AsyncOAuth2Mixin):
    """Backend for OAuth Registry"""

    OAUTH_TYPE = None
    OAUTH_NAME = None
    OAUTH_CONFIG = None
