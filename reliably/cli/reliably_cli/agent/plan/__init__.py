import anyio
import trio
from anyio.abc import TaskStatus
from anyio.streams.memory import (
    MemoryObjectReceiveStream,
    MemoryObjectSendStream,
)

from reliably_cli.client import agent_client
from reliably_cli.config import get_settings
from reliably_cli.config.types import Settings
from reliably_cli.log import console
from reliably_cli.types import Plan

from .providers.github import schedule_plan as gh_schedule_plan

__all__ = ["fetch_plans", "process_plans"]


async def process_plans(
    stream: MemoryObjectReceiveStream,
    task_status: TaskStatus = anyio.TASK_STATUS_IGNORED,
) -> None:
    console.print("Processing plans starting")
    async with anyio.create_task_group() as tg:
        task_status.started()
        async with stream:
            async for plan in stream:
                if plan.definition.environment.provider == "github":
                    tg.start_soon(gh_schedule_plan, plan)

    console.print("Processing plans terminated")


async def fetch_plans(stream: MemoryObjectSendStream) -> None:
    console.print("Fetching plans started")
    async with anyio.create_task_group() as tg:
        try:
            while True:
                event = anyio.Event()
                tg.start_soon(fetch_next_schedulable_plan, stream, event)
                await event.wait()

                settings = get_settings()
                if settings.plan.fetch_frequency <= 0:
                    break
                await trio.sleep(settings.plan.fetch_frequency)
        finally:
            console.print("Fetching plans terminated")
            # by closing the sending stream, this close the receiving stream
            # and terminate the processing of events automatically. neat.
            await stream.aclose()


###############################################################################
# Private
###############################################################################
def get_enabled_providers(settings: Settings) -> list[str]:
    enabled = []

    if settings.plan.providers.github.enabled:
        enabled.append("github")

    return enabled


async def fetch_next_schedulable_plan(
    stream: MemoryObjectSendStream, event: anyio.Event
) -> None:
    try:
        settings = get_settings()
        providers = get_enabled_providers(settings)

        for provider in providers:
            async with agent_client() as client:
                r = await client.get(
                    "/plans/schedulables/next",
                    params={"deployment_type": provider},
                )
                plan = r.json()
                if plan is None:
                    return

                plan = Plan.model_validate(plan)
                await stream.send(plan)
    finally:
        event.set()
