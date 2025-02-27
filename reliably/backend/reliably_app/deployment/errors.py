__all__ = ["DeploymentAlreadyExistsError", "DeploymentNotFoundError"]


class DeploymentAlreadyExistsError(Exception):
    pass


class DeploymentNotFoundError(Exception):
    pass
