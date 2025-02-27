import logging
import random
from typing import List

from authlib.oidc.core import UserInfo
from fastapi import BackgroundTasks
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError

from reliably_app import (
    account,
    agent,
    background,
    deployment,
    organization,
    series,
)
from reliably_app.config import get_settings
from reliably_app.database import SessionLocal
from reliably_app.observability import span

__all__ = [
    "new_org",
    "user_joins_org",
    "populate_organization_with_some_content",
]
logger = logging.getLogger("reliably_app")


async def new_org(
    name: str,
    background_tasks: BackgroundTasks | None = None,
    info: UserInfo | None = None,
    password: str | None = None,
    owner: account.models.User | None = None,
    pending: bool = False,
    fail_on_duplicate_name: bool = False,
) -> tuple[
    organization.models.Organization,
    account.models.User,
]:
    settings = get_settings()

    async with SessionLocal() as db:
        if await organization.crud.has_name_been_already_taken(db, name):
            if fail_on_duplicate_name:
                raise organization.errors.OrgAlreadyExistError()

            suffix = "".join((str(s) for s in random.sample(range(0, 10), 5)))
            name = f"{name}{suffix}"

    with span("new-org-create-org", attributes={"name": name}):
        org = organization.models.Organization(name=name, pending=pending)
        async with SessionLocal() as db:
            try:
                db.add(org)
                await db.commit()
            except IntegrityError:
                raise organization.errors.OrgAlreadyExistError()

    if owner is None:
        with span("new-org-create-user"):
            owner = account.models.User(
                email=info.email,  # type: ignore
                username=name,
                openid_profile=dict(info),  # type: ignore
                password=password,
            )
            async with SessionLocal() as db:
                try:
                    db.add(owner)
                    await db.commit()
                except IntegrityError:
                    raise account.errors.UserAlreadyExistError()

    org_id = org.id
    user_id = owner.id
    attrs = {"org_id": str(org_id), "user_id": str(user_id)}

    with span("new-org-create-assoc-user-to-org", attributes=attrs):
        async with SessionLocal() as db:
            db_org_user = organization.models.OrganizationUsers(
                org_id=org_id,
                user_id=user_id,
                owner=True,
                agent=False,
            )
            db.add(db_org_user)
            await db.commit()

    with span("new-org-create-user-agent", attributes=attrs):
        await agent.crud.create_user_agent(
            org,
            user_id,  # type: ignore
            internal=True,
        )

    with span("new-org-initialize-series", attributes=attrs):
        await series.crud.org.initialize_org_series(org_id)

    if settings.FEATURE_CLOUD_DEPLOYMENT:
        with span("new-org-default-cloud-deployment", attributes=attrs):
            async with SessionLocal() as db:
                definition = (
                    deployment.schemas.DeploymentReliablyCloudDefinition()
                )  # noqa
                await deployment.crud.create_deployment(
                    db,
                    org.id,
                    deployment.schemas.DeploymentCreate(
                        name="cloud", definition=definition
                    ),
                )

    if background_tasks:
        with span("new-org-create-cloud-resources", attributes=attrs):
            background_tasks.add_task(organization.tasks.create_resources, org)

    return (org, owner)


async def user_joins_org(
    user: account.models.User,
    invite: organization.models.OrganizationInvitation | None = None,
    invite_org: organization.models.Organization | None = None,
) -> None:
    if invite and invite_org:
        attrs = {
            "user_id": str(user.id),
            "invite_id": str(invite.id),
            "invite_org_id": str(invite_org.id),
        }
        with span("invite-user-during-login", attributes=attrs):
            async with SessionLocal() as d:
                await organization.crud.add_user(d, invite_org, user)
                async with SessionLocal() as p:
                    await organization.crud.update_users_count(  # noqa
                        p,
                        invite_org.id,  # type: ignore
                    )

                with span("invite-create-agent") as p:
                    agt = await agent.crud.create_user_agent(
                        invite_org,
                        user.id,  # type: ignore
                        internal=True,
                    )
                    p.set_attribute("agent_id", str(agt.id))


async def auto_join_orgs(
    org_names: List[str],
    user: account.models.User,
) -> organization.models.Organization:
    async with SessionLocal() as db:
        main_org = None
        for org_name in org_names:
            org = await organization.crud.get_org_by_name(db, org_name)
            if not org:
                logger.error(
                    f"Failed to join organization {org_name}. It does "
                    "not exist in our records."
                )
                continue

            if main_org is None:
                main_org = org

            async with SessionLocal() as d:
                await organization.crud.add_user(d, org, user)
                async with SessionLocal() as p:
                    await organization.crud.update_users_count(  # noqa
                        p,
                        org.id,  # type: ignore
                    )

                await agent.crud.create_user_agent(
                    org,
                    user.id,  # type: ignore
                    internal=True,
                )

            logger.debug(f"User {user.id} added to org {org.id}")

    if not main_org:
        raise ValueError("failed to locate a default organization to join")

    return main_org


async def add_new_user(user_info: UserInfo) -> account.models.User:
    async with SessionLocal() as db:
        user = await account.crud.create_user(
            db,
            account.schemas.UserCreate(
                email=user_info.email,
                username=user_info.preferred_username,
                openid=dict(user_info),
                as_agent=False,
            ),
        )

    return user


async def populate_organization_with_some_content(
    org_id: UUID4, user_id: UUID4
) -> None:
    background.add_background_async_task(
        organization.tasks.populate_organization(org_id, user_id),
        name=f"Populate user organization {org_id}",
    )
