__all__ = ["EnvironmentNotFoundError", "EnvironmentSecretCreationError"]


class EnvironmentNotFoundError(Exception):
    pass


class EnvironmentSecretCreationError(Exception):
    def __init__(self, env_id: str, message: str) -> None:
        self.env_id = env_id
        self.message = message
