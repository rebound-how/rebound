from typing import Tuple

from fastapi import Depends, HTTPException, status

from reliably_app import account

__all__ = ["valid_in_scope"]


def valid_in_scope(
    user: account.models.User = Depends(account.validators.valid_user),
    scopes: Tuple[str] = ("user",),
) -> account.models.User:
    if user.as_agent and "agent" not in scopes:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    return user
