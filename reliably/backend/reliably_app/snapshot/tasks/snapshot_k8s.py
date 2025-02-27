import logging
from typing import Any

import msgspec
from lueur.models import Discovery
from lueur.platform.k8s import explore, expand_links

from reliably_app.environment.schemas import Environment

__all__ = ["generate_snapshot", "expand_all_links"]
logger = logging.getLogger("reliably_app")
TRUTHY = ("1", "true", "True", "TRUE")


async def generate_snapshot(environment: Environment) -> list[Discovery] | None:
    envvars = environment.envvars

    credentials: dict[str, Any] | None = None

    if envvars.get("RELIABLY_K8S_USE_SYSTEM_CREDS") not in TRUTHY:
        sa = envvars.get("RELIABLY_K8S_USE_SYSTEM_CREDS")
        if sa:
            credentials = msgspec.json.decode(sa)

    return [await explore(credentials=credentials)]


def expand_all_links(d: Discovery, serialized: dict[str, Any]) -> None:
    expand_links(d, serialized)
