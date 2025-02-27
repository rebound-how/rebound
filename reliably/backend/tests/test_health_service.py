import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health(
    client: AsyncClient,
    authed: None,
) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
