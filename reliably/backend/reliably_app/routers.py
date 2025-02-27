import importlib.resources
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from reliably_app.account.service import (
    extend_routers as extend_account_routers,
)
from reliably_app.agent.service import extend_routers as extend_agent_routers
from reliably_app.assistant.service import (
    extend_routers as extend_assistant_routers,
)
from reliably_app.catalog.service import (
    extend_routers as extend_catalog_routers,
)
from reliably_app.config import Settings
from reliably_app.dependencies.auth import (
    validate_auth,
    with_admin_user,
    with_user_in_org,
)
from reliably_app.deployment.service import (
    extend_routers as extend_deployment_routers,
)
from reliably_app.environment.service import (
    extend_routers as extend_environment_routers,
)
from reliably_app.execution.service import (
    extend_routers as extend_execution_routers,
)
from reliably_app.experiment.service import (
    extend_routers as extend_experiment_routers,
)
from reliably_app.health.service import extend_routers as extend_health_routers
from reliably_app.integration.service import (
    extend_routers as extend_integration_routers,
)
from reliably_app.login.service import router as login_router
from reliably_app.me.service import extend_routers as extend_me_routers
from reliably_app.organization.service import (
    extend_routers as extend_organization_routers,
    top_level_router,
)
from reliably_app.plan.service import extend_routers as extend_plan_routers
from reliably_app.series.service import extend_routers as extend_series_routers
from reliably_app.snapshot.service import (
    extend_routers as extend_snapshot_routers,
)
from reliably_app.token.service import extend_routers as extend_token_routers

__all__ = ["load_routers"]
logger = logging.getLogger("reliably_app")


def load_routers(app: FastAPI, settings: Settings) -> None:
    api_router = APIRouter(
        prefix="/api/v1", dependencies=[Depends(validate_auth)]
    )

    admin_api_router = APIRouter(
        prefix="", dependencies=[Depends(with_admin_user)]
    )

    needs_org_router = APIRouter(
        prefix="/organization/{org_id}",
        dependencies=[Depends(with_user_in_org)],
    )

    web_router = APIRouter(prefix="/api")

    needs_org_webrouter = APIRouter(
        prefix="/organization/{org_id}",
        dependencies=[Depends(with_user_in_org)],
    )

    extend_account_routers(web_router, api_router)
    extend_me_routers(web_router)
    extend_health_routers(app)

    extend_agent_routers(needs_org_webrouter, needs_org_router)
    extend_assistant_routers(needs_org_webrouter, needs_org_router)
    extend_catalog_routers(needs_org_webrouter, needs_org_router)
    extend_deployment_routers(needs_org_webrouter, needs_org_router)
    extend_environment_routers(needs_org_webrouter, needs_org_router)
    extend_execution_routers(needs_org_webrouter, needs_org_router)
    extend_experiment_routers(needs_org_webrouter, needs_org_router)
    extend_integration_routers(needs_org_webrouter, needs_org_router)
    extend_organization_routers(needs_org_webrouter, needs_org_router)
    extend_plan_routers(needs_org_webrouter, needs_org_router)
    extend_series_routers(needs_org_webrouter, needs_org_router)
    extend_snapshot_routers(needs_org_webrouter, needs_org_router)
    extend_token_routers(needs_org_webrouter, needs_org_router)

    api_router.include_router(admin_api_router)
    api_router.include_router(needs_org_router)
    api_router.include_router(top_level_router, prefix="/organization")
    web_router.include_router(needs_org_webrouter)
    app.include_router(api_router)
    app.include_router(login_router)
    app.include_router(web_router)
    app.include_router(APIRouter(prefix="/webhooks"))

    configure_static_routes(app, settings)


def configure_static_routes(app: FastAPI, settings: Settings) -> None:
    if settings.FRONTEND_DIR:
        static_dir = settings.FRONTEND_DIR
    else:
        with importlib.resources.path("reliably_app", "www") as p:
            static_dir = p.absolute()

    p = Path(static_dir)
    if not p.is_dir():
        raise ValueError(
            f"Cannot serve frontend from {static_dir}, it's not a directory"
        )

    logger.debug(f"Serving frontend from directory {static_dir}")

    app.mount("/", StaticFiles(directory=static_dir, html=True), name="www")
