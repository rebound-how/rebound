import logging

import httpx

from reliably_app import environment, notification

__all__ = ["notify"]

logger = logging.getLogger("reliably_app")


async def notify(
    ev: notification.schemas.PlanEvent, e: environment.schemas.Environment
) -> None:
    url = e.envvars.get("RELIABLY_NOTIFICATION_WEBHOOK_URL")
    if not url:
        logger.warning(
            "WebHook notification is enabled in the configuration but no URL "
            "was given in the integration. Ignoring event."
        )
        return None

    bearer = e.envvars.get("RELIABLY_NOTIFICATION_WEBHOOK_BEARER_TOKEN")

    notification = build_webhook_notification(ev)

    await send_notification(url, notification, e, bearer)


###############################################################################
# Private functions
###############################################################################
def build_webhook_notification(
    event: notification.schemas.PlanEvent,
) -> notification.schemas.WebHookNotification:
    x = None

    if event.execution_id:
        x = notification.schemas.WebHookExecution(
            execution_id=event.execution_id,
            verified=not event.deviated,
            status=event.status,
        )

    return notification.schemas.WebHookNotification(
        meta=notification.schemas.WebHookMeta(
            org_id=event.org_id, event=event.kind, triggered=event.start_date
        ),
        plan=event.plan,
        experiment=event.experiment,
        execution=x,
    )


async def send_notification(
    url: str,
    n: notification.schemas.WebHookNotification,
    e: environment.schemas.Environment,
    token: str | None = None,
) -> None:
    async with httpx.AsyncClient() as c:
        headers = {
            "Connection": "Close",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if token:
            headers["Authorization"] = f"Bearer {token}"

        r = await c.post(url, headers=headers, content=n.model_dump_json())

        if r.status_code > 399:
            logger.warning(
                "Failed to send notification to webhook from environment "
                f"{e.id}: {r.status_code} => {r.text}"
            )
