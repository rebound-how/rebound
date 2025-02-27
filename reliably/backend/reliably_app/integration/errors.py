__all__ = [
    "IntegrationAlreadyExistsError",
    "IntegrationNotFoundError",
    "IntegrationSecretCreationError",
]


class IntegrationAlreadyExistsError(Exception):
    pass


class IntegrationNotFoundError(Exception):
    pass


class IntegrationSecretCreationError(Exception):
    def __init__(self, integration_id: str, message: str) -> None:
        self.integration_id = integration_id
        self.message = message
