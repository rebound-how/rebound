import logging
import secrets
from base64 import b64decode, b64encode
from typing import Annotated, Any, Callable, Dict, Tuple
from urllib.parse import urlencode

from authlib.integrations.starlette_client import StarletteOAuth2App
from authlib.oidc.core import UserInfo
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from reliably_app import account, hasher, organization
from reliably_app.config import get_settings
from reliably_app.database import SessionLocal
from reliably_app.dependencies.database import get_db
from reliably_app.flags import bail_if_feature_not_enabled
from reliably_app.login import crud, has_provider, oauth, tasks
from reliably_app.login.providers.github import (
    map_userinfo as map_github_user_info,
)
from reliably_app.login.providers.google import (
    map_userinfo as map_google_user_info,
)
from reliably_app.login.providers.okta import map_userinfo as map_okta_user_info
from reliably_app.observability import span

router = APIRouter(prefix="/login")
logger = logging.getLogger("reliably_app")


@router.post(
    "/with/email",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Login via email and password",
    tags=["Auth"],
    summary="Login via email and password",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Logged or register'ed successfully",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": None,
            "description": "When password is invalid",
        },
    },
)
async def login_with_email(
    request: Request,
    background_tasks: BackgroundTasks,
    email: Annotated[str, Body(min_length=3)],
    password: Annotated[str, Body(min_length=8)],
    do_register: Annotated[bool, Body(alias="register")] = False,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    bail_if_feature_not_enabled("login-via-email")

    with span("login-with-email"):
        info = await auth_with_email(
            request,
            email.strip(),
            password.strip(),
            do_register,
            background_tasks,
            db,
        )

        if "error" in info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=info
            )

        return JSONResponse(info)


@router.get(
    "/with/{provider}",
    response_model=None,
    status_code=status.HTTP_302_FOUND,
    description="Redirect to the appropriate OpenID provider to allow/deny",
    tags=["Auth"],
    summary="Redirect to the OpenID provider",
    responses={
        status.HTTP_302_FOUND: {
            "model": None,
            "description": "Redirects to OpenID provider authentication page",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Unsupported OpenID provider",
        },
    },
)
async def login_with_provider(request: Request, provider: str) -> Any:
    with span(f"login-with-{provider}") as s:
        if not has_provider(provider):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        client = oauth.create_client(provider)
        if client is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        s.set_attribute("auth_provider", provider)

        state: Dict[str, str] = {}

        join_hash = request.query_params.get("join")
        if join_hash:
            state["join_hash"] = join_hash

        redirect_to = request.query_params.get("redirect_to")
        plan = request.query_params.get("plan")
        activity = request.query_params.get("activity")

        if redirect_to and plan in ("start", "scale"):
            state["redirect_to"] = redirect_to
            state["plan"] = plan

        elif redirect_to and activity:
            state["redirect_to"] = redirect_to
            state["activity"] = activity

        async with SessionLocal() as db:
            flow = await crud.create_auth_flow(db, provider, state)
            state_hash = str(flow.nonce)

        redirect_uri = str(request.url_for(f"auth_with_{provider}"))
        response = await client.authorize_redirect(
            request,
            redirect_uri=redirect_uri,
            state=b64encode(state_hash.encode("utf-8")).decode("utf-8"),
        )

        # some reverse proxies fail when content length is missing
        # they believe the connection was interrupted. It's a debatable point in
        # HTTP standards
        response.headers["content-length"] = "0"

        return response


@router.get(
    "/with/github/authorized",
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
    description="Redirected to the authenticated page from GitHub",
    tags=["Auth"],
    summary="Redirect to an authenticated page",
)
async def auth_with_github(
    request: Request,
    code: str,
    state: str,
    background_tasks: BackgroundTasks,
    id_token: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> str:
    return await auth_with_provider(
        "github",
        oauth.github,
        map_github_user_info,
        request,
        code,
        state,
        background_tasks,
        id_token,
        db,
    )


@router.get(
    "/with/google/authorized",
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
    description="Redirected to the authenticated page from Google",
    tags=["Auth"],
    summary="Redirect to an authenticated page",
)
async def auth_with_google(
    request: Request,
    code: str,
    state: str,
    background_tasks: BackgroundTasks,
    id_token: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> str:
    return await auth_with_provider(
        "google",
        oauth.google,
        map_google_user_info,
        request,
        code,
        state,
        background_tasks,
        id_token,
        db,
    )


@router.get(
    "/with/okta/authorized",
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
    description="Redirected to the authenticated page from Google",
    tags=["Auth"],
    summary="Redirect to an authenticated page",
)
async def auth_with_okta(
    request: Request,
    code: str,
    state: str,
    background_tasks: BackgroundTasks,
    id_token: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> str:
    return await auth_with_provider(
        "okta",
        oauth.okta,
        map_okta_user_info,
        request,
        code,
        state,
        background_tasks,
        id_token,
        db,
    )


###############################################################################
# Private functions
###############################################################################
async def auth_with_provider(
    provider: str,
    remote: StarletteOAuth2App,
    user_info_mapper: Callable,
    request: Request,
    code: str,
    state: str,
    background_tasks: BackgroundTasks,
    id_token: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> str:
    with span(f"login-auth-with-{provider}") as s:
        s.set_attribute("auth_provider", provider)

        if not state:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        try:
            nonce: str = b64decode(state.encode("utf-8")).decode("utf-8")
        except Exception:
            logger.warning("Failed to parse OAuth state", exc_info=True)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        async with SessionLocal() as d:
            flow = await crud.get_auth_flow(d, provider, nonce)

            if not flow:
                logger.warning("Using an invalid flow state")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

            await crud.disable_auth_flow(d, flow.id)  # type: ignore

        invite_reason: str | None = None
        invite_hash: str | None = None
        invite: organization.models.OrganizationInvitation | None = None
        invite_org: organization.models.Organization | None = None

        state_data = flow.state
        if state_data and isinstance(state_data, dict):
            invite_hash = state_data.get("join_hash")
            logger.debug(f"Found invitation hash {invite_hash}")
            if invite_hash:
                invite = await organization.crud.get_invitation_by_link_hash(
                    db, invite_hash.encode("utf-8")
                )
                if invite:
                    logger.debug(f"Found invitation {invite.id}")
                    s.set_attribute("invite_id", str(invite.id))
                    invite_org = await organization.crud.get_org(
                        db, invite.org_id
                    )

        # only accept to add user to org (from invitation) when limits allow
        if invite and invite_org:
            logger.debug(f"Found invitation {invite.id} to org {invite_org.id}")
            s.set_attribute("invite_org_id", str(invite_org.id))
            invite_reason = "success"
        elif invite and not invite_org:
            logger.debug(f"Found invitation {invite.id} but org has gone")
            invite_reason = "failed"
        elif invite_hash and not invite:
            logger.debug(f"Invitation with {invite_hash} has expired")
            invite_reason = "expired"

        org, user = await auth_with(
            request,
            remote,
            user_info_mapper,
            background_tasks,
            code,
            invite,
            invite_org,
            id_token,
            db,
        )

        s.set_attribute("org_id", str(org.id))
        s.set_attribute("org_name", str(org.name))
        s.set_attribute("user_id", str(user.id))
        s.set_attribute("username", str(user.username))

        qs = {"context": str(org.id)}
        redirect_to = state_data.get("redirect_to")
        plan = state_data.get("plan")
        activity = state_data.get("activity")
        if redirect_to and plan in ("start", "scale"):
            qs["redirect_to"] = redirect_to
            qs["plan"] = plan

        if redirect_to and activity:
            qs["redirect_to"] = redirect_to
            qs["activity"] = activity

        if invite_reason:
            s.set_attribute("invite_reason", invite_reason)
            qs["join"] = invite_reason

        if invite_org:
            qs["org"] = str(invite_org.name)
            qs["orgid"] = str(invite_org.id)

        q = urlencode(qs)

        request.session["user"] = str(user.id)

        return f"/authorized?{q}"


async def auth_with(
    request: Request,
    remote: StarletteOAuth2App,
    user_info_mapper: Callable,
    background_tasks: BackgroundTasks,
    code: str,
    invite: organization.models.OrganizationInvitation | None = None,
    invite_org: organization.models.Organization | None = None,
    id_token: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> Tuple[organization.models.Organization, account.models.User]:
    with span("auth"):
        if code:
            token = await remote.authorize_access_token(request)
            if id_token:
                token["id_token"] = id_token
        elif id_token:
            token = {"id_token": id_token}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if "id_token" in token:
            data = await remote.parse_id_token(token, None)
        else:
            remote.token = token
            data = await remote.userinfo(token=token)

        user_info: UserInfo = user_info_mapper(data)

        if await account.crud.get_user_by_openid(db, user_info) is None:
            org, user = await tasks.new_org(
                user_info.preferred_username, background_tasks, user_info
            )
        else:
            user = await account.crud.get_user_by_openid(
                db,
                user_info,  # type: ignore
            )
            orgs = await organization.crud.get_user_orgs(
                db,
                user.id,  # type: ignore
            )

            org = orgs[0]

        await tasks.user_joins_org(user, invite, invite_org)

        return (org, user)


async def auth_with_email(
    request: Request,
    email: str,
    password: str,
    register: bool,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    with span("login-auth-with-email") as s:
        invite_reason: str | None = None
        invite_hash: str | None = None
        invite: organization.models.OrganizationInvitation | None = None
        invite_org: organization.models.Organization | None = None

        invite_hash = request.query_params.get("join")
        logger.debug(f"Found invitation hash {invite_hash}")
        if invite_hash:
            invite = await organization.crud.get_invitation_by_link_hash(
                db, invite_hash.encode("utf-8")
            )
            if invite:
                logger.debug(f"Found invitation {invite.id}")
                s.set_attribute("invite_id", str(invite.id))
                invite_org = await organization.crud.get_org(
                    db,
                    invite.org_id,  # type: ignore
                )

        # only accept to add user to org (from invitation) when limits allow
        if invite and invite_org:
            logger.debug(f"Found invitation {invite.id} to org {invite_org.id}")
            s.set_attribute("invite_org_id", str(invite_org.id))
            invite_reason = "success"
        elif invite and not invite_org:
            logger.debug(f"Found invitation {invite.id} but org has gone")
            invite_reason = "failed"
        elif invite_hash and not invite:
            logger.debug(f"Invitation with {invite_hash} has expired")
            invite_reason = "expired"

        user = await account.crud.get_user_by_email(db, email)
        logger.debug(f"Attempt login from '{user.id if user else None}'")
        if user is None:
            if not register:
                logger.debug(
                    f"Email '{email}' used to login but user doesn't exist"
                )
                return {"error": "Invalid user or password"}
            else:
                user_info = UserInfo(
                    {
                        " ": secrets.token_hex(8),
                        "name": "",
                        "email": email,
                        "preferred_username": email,
                        "profile": None,
                        "picture": "",
                        "website": None,
                        "given_name": None,
                        "family_name": None,
                    }
                )

                org, user = await tasks.new_org(
                    user_info.preferred_username,
                    background_tasks,
                    user_info,
                    password=hasher.hash(password),
                )
                logger.debug(
                    f"New account '{user.id}' in org {org.name}' {org.id}"
                )

                settings = get_settings()
                await tasks.auto_join_orgs(settings.DEFAULT_ORGANIZATIONS, user)

                if settings.FEATURE_POPULATE_NEW_ORG_WITH_DEFAULTS:
                    await tasks.populate_organization_with_some_content(
                        org.id,  # type: ignore
                        user.id,  # type: ignore
                    )
        elif user.password is None:
            logger.debug(
                "Email '{email}' used to login but account created with "
                "openid before"
            )
            return {"error": "Invalid user or password"}
        else:
            if hasher.verify(str(user.password), password) is False:
                logger.debug(f"Email '{email}' used to login but invalid pwd")
                return {"error": "Invalid user or password"}

            orgs = await organization.crud.get_user_orgs(
                db,
                user.id,  # type: ignore
            )

            org = orgs[0]

            logger.debug(f"New login '{user.id}'")

        await tasks.user_joins_org(user, invite, invite_org)

        s.set_attribute("org_id", str(org.id))
        s.set_attribute("org_name", str(org.name))
        s.set_attribute("user_id", str(user.id))
        s.set_attribute("username", str(user.username))

        qs = {"context": str(org.id)}
        redirect_to = request.query_params.get("redirect_to")
        plan = request.query_params.get("plan")
        if redirect_to and plan in ("start", "scale"):
            qs["redirect_to"] = redirect_to
            qs["plan"] = plan

        if invite_reason:
            s.set_attribute("invite_reason", invite_reason)
            qs["join"] = invite_reason

        if invite_org:
            qs["org"] = str(invite_org.name)
            qs["orgid"] = str(invite_org.id)

        request.session["user"] = str(user.id)

        return qs
