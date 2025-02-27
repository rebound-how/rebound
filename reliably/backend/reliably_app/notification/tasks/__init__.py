import asyncio
import logging
import time

from reliably_app import environment, integration
from reliably_app.database import SessionLocal
from reliably_app.notification.schemas import Event, PlanEvent
from reliably_app.notification.tasks.notification_email import (
    notify as notify_via_email,
)
from reliably_app.notification.tasks.notification_github import (
    notify as notify_via_github,
)
from reliably_app.notification.tasks.notification_webhook import (
    notify as notify_via_webhook,
)

__all__ = ["process_notifications", "notify_event"]

logger = logging.getLogger("reliably_app")
event_stream = asyncio.LifoQueue()  # type: ignore


async def process_notifications(event: asyncio.Event) -> None:
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                cancel_on_shutdown(event), name="notification-supervisor"
            )

            while not event.is_set():
                e = await event_stream.get()
                if e is None:
                    logger.debug("Terminating notifications processing")
                    return None

                t = tg.create_task(
                    notify_all(e), name=f"notification-all-{time.time()}"
                )
                t.add_done_callback(completed_task)
                event_stream.task_done()
    except ExceptionGroup as xg:
        for x in xg.exceptions:
            logger.error("Failed to process event notification", exc_info=x)


async def notify_event(event: Event) -> None:
    try:
        await event_stream.put(event)
    except Exception:
        logger.error(
            "Failed to process event, likely because the stream was closed",
            exc_info=True,
        )


###############################################################################
# Private functions
###############################################################################
async def cancel_on_shutdown(event: asyncio.Event) -> None:
    try:
        await event.wait()
    finally:
        await event_stream.put(None)


async def notify_all(event: PlanEvent) -> None:
    logger.debug(f"Notifying event from organization {event.org_id}")

    environments = await get_environments(event)

    tasks: list[asyncio.Task] = []

    try:
        async with asyncio.TaskGroup() as tg:
            for e in environments:
                e_id = str(e.id)

                if should_use_email(e):
                    t = tg.create_task(
                        notify_via_email(event, e),
                        name=f"notification-email-{e_id}",
                    )
                    t.add_done_callback(completed_task)
                    tasks.append(t)

                if should_use_webhook(e):
                    t = tg.create_task(
                        notify_via_webhook(event, e),
                        name=f"notification-webhook-{e_id}",
                    )
                    t.add_done_callback(completed_task)
                    tasks.append(t)

                if should_use_github(e):
                    t = tg.create_task(
                        notify_via_github(event, e),
                        name=f"notification-github-{e_id}",
                    )
                    t.add_done_callback(completed_task)
                    tasks.append(t)
    except ExceptionGroup as xg:
        for x in xg.exceptions:
            logger.error("Failed to notify on event", exc_info=x)


async def get_environments(
    event: PlanEvent,
) -> list[environment.schemas.Environment]:
    ids = []
    async with SessionLocal() as db:
        ints = await integration.crud.get_integrations_by_provider_and_vendor(
            db, event.org_id, "reliably", "notification"
        )

        ids.extend([str(i.environment_id) for i in ints])

        environments = (
            await environment.crud.get_environments_from_integrations(
                db, event.org_id, ids, "notification"
            )
        )

        return [
            environment.schemas.Environment.model_validate(
                e, from_attributes=True
            )
            for e in environments
        ]


def should_use_email(e: environment.schemas.Environment) -> bool:
    return e.envvars.is_truthy("RELIABLY_NOTIFICATION_USE_EMAIL")


def should_use_webhook(e: environment.schemas.Environment) -> bool:
    return e.envvars.is_truthy("RELIABLY_NOTIFICATION_USE_WEBHOOK")


def should_use_github(e: environment.schemas.Environment) -> bool:
    return e.envvars.is_truthy("RELIABLY_NOTIFICATION_USE_GITHUB")


def completed_task(task: asyncio.Task) -> None:
    task.remove_done_callback(completed_task)

    if task.cancelled():
        logger.info(f"Notification task '{task.get_name()}' was cancelled")
        return None

    x = task.exception()
    if x:
        logger.warning(
            f"Notification task '{task.get_name()}' raised an error: {x}"
        )
        logger.debug(
            f"Notification task '{task.get_name()}' failed", exc_info=x
        )
    elif task.done():
        try:
            r = task.result()
            logger.debug(
                f"Notification task '{task.get_name()}' completed normally: {r}"
            )
        except Exception:
            logger.warning(
                f"Notification task '{task.get_name()}' failed", exc_info=True
            )
