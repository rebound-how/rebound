import Secweb
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from reliably_app.auth.middlewares import (
    register_middlewares as auth_register_middlewares,
)
from reliably_app.config import Settings

__all__ = ["configure_middlewares"]


def configure_middlewares(app: FastAPI, settings: Settings) -> None:
    auth_register_middlewares(app, settings)
    app.add_middleware(GZipMiddleware)
    configure_sec(app, settings)


def configure_sec(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        Secweb.CacheControl.CacheControlMiddleware.CacheControl,
        Option={
            "s-maxage": 3600,
            "must-revalidate": True,
            "no-transform": True,
        },
    )
    app.add_middleware(Secweb.XContentTypeOptions.XContentTypeOptions)
    app.add_middleware(Secweb.StrictTransportSecurity.HSTS)
    app.add_middleware(Secweb.OriginAgentCluster.OriginAgentCluster)
    app.add_middleware(
        Secweb.XFrameOptions.XFrame,
        Option="SAMEORIGIN",
    )
    app.add_middleware(Secweb.xXSSProtection.xXSSProtection)
    app.add_middleware(
        Secweb.ReferrerPolicy.ReferrerPolicy,
        Option=["no-referrer-when-downgrade"],
    )
    app.add_middleware(
        Secweb.ContentSecurityPolicy.ContentSecurityPolicyMiddleware.ContentSecurityPolicy,  # noqa
        Option={
            "default-src": ["'self'"],
            "script-src": [
                "'self'",
                "'unsafe-inline'",
                "'unsafe-eval'",
                "'wasm-unsafe-eval'",
                "data:",
            ],
            "img-src": [
                "'self'",
                "https://avatars.githubusercontent.com",
                "https://lh3.googleusercontent.com",
                "data:",
            ],
            "style-src": ["'self'", "'unsafe-inline'"],
            "connect-src": ["'self'"],
        },
        script_nonce=False,
        style_nonce=False,
    )
