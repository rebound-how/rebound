import asyncio
import os

import httpx


async def delete(client: httpx.AsyncClient, exp_id: str, exec_id: str) -> None:
    print(f"Deleting {exec_id}")
    r = await client.delete(f"/experiments/{exp_id}/executions/{exec_id}")
    print(f"Deleted {exec_id}: {r.status_code}")


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
            r = await client.get("/executions")
            if r.status_code > 399:
                print(r.status_code, r.json())
                return

            execs = r.json()
            if not execs["items"]:
                break

            tasks = []
            for exec in execs["items"]:
                tasks.append(delete(client, exec["experiment_id"], exec["id"]))

            await asyncio.gather(*tasks)
            return


if __name__ == '__main__':
    asyncio.run(run())
