import os
from contextlib import asynccontextmanager, contextmanager

import httpx
from pydantic import SecretStr

from .config import get_settings

__all__ = ["agent_client", "api_client", "should_verify_tls_cert"]


@asynccontextmanager
async def agent_client() -> httpx.AsyncClient:
    settings = get_settings()
    host = settings.service.host
    org_id = settings.organization.id
    token = settings.agent.token

    headers = {"Authorization": f"Bearer {token.get_secret_value()}"}

    async with httpx.AsyncClient(
        http2=True,
        base_url=f"{host}/api/v1/organization/{org_id}",
        headers=headers,
        timeout=30.0,
        verify=should_verify_tls_cert(),
    ) as c:
        yield c


@contextmanager
def api_client(
    bare: bool = False, token: SecretStr | None = None
) -> httpx.Client:
    settings = get_settings()
    host = settings.service.host

    if not token:
        token = settings.service.token

    url = f"{host}/api/v1"
    if not bare:
        org_id = settings.organization.id
        url = f"{url}/organization/{org_id}"

    headers = {"Authorization": f"Bearer {token.get_secret_value()}"}

    with httpx.Client(
        http2=True,
        base_url=url,
        headers=headers,
        timeout=30.0,
        verify=should_verify_tls_cert(),
    ) as c:
        yield c


def should_verify_tls_cert() -> bool:
    return os.getenv("RELIABLY_VERIFY_TLS", "1") == "1"
