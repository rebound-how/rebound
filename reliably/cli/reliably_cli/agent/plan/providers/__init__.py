from typing import Any

from reliably_cli.client import agent_client
from reliably_cli.config.types import Settings
from reliably_cli.log import console
from reliably_cli.types import Plan

__all__ = ["fetch_deployment", "fetch_experiment"]


async def fetch_deployment(
    plan: Plan, settings: Settings
) -> dict[str, Any] | None:
    dep_id = plan.definition.deployment.deployment_id

    async with agent_client() as client:
        r = await client.get(f"/deployments/{dep_id}")
        if r.status_code > 399:
            console.print(
                f"error fetching deployment {dep_id} for plan {plan.id}"
            )
            return

        return r.json()


async def fetch_experiment(
    plan: Plan, settings: Settings
) -> dict[str, Any] | None:
    exp_id = plan.definition.experiments[0]

    async with agent_client() as client:
        r = await client.get(f"/experiments/{exp_id}")
        if r.status_code > 399:
            console.print(
                f"error fetching experiment {exp_id} for plan {plan.id}"
            )
            return

        return r.json()


async def set_plan_status(
    plan_id: str, status: str, error: str | None = None
) -> None:
    async with agent_client() as client:
        await client.put(
            f"/plans/{plan_id}/status", json={"status": status, "error": error}
        )
