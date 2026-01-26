import asyncio
import logging
import os
from configparser import ConfigParser
from functools import lru_cache
from pathlib import Path
from typing import Any, Tuple

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
    project_id: str | None = None
    region: str | None = None

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
    else:
        project_id, region = get_gcp_project_and_region()

    tasks: list[asyncio.Task] = []

    include = [
        "addresses",
        "gke",
        "cloudrun",
        "lb",
        "forwardingrules",
        "health_checks",
        "target_proxies",
        "dns",
        "vpc",
        "monitoring",
    ]

    async with asyncio.TaskGroup() as tg:
        if project_id:
            logger.debug(f"Using GCP project {project_id}")
            tasks.append(tg.create_task(explore(
                project_id, creds=credentials, include=include)))

        if region:
            logger.debug(f"Using GCP region {region}")
            tasks.append(
                tg.create_task(explore(
                    project_id, region, creds=credentials, include=include))
            )

    discos = []
    for task in tasks:
        discos.append(task.result())

    return discos


def expand_all_links(d: Discovery, serialized: dict[str, Any]) -> None:
    expand_links(d, serialized)



@lru_cache(maxsize=1)
def get_gcp_project_and_region() -> Tuple[str | None, str | None]:
    """
    Return (project_id, compute_region) from the active gcloud configuration.

    Values may be None if unset.
    """

    # 1. Locate gcloud config root
    config_root = Path(
        os.environ.get(
            "CLOUDSDK_CONFIG",
            Path.home() / ".config" / "gcloud",
        )
    )

    if not config_root.exists():
        return None, None

    # 2. Determine active configuration name
    active_config_path = config_root / "active_config"
    if active_config_path.exists():
        config_name = active_config_path.read_text().strip()
    else:
        config_name = "default"

    config_file = config_root / "configurations" / f"config_{config_name}"
    if not config_file.exists():
        return None, None

    # 3. Parse INI-style config
    parser = ConfigParser()
    parser.read(config_file)

    # --- Project ID ---
    project_id = None
    if parser.has_section("core"):
        project_id = parser.get("core", "project", fallback=None)

    # --- Region ---
    region = None
    if parser.has_section("compute"):
        region = parser.get("compute", "region", fallback=None)

        if not region:
            zone = parser.get("compute", "zone", fallback=None)
            if zone and "-" in zone:
                region = zone.rsplit("-", 1)[0]

    return project_id, region
