import asyncio
import os

import httpx


async def delete(client: httpx.AsyncClient, int_id: str) -> None:
    print(f"Deleting {int_id}")
    r = await client.delete(f"/integrations/{int_id}")
    print(f"Deleted {int_id}: {r.status_code}")


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
            r = await client.get("/integrations")
            if r.status_code > 399:
                print(r.status_code, r.json())
                return

            integrations = r.json()
            if not integrations["items"]:
                break

            tasks = []
            for integration in integrations["items"]:
                tasks.append(delete(client, integration["id"]))

            await asyncio.gather(*tasks)
            return


if __name__ == '__main__':
    asyncio.run(run())
