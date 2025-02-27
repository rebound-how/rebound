from typing import Any, cast

from fastapi import HTTPException, status

from .config import get_settings

__all__ = ["bail_if_feature_not_enabled"]


def bail_if_feature_not_enabled(
    feature: str,
    value: Any | None = None,
    status: int = status.HTTP_404_NOT_FOUND,
) -> None:
    settings = get_settings()

    match feature:
        case "login-via-email":
            if settings.FEATURE_LOGIN_EMAIL is False:
                raise HTTPException(status_code=status)
        case "create-deployment":
            match cast(str, value):
                case "container":
                    if settings.FEATURE_CONTAINER_DEPLOYMENT is False:
                        raise HTTPException(status_code=status)
                case "k8s_job":
                    if settings.FEATURE_K8S_JOB_DEPLOYMENT is False:
                        raise HTTPException(status_code=status)
