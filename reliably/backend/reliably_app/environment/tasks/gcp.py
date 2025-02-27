import logging

from reliably_app.environment import schemas

__all__ = [
    "delete_environment_secrets",
    "store_environment_secrets",
    "update_environment_secret",
    "remove_environment_secret",
]
logger = logging.getLogger("reliably_app")


async def store_environment_secrets(
    environment: schemas.Environment,
) -> None:
    pass


async def delete_environment_secrets(environment: schemas.Environment) -> None:
    pass


async def update_environment_secret(
    environment: schemas.Environment,
    new_sec: schemas.EnvironmentSecretAsFile | schemas.EnvironmentSecret,
) -> None:
    pass


async def remove_environment_secret(
    environment: schemas.Environment,
    key: str,
) -> None:
    pass
