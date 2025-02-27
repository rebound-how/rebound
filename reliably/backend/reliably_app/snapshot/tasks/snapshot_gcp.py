import asyncio
import logging
from typing import Any

import msgspec
from google.oauth2._service_account_async import Credentials
from lueur.models import Discovery
from lueur.platform.gcp import explore, expand_links

from reliably_app.environment.schemas import Environment

__all__ = ["generate_snapshot", "expand_all_links"]
logger = logging.getLogger("reliably_app")
TRUTHY = ("1", "true", "True", "TRUE")


async def generate_snapshot(environment: Environment) -> list[Discovery] | None:
    credentials: Credentials | None = None

    envvars = environment.envvars
    if envvars.get("RELIABLY_GCP_USE_SYSTEM_CREDS") not in TRUTHY:
        project_id = envvars.get("GOOGLE_CLOUD_PROJECT_ID")
        if not project_id:
            logger.debug(
                f"Snapshot environment {environment.id} expects GCP project id"
            )
            return None

        region = envvars.get("GOOGLE_CLOUD_REGION")

        secrets = environment.secrets
        sa = secrets.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not sa:
            logger.debug(
                f"Snapshot environment {environment.id} expects GCP service "
                "account"
            )
            return None

        creds = msgspec.json.decode(sa)

        credentials = Credentials.from_service_account_info(
            creds,
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-platform.read-only",
                "https://www.googleapis.com/auth/monitoring.read",
                "https://www.googleapis.com/auth/logging.read",
                "https://www.googleapis.com/auth/ndev.clouddns.readonly",
            ],
        )

    tasks: list[asyncio.Task] = []

    async with asyncio.TaskGroup() as tg:
        tasks.append(tg.create_task(explore(project_id, creds=credentials)))

        if region:
            tasks.append(
                tg.create_task(explore(project_id, region, creds=credentials))
            )

    discos = []
    for task in tasks:
        discos.append(task.result())

    return discos


def expand_all_links(d: Discovery, serialized: dict[str, Any]) -> None:
    expand_links(d, serialized)
