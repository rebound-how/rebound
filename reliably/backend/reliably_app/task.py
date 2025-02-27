import hashlib
import logging
from typing import Tuple

import httpx

from reliably_app.observability import span

__all__ = ["get_gcp_token", "get_org_id_hash_prefix", "get_project_number"]

METADATA_BASE = "http://metadata.google.internal/computeMetadata/v1"
METADATA_TOKEN_URL = f"{METADATA_BASE}/instance/service-accounts/default/token"
METADATA_PROJECT_ID_URL = f"{METADATA_BASE}/project/project-id"
METADATA_PROJECT_NUM_URL = f"{METADATA_BASE}/project/numeric-project-id"
METADATA_SA_EMAIL_URL = (
    f"{METADATA_BASE}/instance/service-accounts/default/email"
)
logger = logging.getLogger("reliably_app")


async def get_gcp_token() -> Tuple[str | None, str | None]:
    token = project_id = None

    with span("cloud-get-gcp-metadata"):
        async with httpx.AsyncClient(http2=True) as client:
            with span("cloud-get-gcp-token"):
                r = await client.get(
                    METADATA_TOKEN_URL,
                    headers={
                        "Metadata-Flavor": "Google",
                    },
                )
                if r.status_code > 399:
                    logger.error(
                        "failed to load id token from service: "
                        f"{r.status_code} - {r.text}"
                    )
                    return (None, None)

                token = r.json()["access_token"]

            with span("cloud-get-gcp-project-id"):
                r = await client.get(
                    METADATA_PROJECT_ID_URL,
                    headers={
                        "Metadata-Flavor": "Google",
                    },
                )
                if r.status_code > 399:
                    logger.error(
                        "failed to load project id from service: "
                        f"{r.status_code} - {r.text}"
                    )
                    return (token, None)

                project_id = r.text

        return (token, project_id)


async def get_project_number() -> str | None:
    with span("cloud-get-gcp-project-number"):
        async with httpx.AsyncClient(http2=True) as client:
            r = await client.get(
                METADATA_PROJECT_NUM_URL,
                headers={
                    "Metadata-Flavor": "Google",
                },
            )
            if r.status_code > 399:
                logger.error(
                    "failed to load project number from service: "
                    f"{r.status_code} - {r.text}"
                )
                return None

            return r.text


def get_org_id_hash_prefix(org_id: str) -> str:
    return hashlib.blake2s(org_id.encode("utf-8"), digest_size=6).hexdigest()
