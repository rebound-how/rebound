import importlib.resources
import logging
from functools import lru_cache
from urllib.parse import urlparse

import httpx

from reliably_app import environment, notification
from reliably_app.config import get_settings

__all__ = ["notify"]

logger = logging.getLogger("reliably_app")


async def notify(
    ev: notification.schemas.PlanEvent, e: environment.schemas.Environment
) -> None:
    logger.info(ev)
    if (ev.status is None or ev.status == "completed") and e.envvars.is_truthy(
        "RELIABLY_NOTIFICATION_GITHUB_ON_FAILURE_EVENTS"
    ):
        return None

    url = e.envvars.get("RELIABLY_NOTIFICATION_GITHUB_URL")
    if not url:
        logger.warning(
            "GitHub notification is enabled in the configuration but no "
            "repository URL was given in the integration. Ignoring event."
        )
        return None

    bearer = e.secrets.get("RELIABLY_NOTIFICATION_GITHUB_TOKEN")
    if not bearer:
        logger.warning(
            "GitHub notification is enabled in the configuration but no "
            "PAT token was given in the integration. Ignoring event."
        )
        return None

    labels = e.envvars.get("RELIABLY_NOTIFICATION_GITHUB_LABELS")

    await publish_notification(ev, url, e, bearer, labels)


###############################################################################
# Private functions
###############################################################################
@lru_cache
def load_template_by_type(event_type: str) -> str:
    with importlib.resources.path(
        "reliably_app.www.notifications.gh", f"{event_type}.md"
    ) as p:
        return p.read_text()


async def publish_notification(
    ev: notification.schemas.PlanEvent,
    url: str,
    e: environment.schemas.Environment,
    token: str | None = None,
    labels: str | None = None,
) -> None:
    settings = get_settings()

    pl = ev.plan
    x = ev.experiment

    domain = settings.RELIABLY_DOMAIN

    template_type = "plan-starting"
    if ev.deviated:
        template_type = "plan-deviated"
    elif ev.status == "interrupted":
        template_type = "plan-interrupted"
    elif ev.status == "aborted":
        template_type = "plan-aborted"
    elif ev.status == "failed":
        template_type = "plan-failed"
    elif ev.status == "completed":
        template_type = "plan-finished"

    template = load_template_by_type(template_type)
    md = template.format(
        username="",
        plan_link=f"{domain}/plans/view/?id={str(pl.id)}",
        build_link=f"{domain}/experiments/workflows/",
        plan_title=pl.definition.title,
        plan_desc=x.desc,
        status=ev.status,
        error_desc="kaboom",
    )

    p = urlparse(url)
    issue_url = f"{p.scheme}://api.{p.netloc}/repos{p.path}/issues"

    logger.info(issue_url)

    issue_labels = []
    if labels:
        issue_labels = [l.strip() for l in labels.split(",")]  # noqa: E741

    async with httpx.AsyncClient(http2=True) as c:
        headers = {
            "Connection": "Close",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        r = await c.post(
            issue_url,
            headers=headers,
            json={
                "title": f"Reliably Plan: {pl.definition.title}",
                "body": md,
                "labels": issue_labels,
            },
        )

        if r.status_code > 399:
            logger.warning(
                "Failed to send notification to github from environment "
                f"{e.id}: {r.status_code} => {r.text}"
            )
