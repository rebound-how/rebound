from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from reliably_app.config import Settings

__all__ = ["register_middlewares"]


def register_middlewares(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SESSION_SECRET_KEY.get_secret_value(),
    )
