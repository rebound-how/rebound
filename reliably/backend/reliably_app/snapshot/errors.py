__all__ = ["DiscoveryError"]


class DiscoveryError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
