import hashlib
import logging
from typing import Any, Dict

from reliably_app import environment
from reliably_app.config import get_settings
from reliably_app.integration import schemas
from reliably_app.integration.tasks import gcp, local

__all__ = ["store_integration_secrets", "delete_integration_secrets"]
logger = logging.getLogger("reliably_app")


async def store_integration_secrets(
    integration: schemas.IntegrationFull,
) -> None:
    settings = get_settings()
    strategy = settings.ENVIRONMENT_STORE_STRATEGY

    logger.debug(f"Storing integration secret with strategy: {strategy}")

    match strategy:
        case "gcp":
            return await gcp.store_integration_secrets(integration)
        case "local":
            return await local.store_integration_secrets(integration)


async def delete_integration_secrets(
    integration: schemas.IntegrationFull,
) -> None:
    settings = get_settings()
    strategy = settings.ENVIRONMENT_STORE_STRATEGY

    logger.debug(
        f"Deleting stored integration secret with strategy: {strategy}"
    )

    match strategy:
        case "gcp":
            return await gcp.delete_integration_secrets(integration)
        case "local":
            return await local.delete_integration_secrets(integration)


###############################################################################
# Private functions
###############################################################################
def get_control_from_integration(
    integration: schemas.Integration,
    env: environment.schemas.Environment,
) -> Dict[str, Any] | None:
    suffix = hashlib.md5(integration.name.encode("utf-8")).hexdigest()  # nosec

    match integration.provider:  # noqa
        case "slack":
            return {
                "name": "reliably-integration-slack",
                "provider": {
                    "type": "python",
                    "module": "chaosslack.control",
                    "secrets": ["reliably-integration-slack"],
                },
            }
        case "opentelemetry":
            return {
                "name": "reliably-integration-opentelemetry",
                "provider": {
                    "type": "python",
                    "module": "chaostracing.oltp",
                    "arguments": {
                        "trace_request": True,
                        "trace_httpx": True,
                        "trace_botocore": True,
                        "trace_urllib3": True,
                    },
                },
            }
        case "chatgpt":
            return remove_default_nones(
                {
                    "name": f"reliably-integration-chatgpt-{suffix}",
                    "provider": {
                        "type": "python",
                        "module": "chaosreliably.controls.chatgpt",
                        "arguments": {
                            "openai_model": {
                                "type": "env",
                                "key": "OPENAI_MODEL",
                            },
                        },
                    },
                }
            )
        case "prechecks":
            return remove_default_nones(
                {
                    "name": f"reliably-integration-prechecks-{suffix}",
                    "provider": {
                        "type": "python",
                        "module": "chaosreliably.controls.prechecks",
                        "arguments": {
                            "url": {
                                "type": "env",
                                "key": "RELIABLY_PRECHECKS_ENDPOINT",
                                "default": get_value_from_environment(
                                    "RELIABLY_PRECHECKS_ENDPOINT", env
                                ),
                            },
                            "auth": {
                                "type": "env",
                                "key": "RELIABLY_PRECHECKS_ENDPOINT_AUTH",
                            },
                        },
                    },
                }
            )
        case "safeguards":
            return remove_default_nones(
                {
                    "name": f"reliably-integration-safeguards-{suffix}",
                    "provider": {
                        "type": "python",
                        "module": "chaosreliably.controls.safeguards",
                        "arguments": {
                            "url": {
                                "type": "env",
                                "key": "RELIABLY_SAFEGUARDS_ENDPOINT",
                                "default": get_value_from_environment(
                                    "RELIABLY_PRECHECKS_ENDPOINT", env
                                ),
                            },
                            "frequency": {
                                "type": "env",
                                "key": "RELIABLY_SAFEGUARDS_FREQUENCY",
                                "default": get_value_from_environment(
                                    "RELIABLY_SAFEGUARDS_FREQUENCY", env
                                ),
                            },
                            "auth": {
                                "type": "env",
                                "key": "RELIABLY_SAFEGUARDS_ENDPOINT_AUTH",
                            },
                        },
                    },
                }
            )
        case "autopause":
            return remove_default_nones(
                {
                    "name": f"reliably-integration-autopause-{suffix}",
                    "provider": {
                        "type": "python",
                        "module": "chaosreliably.controls.autopause",
                        "arguments": {
                            "autopause": {
                                "method": {
                                    "actions": {
                                        "enabled": {
                                            "type": "env",
                                            "key": "RELIABLY_AUTOPAUSE_METHOD_ACTION_ENABLED",  # noqa: E501
                                            "default": get_value_from_environment(  # noqa: E501
                                                "RELIABLY_AUTOPAUSE_METHOD_ACTION_ENABLED",  # noqa: E501
                                                env,
                                            ),
                                        },
                                        "pause_duration": {
                                            "type": "env",
                                            "key": "RELIABLY_AUTOPAUSE_METHOD_ACTION_DURATION",  # noqa: E501
                                            "default": get_value_from_environment(  # noqa: E501
                                                "RELIABLY_AUTOPAUSE_METHOD_ACTION_DURATION",  # noqa: E501
                                                env,
                                            ),
                                        },
                                    },
                                    "probes": {
                                        "enabled": {
                                            "type": "env",
                                            "key": "RELIABLY_AUTOPAUSE_METHOD_PROBE_ENABLED",  # noqa: E501
                                            "default": get_value_from_environment(  # noqa: E501
                                                "RELIABLY_AUTOPAUSE_METHOD_PROBE_ENABLED",  # noqa: E501
                                                env,
                                            ),
                                        },
                                        "pause_duration": {
                                            "type": "env",
                                            "key": "RELIABLY_AUTOPAUSE_METHOD_PROBE_DURATION",  # noqa: E501
                                            "default": get_value_from_environment(  # noqa: E501
                                                "RELIABLY_AUTOPAUSE_METHOD_PROBE_DURATION",  # noqa: E501
                                                env,
                                            ),
                                        },
                                    },
                                },
                                "steady-state-hypothesis": {
                                    "enabled": {
                                        "type": "env",
                                        "key": "RELIABLY_AUTOPAUSE_SSH_ENABLED",
                                        "default": get_value_from_environment(
                                            "RELIABLY_AUTOPAUSE_SSH_ENABLED",
                                            env,
                                        ),
                                    },
                                    "pause_duration": {
                                        "type": "env",
                                        "key": "RELIABLY_AUTOPAUSE_SSH_DURATION",  # noqa: E501
                                        "default": get_value_from_environment(
                                            "RELIABLY_AUTOPAUSE_SSH_DURATION",
                                            env,
                                        ),
                                    },
                                },
                                "rollbacks": {
                                    "enabled": {
                                        "type": "env",
                                        "key": "RELIABLY_AUTOPAUSE_ROLLBACKS_ENABLED",  # noqa: E501
                                        "default": get_value_from_environment(
                                            "RELIABLY_AUTOPAUSE_ROLLBACKS_ENABLED",  # noqa: E501
                                            env,
                                        ),
                                    },
                                    "pause_duration": {
                                        "type": "env",
                                        "key": "RELIABLY_AUTOPAUSE_ROLLBACKS_DURATION",  # noqa: E501
                                        "default": get_value_from_environment(
                                            "RELIABLY_AUTOPAUSE_ROLLBACKS_DURATION",  # noqa: E501
                                            env,
                                        ),
                                    },
                                },
                            }
                        },
                    },
                }
            )

    return None


def get_value_from_environment(
    key: str, env: environment.schemas.Environment
) -> str | None:
    for v in env.envvars:
        if v.var_name == key:
            return v.value

    return None


def remove_default_nones(control: Dict[str, Any]) -> Dict[str, Any]:
    for arg in control["provider"].get("arguments", {}).values():
        clean_nones(arg)

    return control


def clean_nones(d: Dict[str, Any]) -> None:
    for arg in d.values():
        if isinstance(arg, dict):
            if "default" in arg:
                if arg["default"] is None:
                    arg.pop("default", None)
            else:
                clean_nones(arg)
