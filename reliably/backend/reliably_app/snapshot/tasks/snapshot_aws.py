import asyncio
import logging
import os
from typing import Any

import boto3
from lueur.models import Discovery
from lueur.platform.aws import explore, expand_links

from reliably_app.environment.schemas import Environment

__all__ = ["generate_snapshot", "expand_all_links"]
logger = logging.getLogger("reliably_app")
TRUTHY = ("1", "true", "True", "TRUE")


async def generate_snapshot(environment: Environment) -> list[Discovery] | None:
    envvars = environment.envvars
    if envvars.get("RELIABLY_AWS_USE_SYSTEM_CREDS") not in TRUTHY:
        region = envvars.get("AWS_REGION")
        if not region:
            logger.debug(
                f"Snapshot environment {environment.id} expects AWS region"
            )
            return None

        secrets = environment.secrets
        key_id = secrets.get("AWS_ACCESS_KEY_ID")
        if not key_id:
            logger.debug(
                f"Snapshot environment {environment.id} expects AWS key id"
            )
            return None

        key = secrets.get("AWS_SECRET_ACCESS_KEY")
        if not key:
            logger.debug(
                f"Snapshot environment {environment.id} expects AWS access key"
            )
            return None
    else:
        region = detect_configured_region()
        logger.debug(f"Discovery will be made against AWS region {region}")

    loop = asyncio.get_running_loop()
    discos = await loop.run_in_executor(None, explore, region)

    return [discos]


def expand_all_links(d: Discovery, serialized: dict[str, Any]) -> None:
    expand_links(d, serialized)


###############################################################################
# Private function
###############################################################################
def detect_configured_region() -> str | None:
    checks = (
        os.getenv("AWS_REGION"),
        os.getenv("AWS_DEFAULT_REGION"),
        boto3.DEFAULT_SESSION.region_name if boto3.DEFAULT_SESSION else None,
        boto3.Session().region_name,
    )
    for region in checks:
        if region:
            return region

    return None
