import logging

from reliably_app.config import get_settings
from reliably_app.environment import schemas
from reliably_app.environment.tasks import aws, gcp, local

__all__ = [
    "store_environment_secrets",
    "delete_environment_secrets",
    "update_environment_secrets",
]
logger = logging.getLogger("reliably_app")


async def store_environment_secrets(environment: schemas.Environment) -> None:
    settings = get_settings()
    strategy = settings.ENVIRONMENT_STORE_STRATEGY

    logger.debug(f"Storing secret with strategy: {strategy}")

    match strategy:
        case "gcp":
            return await gcp.store_environment_secrets(environment)
        case "local":
            return await local.store_environment_secrets(environment)
        case "aws":
            return await aws.store_environment_secrets(environment)


async def delete_environment_secrets(environment: schemas.Environment) -> None:
    settings = get_settings()
    strategy = settings.ENVIRONMENT_STORE_STRATEGY

    logger.debug(f"Deleting stored secret with strategy: {strategy}")

    match strategy:
        case "gcp":
            return await gcp.delete_environment_secrets(environment)
        case "local":
            return await local.delete_environment_secrets(environment)
        case "aws":
            return await aws.delete_environment_secrets(environment)


async def update_environment_secret(
    environment: schemas.Environment,
    new_sec: schemas.EnvironmentSecretAsFile | schemas.EnvironmentSecret,
) -> None:
    settings = get_settings()
    strategy = settings.ENVIRONMENT_STORE_STRATEGY

    logger.debug(f"Updating secret key with strategy: {strategy}")

    match strategy:
        case "gcp":
            return await gcp.update_environment_secret(environment, new_sec)
        case "local":
            return await local.update_environment_secret(environment, new_sec)
        case "aws":
            return await aws.update_environment_secret(environment, new_sec)


async def remove_environment_secret(
    environment: schemas.Environment, key: str
) -> None:
    settings = get_settings()
    strategy = settings.ENVIRONMENT_STORE_STRATEGY

    logger.debug(f"Removing secret key with strategy: {strategy}")

    match strategy:
        case "gcp":
            return await gcp.remove_environment_secret(environment, key)
        case "local":
            return await local.remove_environment_secret(environment, key)
        case "aws":
            return await aws.remove_environment_secret(environment, key)
