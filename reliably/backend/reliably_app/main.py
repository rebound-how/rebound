from pathlib import Path

import certifi  # noqa
from fastapi import FastAPI

from reliably_app.__version__ import __version__
from reliably_app.background import run_background_tasks
from reliably_app.config import get_settings, Settings
from reliably_app.database import create_db_engine
from reliably_app.log import configure_logging
from reliably_app.login import register_oauth_providers
from reliably_app.middlewares import configure_middlewares
from reliably_app.observability import instrument_app, setup_exporter
from reliably_app.routers import load_routers


__all__ = ["create_app", "init_app"]


def create_app(env_file: Path = Path(".env")) -> FastAPI:
    """
    Factory to create and initialize our application.

    It should then be handed over to an ASGI server.
    """
    settings = get_settings(env_file)
    configure_logging(settings)
    return init_app(settings)


def init_app(settings: Settings) -> FastAPI:
    engine = create_db_engine(settings)

    app = FastAPI(
        lifespan=run_background_tasks,
        redoc_url=None,
        docs_url=None,
        version=__version__,
        description="Orchestrate Your Resilience Strategy",
        servers=[
            {"url": "http://localhost:8090", "description": "Dev server"},
        ],
        license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
        contact={
            "name": "Sylvain Hellegouarch",
            "url": "https://rebound.how/support/#contact",
            "email": "sylvain@rebound.how",
        },
        openapi_tags=[{"name": "reliably"}],
    )
    app.db_engine = engine  # type: ignore

    load_routers(app, settings)
    configure_middlewares(app, settings)
    register_oauth_providers(settings)

    if settings.OTEL_ENABLED:  # pragma: no cover
        setup_exporter(settings)
        instrument_app(app)

    return app
