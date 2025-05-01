from typing import Dict, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import account, organization, token
from reliably_app.dependencies.auth import with_user
from reliably_app.dependencies.database import get_db
from reliably_app.me import schemas
from reliably_app.observability import span

__all__ = ["extend_routers"]

router = APIRouter()


def extend_routers(web: APIRouter) -> None:
    web.include_router(router, prefix="/me", include_in_schema=False)


@router.get(
    "/info",
    response_model=schemas.Info,
    status_code=status.HTTP_200_OK,
    description="Information on the user",
    tags=["Me"],
    summary="Information on the user",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Info,
            "description": "Ok Response",
        }
    },
)
async def info(
    user: account.models.User = Depends(with_user),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    attrs = {"user_id": str(user.id)}
    with span("api-me-info", attributes=attrs):
        info = {
            "profile": account.schemas.UserProfile(
                username=user.username,
                email=user.email,
                id=user.id,
                openid_profile=user.openid_profile,
            ),
            "orgs": await organization.crud.get_user_orgs(
                db,
                user.id,  # type: ignore
            ),
        }

        return info


@router.get(
    "/tokens",
    response_model=schemas.MyTokens,
    status_code=status.HTTP_200_OK,
    description="Tokens on the user per org",
    tags=["Me"],
    summary="Tokens on the user per org",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.MyTokens,
            "description": "Ok Response",
        }
    },
)
async def tokens(
    user: account.models.User = Depends(with_user),
    db: AsyncSession = Depends(get_db),
) -> List:
    attrs = {"user_id": str(user.id)}
    with span("api-me-tokens", attributes=attrs):
        data = []

        orgs = await organization.crud.get_user_orgs(
            db,
            user.id,  # type: ignore
        )
        for org in orgs:
            toks = await token.crud.get_tokens(
                db,
                org.id,  # type: ignore
                user.id,  # type: ignore
            )
            data.append({"org": org, "tokens": toks})

        return data
