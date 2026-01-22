from typing import Annotated, Optional, Tuple
from typing_extensions import Doc

from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi import Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyBase, APIKeyHeader
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from reliably_app import account, organization, token
from reliably_app.dependencies.database import get_db
from reliably_app.dependencies.org import valid_org
from reliably_app.observability import span

__all__ = ["validate_auth", "with_user_in_org", "with_admin_user"]


class _APIKeySession(APIKeyBase):  # pragma: no cover
    def __init__(
        self,
        *,
        name: str,
    ) -> None:
        self.name = name

    async def __call__(self, request: Request) -> str | None:
        api_key = request.session.get(self.name)
        return api_key


class APIKeySession(APIKeyBase):  # pragma: no cover
    def __init__(
        self,
        *,
        name: Annotated[
            str,
            Doc("Query parameter name."),
        ],
        scheme_name: Annotated[
            Optional[str],
            Doc(
                """
                Security scheme name.

                It will be included in the generated OpenAPI.
                """
            ),
        ] = None,
        description: Annotated[
            Optional[str],
            Doc(
                """
                Security scheme description.

                It will be included in the generated OpenAPI.
                """
            ),
        ] = None,
        auto_error: Annotated[
            bool,
            Doc(
                """
                By default, if the session is not provided, `APIKeySession` will
                automatically cancel the request and send the client an error.

                If `auto_error` is set to `False`, when the query parameter is
                not available, instead of erroring out, the dependency result
                will be `None`.

                This is useful when you want to have optional authentication.

                It is also useful when you want to have authentication that can
                be provided in one of multiple optional ways.
                """
            ),
        ] = True,
    ):
        self.model: APIKey = APIKey(
            **{"in": APIKeyIn.query},
            name=name,
            description=description,
        )
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> Optional[str]:
        api_key = request.session.get(self.model.name)
        return self.check_api_key(api_key)


api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
api_key_session = APIKeySession(name="user", auto_error=False)


async def validate_auth(
    request: Request,
    authorization: str = Security(api_key_header),
    user_id: str = Security(api_key_session),
    db: AsyncSession = Depends(get_db),
) -> Tuple[UUID4 | None, UUID4, UUID4 | None]:
    attrs = {"user_id": str(user_id)}

    with span("validate-auth", attributes=attrs) as s:
        if not authorization and not user_id:
            s.set_attribute("reason", "Missing credentials")
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
            )

        # API calls require the Authorization header
        if request.url.path.startswith("/api/v1") and not authorization:
            s.set_attribute("reason", "Missing Auth header")
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
            )

        # Web calls require a session
        if not request.url.path.startswith("/api/v1") and not user_id:
            s.set_attribute("reason", "Missing session cookie")
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
            )

        if authorization:
            scheme, _, param = authorization.partition(" ")
            if not scheme or scheme.lower() != "bearer":
                s.set_attribute("reason", "invalid auth header")
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )

            try:
                token_value = param.encode("utf-8")
            except UnicodeEncodeError:
                s.set_attribute("reason", "invalid auth encoding")
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )

            if len(token_value) != 32:
                s.set_attribute("reason", "invalid auth length")
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )

            user_token = await token.crud.get_by_token_value(db, token_value)
            if not user_token:
                s.set_attribute("reason", "invalid token")
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )

            if user_token.revoked:
                s.set_attribute("reason", "token revoked")
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )

            s.set_attribute("org_id", str(user_token.org_id))
            s.set_attribute("token_id", str(user_token.id))

            return (
                user_token.org_id,
                user_token.user_id,  # type: ignore
                user_token.id,
            )
        else:
            return None, user_id, None  # type: ignore


async def with_user_in_org(
    creds: Tuple[UUID4 | None, UUID4, UUID4 | None] = Depends(validate_auth),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> account.models.User:
    with span("with-user-in-org") as s:
        _, user_id, _ = creds
        s.set_attribute("user_id", str(user_id))
        s.set_attribute("org_id", str(org.id))

        if not await organization.crud.does_user_belong_to_org(
            db,
            org.id,  # type: ignore
            user_id,
        ):
            s.set_attribute("reason", "user not authorized in org")
            raise HTTPException(status.HTTP_403_FORBIDDEN)

        user = await account.crud.get_user(db, user_id)
        if not user:
            s.set_attribute("reason", "user not found")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        return user


async def with_user(
    creds: Tuple[UUID4 | None, UUID4, UUID4 | None] = Depends(validate_auth),
    db: AsyncSession = Depends(get_db),
) -> account.models.User:
    with span("with-user") as s:
        _, user_id, _ = creds
        s.set_attribute("user_id", str(user_id))

        user = await account.crud.get_user(db, user_id)
        if not user:
            s.set_attribute("reason", "user not found")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        return user


async def with_admin_user(
    creds: Tuple[UUID4 | None, UUID4, UUID4 | None] = Depends(validate_auth),
    db: AsyncSession = Depends(get_db),
) -> account.models.User:
    with span("with-admin-user") as s:
        _, user_id, _ = creds
        s.set_attribute("user_id", str(user_id))

        user = await account.crud.get_user(db, user_id)
        if not user:
            s.set_attribute("reason", "user not found")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        return user
