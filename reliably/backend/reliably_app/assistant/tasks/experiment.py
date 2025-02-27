import asyncio
import json
import logging
from base64 import b64encode
from copy import deepcopy
from typing import Any, Dict, List, cast

import httpx
import itsdangerous

from reliably_app import config
from reliably_app.assistant import schemas

__all__ = ["create_experiment_from_scenario"]
logger = logging.getLogger("reliably_app")


async def create_experiment_from_scenario(
    user_id: str, context: schemas.ScenarioExperimentCreate
) -> Dict[str, Any]:
    settings = config.get_settings()
    session_cookie = get_session_cookie(settings, user_id)

    x = create_base_experiment(context)

    async def fetch_starter(
        item: schemas.ScenarioCreateItem,
    ) -> Dict[str, Any] | None:
        async with httpx.AsyncClient(http2=True) as c:
            r = await c.get(
                get_url(settings, item.name),
                cookies={"session": session_cookie},
            )

            if r.status_code > 399:
                logger.error(
                    f"Failed to fetch starter {item.name}: {r.status_code}"
                )
                return None

            return cast(dict[str, Any], r.json())

    starters = await asyncio.gather(
        *[fetch_starter(item) for item in context.items]
    )

    list([add_activity_from_starter(x, s) for s in starters if s is not None])  # type: ignore

    cleanup_experiment(x)

    return x


###############################################################################
# Private functions
###############################################################################
def get_session_cookie(settings: config.Settings, user_id: str) -> str:
    secret_key = settings.SESSION_SECRET_KEY.get_secret_value()

    signer = itsdangerous.TimestampSigner(str(secret_key))
    data = b64encode(json.dumps({"user": user_id}).encode("utf-8"))
    return signer.sign(data).decode("utf-8")


def get_url(settings: config.Settings, target: str) -> str:
    reliably_host = settings.RELIABLY_DOMAIN
    reliably_host = reliably_host.replace("https://", "")
    return f"https://{reliably_host}/templates/experiments/{target}.json"


def add_activity_from_starter(
    experiment: Dict[str, Any], starter: Dict[str, Any]
) -> None:
    template = starter["spec"]["template"]

    method = template.get("method")
    if method:
        experiment["method"].append(deepcopy(method[0]))

    rollbacks = template.get("rollbacks")
    if rollbacks:
        experiment["rollbacks"].append(deepcopy(rollbacks[0]))

    ssh = template.get("steady-state-hypothesis", {}).get("probes")
    if ssh:
        experiment["steady-state-hypothesis"]["probes"].append(deepcopy(ssh[0]))


def create_base_experiment(
    context: schemas.ScenarioExperimentCreate,
) -> Dict[str, Any]:
    x = {
        "title": context.title,
        "description": context.description,
        "contributions": {
            "errors": "none",
            "latency": "none",
            "security": "none",
            "availability": "none",
        },
        "runtime": {"rollbacks": {"strategy": "always"}},
        "configuration": fill_configuration(context.items),
        "steady-state-hypothesis": {"title": context.title, "probes": []},
        "method": [],
        "rollbacks": [],
    }

    if context.tags:
        x["tags"] = deepcopy(context.tags)

    if context.contributions:
        x["contributions"] = deepcopy(context.contributions)

    return x


def cleanup_experiment(experiment: Dict[str, Any]) -> None:
    if len(experiment["tags"]) == 0:
        experiment.pop("tags", None)

    if len(experiment["rollbacks"]) == 0:
        experiment.pop("rollbacks", None)

    if len(experiment["steady-state-hypothesis"]["probes"]) == 0:
        experiment.pop("steady-state-hypothesis", None)


def fill_configuration(
    items: List[schemas.ScenarioCreateItem],
) -> Dict[str, Any]:
    c = {}

    indices = {"R": 0, "M": 0, "H": 0}

    for item in items:
        suffix: str
        match item.target:
            case "hypothesis":
                suffix = "H"
            case "method":
                suffix = "M"
            case "rollbacks":
                suffix = "R"

        for p in item.parameters:
            c[p.name] = {
                "type": "env",
                "key": f"RELIABLY_{p.name.upper()}_{suffix}{str(indices[suffix]).zfill(2)}",  # noqa E501
                "env_var_type": p.type,
            }

            if p.value is not None and p.type in (
                "string",
                "number",
                "integer",
                "float",
                "boolean",
            ):
                c[p.name]["default"] = p.value
            elif p.type == "object":
                c[p.name]["default"] = p.value

    return c
