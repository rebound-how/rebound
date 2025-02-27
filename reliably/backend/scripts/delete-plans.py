import asyncio
import os

import httpx


async def delete(client: httpx.AsyncClient, plan_id: str) -> None:
    print(f"Deleting {plan_id}")
    r = await client.delete(f"/plans/{plan_id}")
    print(f"Deleted {plan_id}: {r.status_code}")


async def run():
    token = os.getenv("RELIABLY_TOKEN")
    org = os.getenv("RELIABLY_ORG")
    host = os.getenv("RELIABLY_HOST", "https://app.reliably.dev")

    async with httpx.AsyncClient(http2=True) as client:
        client.base_url = httpx.URL(f"{host}/api/v1/organization/{org}")
        client.headers = httpx.Headers(
            {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {token}",
            }
        )

        while True:
            r = await client.get("/plans")
            if r.status_code > 399:
                print(r.status_code, r.json())
                return

            plans = r.json()
            if not plans["items"]:
                break

            tasks = []
            for plan in plans["items"]:
                tasks.append(delete(client, plan["id"]))

            await asyncio.gather(*tasks)
            return


if __name__ == '__main__':
    asyncio.run(run())
