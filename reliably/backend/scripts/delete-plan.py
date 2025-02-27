import asyncio
import os

import httpx


async def run():
    token = os.getenv("RELIABLY_TOKEN")
    org = os.getenv("RELIABLY_ORG")
    host = os.getenv("RELIABLY_HOST", "https://app.reliably.dev")
    plan_id = os.getenv("RELIABLY_PLAN_ID")

    async with httpx.AsyncClient(http2=True) as client:
        client.base_url = httpx.URL(f"{host}/api/v1/organization/{org}")
        client.headers = httpx.Headers(
            {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {token}",
            }
        )

        r = await client.delete(f"/plans/{plan_id}")
        if r.status_code > 399:
            print(r.status_code, r.json())
            return


if __name__ == '__main__':
    asyncio.run(run())
