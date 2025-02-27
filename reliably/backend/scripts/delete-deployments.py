import asyncio
import os

import httpx


async def delete(client: httpx.AsyncClient, dep_id: str) -> None:
    print(f"Deleting {dep_id}")
    r = await client.delete(f"/deployments/{dep_id}")
    print(f"Deleted {dep_id}: {r.status_code}")


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
            r = await client.get("/deployments")
            if r.status_code > 399:
                print(r.status_code, r.json())
                return

            deployments = r.json()
            if not deployments["items"]:
                break

            tasks = []
            for deployment in deployments["items"]:
                tasks.append(delete(client, deployment["id"]))

            await asyncio.gather(*tasks)
            return


if __name__ == '__main__':
    asyncio.run(run())
