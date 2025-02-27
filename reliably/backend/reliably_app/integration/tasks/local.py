import logging

from reliably_app.integration import schemas

__all__ = ["delete_integration_secrets", "store_integration_secrets"]
logger = logging.getLogger("reliably_app")


async def store_integration_secrets(
    integration: schemas.IntegrationFull,
) -> None:
    pass


async def delete_integration_secrets(
    integration: schemas.IntegrationFull,
) -> None:
    pass
