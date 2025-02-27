import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, Coroutine

from fastapi import FastAPI

from reliably_app.config import get_settings
from reliably_app.job.tasks import process_jobs
from reliably_app.notification.tasks import process_notifications
from reliably_app.organization.tasks import create_default_organizations

__all__ = [
    "run_background_tasks",
    "add_background_async_task",
    "add_background_task",
]
logger = logging.getLogger("reliably_app")
event = asyncio.Event()
tasks: set[asyncio.Task] = set()


@asynccontextmanager
async def run_background_tasks(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.debug("Starting background tasks")

    settings = get_settings()
    org_names = settings.DEFAULT_ORGANIZATIONS
    if not org_names:
        raise ValueError(
            "you must specify at least one organization in your settings "
            "using the DEFAULT_ORGANIZATIONS key"
        )

    add_background_async_task(
        create_default_organizations(org_names),
        name="Create & populate default organizations",
    )
    add_background_async_task(process_jobs(event), name="Job processor")
    add_background_async_task(
        process_notifications(event), name="Notification processor"
    )

    yield

    logger.debug("Terminating background tasks")
    event.set()

    try:
        await asyncio.gather(*tasks)
    except Exception:
        logger.warning(
            "One of the background tasks failed in a way that has "
            "the side effect that we couldn't cleanly stop the other "
            "tasks. That shouldn't be an issue as we are terminating.",
            exc_info=True,
        )
    finally:
        tasks.clear()


def add_background_async_task(
    coro: Coroutine, /, name: str | None = None
) -> None:
    task = asyncio.create_task(coro, name=name)
    task.add_done_callback(supervise_task)
    tasks.add(task)


def add_background_task(f: Callable, /, **kwargs) -> None:  # type: ignore
    coro = asyncio.to_thread(f, **kwargs)
    add_background_async_task(coro)


def supervise_task(task: asyncio.Task) -> None:
    # we cleanup here to prevent memory leaks
    task.remove_done_callback(supervise_task)
    try:
        tasks.remove(task)
    except KeyError:
        pass

    if task.cancelled():
        logger.error(f"Task {task.get_name()} was cancelled")
        return None

    x = task.exception()
    if x:
        logger.warning(f"Task '{task.get_name()}' raised an error: {x}")
        logger.debug(f"Task '{task.get_name()}' failed", exc_info=x)
    elif task.done():
        try:
            r = task.result()
            logger.debug(f"Task '{task.get_name()}' completed normally: {r}")
        except Exception:
            logger.warning(f"Task '{task.get_name()}' failed", exc_info=True)
