from reliably_app.environment import schemas

__all__ = [
    "store_environment_secrets",
    "delete_environment_secrets",
    "update_environment_secret",
    "remove_environment_secret",
]


async def store_environment_secrets(environment: schemas.Environment) -> None:
    pass


async def delete_environment_secrets(environment: schemas.Environment) -> None:
    pass


async def update_environment_secret(
    environment: schemas.Environment,
    new_sec: schemas.EnvironmentSecretAsFile | schemas.EnvironmentSecret,
) -> None:
    pass


async def remove_environment_secret(
    environment: schemas.Environment, key: str
) -> None:
    pass
