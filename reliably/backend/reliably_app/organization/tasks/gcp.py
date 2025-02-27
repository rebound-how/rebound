import logging

from reliably_app.organization import models

__all__ = ["create_cloud_resources"]
logger = logging.getLogger("reliably_app")


async def create_cloud_resources(org: models.Organization) -> None:
    pass
