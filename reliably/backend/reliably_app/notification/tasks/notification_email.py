import asyncio
import importlib.resources
import logging
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import lru_cache
from typing import Tuple
from urllib.parse import urlencode

from croniter import croniter
from pydantic import UUID4

from reliably_app import environment, notification
from reliably_app.config import get_settings, Settings

__all__ = ["notify"]

logger = logging.getLogger("reliably_app")
TREND_COLORS = {
    0.0: "rgb(255, 60, 88)",
    0.5: "rgb(255, 165, 0)",
    1.0: "rgb(85, 185, 85)",
}


async def notify(
    ev: notification.schemas.PlanEvent, e: environment.schemas.Environment
) -> None:
    settings = get_settings()

    if is_email_notification_disabled(settings):
        logger.debug("Email notification is disabled.")
        return None

    loop = asyncio.get_running_loop()

    f = loop.run_in_executor(None, dispatch_event, settings, ev, e)
    await asyncio.wait_for(f, timeout=20)


###############################################################################
# Private functions
###############################################################################
def dispatch_event(
    settings: Settings,
    ev: notification.schemas.PlanEvent,
    e: environment.schemas.Environment,
) -> None:
    if ev.kind == "plan-phases":
        _send_plan_email(settings, ev, e)


def _send_plan_email(
    settings: Settings,
    ev: notification.schemas.PlanEvent,
    e: environment.schemas.Environment,
) -> None:
    smtp_addr = settings.SMTP_ADDR
    smtp_port = settings.SMTP_PORT
    smtp_username = settings.SMTP_USERNAME
    smtp_pwd = settings.SMTP_PASSWORD
    smtp_from = settings.SMTP_FROM_EMAIL or smtp_username

    vars = e.envvars
    to_addresses = vars.get("RELIABLY_NOTIFICATION_TO_ADDRESSES")

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
    html = configure_template(settings, ev, template)

    m = MIMEMultipart()
    m["From"] = smtp_from  # type: ignore
    m["To"] = to_addresses  # type: ignore
    m["Subject"] = f"Reliably Plan - {ev.plan.definition.title}"
    m.attach(MIMEText(html, _subtype="html"))

    with smtplib.SMTP_SSL(smtp_addr, smtp_port) as c:  # type: ignore
        c.login(
            user=smtp_username,  # type: ignore
            password=smtp_pwd,  # type: ignore
        )

        try:
            errors = c.send_message(m)
            if errors:
                logger.error(
                    "Failed to send notification email. "
                    f"We will not try again: {errors}"
                )
        except smtplib.SMTPException:
            logger.error(
                "Failed to send notification email. We will not try again",
                exc_info=True,
            )


def is_email_notification_disabled(settings: Settings) -> bool:
    return settings.FEATURE_NOTIFICATION_VIA_EMAIL is False


@lru_cache
def load_template_by_type(event_type: str) -> str:
    with importlib.resources.path(
        "reliably_app.www.notifications.emails", f"{event_type}.html"
    ) as p:
        return p.read_text()


def configure_template(
    settings: Settings, event: notification.schemas.PlanEvent, template: str
) -> str:
    pl = event.plan
    x = event.experiment
    domain = settings.RELIABLY_DOMAIN

    if event.deviated or event.status in ("interrupted", "aborted", "failed"):
        exec_id = str(event.execution_id)
        html = template.format(
            username="",
            execution_link=f"{domain}/executions/view/?id={exec_id}&exp={x.id}",
            plan_title=pl.definition.title,
            plan_desc=x.desc,
            meta=build_meta(event, domain),
            error="",
        )
    elif event.status == "completed":
        exec_id = str(event.execution_id)
        html = template.format(
            username="",
            execution_link=f"{domain}/executions/view/?id={exec_id}&exp={x.id}",
            build_link=f"{domain}/experiments/workflows/",
            plan_title=pl.definition.title,
            count=build_count(x.executions_count),
            trend=build_trend(x.id, x.trend, domain),  # type: ignore
            score=build_score(x.score),
        )
    else:
        html = template.format(
            username="",
            plan_link=f"{domain}/plans/view/?id={str(pl.id)}",
            build_link=f"{domain}/experiments/workflows/",
            plan_title=pl.definition.title,
            plan_desc=x.desc,
            count=build_count(x.executions_count),
            trend=build_trend(x.id, x.trend, domain),  # type: ignore
            score=build_score(x.score),
            meta=build_meta(event, domain),
        )

    return html


def build_meta(event: notification.schemas.PlanEvent, domain: str) -> str:
    html = ""

    if event.experiment.last_execution:
        dt = event.experiment.last_execution.strftime("%Y/%m/%d, %H:%M:%S")
        html += f"<span>Last Executed on {dt} UTC</span>"

    if event.deployment:
        dep_link = f"{domain}/deployments/view/?id={str(event.deployment.id)}"
        html += f' | <span>Deployed on <a href="{dep_link}">{event.deployment.name}</a></span>'  # noqa: E501

        s = event.plan.definition.schedule
        if s.type == "cron":
            now = datetime.now(tz=timezone.utc)
            c = (
                croniter(s.pattern, now, ret_type=datetime)
                .get_next()
                .strftime("%Y/%m/%d, %H:%M:%S")
            )
            html += f" | <span>Next Run on {c} UTC</span>"

    return html


def build_count(count: int | None) -> str:
    style = "margin: auto; width:30px; height:30px; border-radius: .4rem"

    if count is None:
        style = f"{style}; background-color: rgb(233, 234, 241); color: rgb(84, 84, 89); opacity: 0;"  # noqa: E501

    inner_style = "text-align: center; padding: 0.3rem; font-size: 1.4rem; font-weight: 700; line-height: 0.9;"  # noqa: E501
    html = f"""
    <div style="{style}"><div style="{inner_style}">{count or "-"}</div></div>
    """

    return html.strip()


def build_trend(
    exp_id: UUID4, trend: list[Tuple[UUID4, str, float]], domain: str
) -> str:
    columns = []
    for exec_id, _, value in trend[:10]:
        c = TREND_COLORS[value]
        qs = urlencode({"id": exec_id, "exp": exp_id})
        link = f"{domain}/executions/view/?{qs}"
        columns.append(
            """<td style="padding:0; margin:0;">"""
            f"""<a href="{link}" style="display:block; width:12px; height:30px; border-radius: calc(.5 * .4rem); background-color:{c}; text-decoration:none; mso-line-height-rule:exactly; line-height:0;">&nbsp;</a>"""  # noqa: E501
            "</td>"
        )

    columns = '<td style="width:4px;">&nbsp;</td>'.join(columns)  # type: ignore

    html = f"""
    <div>
        <table border="0" cellspacing="0" cellpadding="0" align="center">
        <tr>
            {columns}
        </tr>
        </table>
    </div>
    """

    return html


def build_score(score: float | None) -> str:
    letter = "-"
    style = "margin: auto; width:30px; height:30px; border-radius: .4rem"

    if score is None:
        style = f"{style}; background-color: rgb(233, 234, 241); color: rgb(84, 84, 89); opacity: 0;"  # noqa: E501
    elif score >= 0.9:
        letter = "A"
        style = f"{style}; background-color: rgb(85, 185, 85); color: rgb(7, 30, 34);"  # noqa: E501
    elif 0.7 < score <= 0.9:
        letter = "B"
        style = f"{style}; background-color: rgb(239, 223, 11); color: rgb(7, 30, 34);"  # noqa: E501
    elif 0.5 <= score <= 0.7:
        letter = "C"
        style = f"{style}; background-color: rgb(255, 165, 0); color: rgb(7, 30, 34);"  # noqa: E501
    elif score < 0.5:
        letter = "D"
        style = f"{style}; background-color: rgb(255, 60, 88); color: rgb(7, 30, 34);"  # noqa: E501

    inner_style = "text-align: center; padding: 0.3rem; font-size: 1.4rem; font-weight: 700; line-height: 0.9;"  # noqa: E501
    html = f"""
    <div style="{style}"><div style="{inner_style}">{letter}</div></div>
    """

    return html.strip()
