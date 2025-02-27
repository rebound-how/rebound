from typing import List, cast

from pydantic import UUID4
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import account
from reliably_app.organization import errors, models, schemas

__all__ = [
    "create_org",
    "is_name_available",
    "get_org",
    "get_org_by_name",
    "get_user_first_org",
    "delete_org",
    "add_user",
    "get_org_users",
    "remove_user",
    "get_user_orgs",
    "does_user_belong_to_org",
    "create_invitation",
    "get_invitation_by_link_hash",
    "update_consumed_minutes",
]


async def create_org(
    db: AsyncSession,
    org: schemas.OrganizationCreate,
    pending: bool = False,
) -> models.Organization:
    db_org = models.Organization(name=org.name, pending=pending)

    try:
        db.add(db_org)
        await db.commit()
    except IntegrityError:
        raise errors.OrgAlreadyExistError()

    return cast(models.Organization, db_org)


async def is_name_available(db: AsyncSession, candidate: str) -> bool:
    result = await db.execute(
        select(models.Organization.id).where(
            models.Organization.name == candidate
        )
    )
    return result.scalar() is None


async def get_org(
    db: AsyncSession, org_id: UUID4 | str
) -> models.Organization | None:
    return (
        (
            await db.execute(
                select(models.Organization).where(
                    models.Organization.id == str(org_id)
                )
            )
        )
        .scalars()
        .first()
    )


async def get_org_by_name(
    db: AsyncSession,
    name: str,
) -> models.Organization | None:
    return (
        (
            await db.execute(
                select(models.Organization).where(
                    models.Organization.name == name
                )
            )
        )
        .scalars()
        .first()
    )


async def get_user_first_org(
    db: AsyncSession, user_id: UUID4
) -> models.Organization | None:
    return (
        (
            await db.execute(
                select(models.Organization)
                .where(
                    models.Organization.id.in_(
                        select(models.OrganizationUsers.org_id).filter(
                            models.OrganizationUsers.user_id == str(user_id)
                        )
                    )
                )
                .where(models.Organization.deleted.is_(False))
                .order_by(models.Organization.created_date)
                .limit(1)
            )
        )
        .scalars()
        .first()
    )


async def mark_deleted(db: AsyncSession, org_id: UUID4) -> None:
    await db.execute(
        update(models.Organization)
        .where(models.Organization.id == str(org_id))
        .values(deleted=True)
    )
    await db.commit()


async def is_deleted(db: AsyncSession, org_id: UUID4) -> bool:
    result = await db.execute(
        select(models.Organization.id)
        .where(models.Organization.id == str(org_id))
        .where(models.Organization.deleted.is_(True))
    )
    return result.scalar() is not None


async def is_owner(db: AsyncSession, org_id: UUID4, user_id: UUID4) -> bool:
    result = await db.execute(
        select(models.OrganizationUsers.org_id)
        .where(models.OrganizationUsers.org_id == str(org_id))
        .where(models.OrganizationUsers.user_id == str(user_id))
        .where(models.OrganizationUsers.owner.is_(True))
    )
    return result.scalar() is not None


async def enable_org(db: AsyncSession, org_id: UUID4) -> None:
    await db.execute(
        update(models.Organization)
        .where(models.Organization.id == str(org_id))
        .values(pending=False)
    )
    await db.commit()


async def block_org(db: AsyncSession, org_id: UUID4) -> None:
    await db.execute(
        update(models.Organization)
        .where(models.Organization.id == str(org_id))
        .values(blocked=True)
    )
    await db.commit()


async def delete_org(db: AsyncSession, org_id: UUID4) -> None:
    await db.execute(
        delete(models.Organization).where(models.Organization.id == str(org_id))
    )
    await db.commit()


async def get_org_users(
    db: AsyncSession, org_id: UUID4, page: int = 0, limit: int = 10
) -> List[account.models.User]:
    return (
        (
            await db.execute(
                select(account.models.User)
                .where(
                    account.models.User.id.in_(
                        select(models.OrganizationUsers.user_id)
                        .where(models.OrganizationUsers.org_id == str(org_id))
                        .where(models.OrganizationUsers.agent.is_(False))
                    )
                )
                .offset(page)
                .limit(limit)
            )
        )
        .scalars()
        .all()
    )


async def count_user_organizations(db: AsyncSession, user_id: UUID4) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.OrganizationUsers.org_id))
                .where(models.OrganizationUsers.user_id == str(user_id))
                .where(models.OrganizationUsers.agent.is_(False))
            )
        ).scalar_one(),
    )


async def get_user_orgs(
    db: AsyncSession, user_id: UUID4, page: int = 0, limit: int = 10
) -> List[models.Organization]:
    return (
        (
            await db.execute(
                select(models.Organization)
                .where(
                    models.Organization.id.in_(
                        select(models.OrganizationUsers.org_id).filter(
                            models.OrganizationUsers.user_id == str(user_id)
                        )
                    )
                )
                .where(models.Organization.deleted.is_(False))
                .offset(page)
                .limit(limit)
            )
        )
        .scalars()
        .all()
    )


async def add_user(
    db: AsyncSession,
    org: models.Organization,
    user: account.models.User,
    agent: bool = False,
) -> None:
    db_org_user = models.OrganizationUsers(
        org_id=org.id, user_id=user.id, owner=False, agent=agent
    )
    db.add(db_org_user)
    await db.commit()


async def remove_user(
    db: AsyncSession, org: models.Organization, user: account.models.User
) -> None:
    await db.execute(
        delete(models.OrganizationUsers)
        .where(models.OrganizationUsers.org_id == str(org.id))
        .where(models.OrganizationUsers.user_id == str(user.id))
    )
    await db.commit()


async def does_user_belong_to_org(
    db: AsyncSession, org_id: UUID4, user_id: UUID4
) -> bool:
    result = await db.execute(
        select(models.OrganizationUsers.id)
        .where(models.OrganizationUsers.org_id == str(org_id))
        .where(models.OrganizationUsers.user_id == str(user_id))
    )
    return result.scalar() is not None


async def count_users_in_org(db: AsyncSession, org_id: UUID4) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.OrganizationUsers.user_id))
                .where(models.OrganizationUsers.org_id == str(org_id))
                .where(models.OrganizationUsers.agent.is_(False))
            )
        ).scalar_one(),
    )


async def set_role_name(
    db: AsyncSession, org_id: UUID4 | str, role: str
) -> None:
    await db.execute(
        update(models.Organization)
        .where(models.Organization.id == str(org_id))
        .values(role=role)
    )
    await db.commit()


async def set_service_account(
    db: AsyncSession, org_id: UUID4 | str, sa: str
) -> None:
    await db.execute(
        update(models.Organization)
        .where(models.Organization.id == str(org_id))
        .values(service_account=sa)
    )
    await db.commit()


async def has_name_been_already_taken(db: AsyncSession, name: str) -> bool:
    result = await db.execute(
        select(models.Organization.id).where(models.Organization.name == name)
    )
    return result.scalar() is not None


async def update_counts(db: AsyncSession, org_id: UUID4) -> None:
    from reliably_app import execution, experiment

    await db.execute(
        update(models.Organization)
        .where(models.Organization.id == str(org_id))
        .values(
            executions_count=select(func.count(execution.models.Execution.id))
            .where(execution.models.Execution.org_id == str(org_id))
            .scalar_subquery()
        )
    )

    await db.execute(
        update(models.Organization)
        .where(models.Organization.id == str(org_id))
        .values(
            running_executions_count=select(
                func.count(execution.models.Execution.id)
            )
            .where(execution.models.Execution.org_id == str(org_id))
            .where(
                execution.models.Execution.user_state["current"].astext
                == "running"
            )
            .scalar_subquery()
        )
    )

    await db.execute(
        update(models.Organization)
        .where(models.Organization.id == str(org_id))
        .values(
            experiments_count=select(
                func.count(experiment.models.Experiment.id)
            )
            .where(experiment.models.Experiment.org_id == str(org_id))
            .scalar_subquery()
        )
    )
    await db.commit()


async def update_executions_count(db: AsyncSession, org_id: UUID4) -> None:
    from reliably_app import execution

    await db.execute(
        update(models.Organization)
        .where(models.Organization.id == str(org_id))
        .values(
            executions_count=select(func.count(execution.models.Execution.id))
            .where(execution.models.Execution.org_id == str(org_id))
            .scalar_subquery()
        )
    )
    await db.commit()


async def update_running_executions_count(
    db: AsyncSession, org_id: UUID4
) -> None:
    from reliably_app import execution

    await db.execute(
        update(models.Organization)
        .where(models.Organization.id == str(org_id))
        .values(
            running_executions_count=select(
                func.count(execution.models.Execution.id)
            )
            .where(execution.models.Execution.org_id == str(org_id))
            .where(
                execution.models.Execution.user_state["current"].astext
                == "running"
            )
            .scalar_subquery()
        )
    )
    await db.commit()


async def update_experiments_count(db: AsyncSession, org_id: UUID4) -> None:
    from reliably_app import experiment

    await db.execute(
        update(models.Organization)
        .where(models.Organization.id == str(org_id))
        .values(
            experiments_count=select(
                func.count(experiment.models.Experiment.id)
            )
            .where(experiment.models.Experiment.org_id == str(org_id))
            .scalar_subquery()
        )
    )
    await db.commit()


async def update_users_count(db: AsyncSession, org_id: UUID4) -> None:
    await db.execute(
        update(models.Organization)
        .where(models.Organization.id == str(org_id))
        .values(
            users_count=select(func.count(models.OrganizationUsers.user_id))
            .where(models.OrganizationUsers.org_id == str(org_id))
            .where(models.OrganizationUsers.agent.is_(False))
            .scalar_subquery()
        )
    )
    await db.commit()


async def update_consumed_minutes(
    db: AsyncSession, org_id: UUID4, consumed_minutes: int
) -> None:
    result = await db.execute(
        select(models.Organization.consumed_minutes)
        .where(models.Organization.id == str(org_id))
        .with_for_update()
    )
    current = result.scalar_one()
    total = current + consumed_minutes

    await db.execute(
        update(models.Organization)
        .where(models.Organization.id == str(org_id))
        .values(consumed_minutes=total)
    )
    await db.commit()


async def create_invitation(
    db: AsyncSession, org_id: UUID4
) -> models.OrganizationInvitation:
    db_invite = models.OrganizationInvitation(org_id=str(org_id))
    db.add(db_invite)
    await db.commit()
    return cast(models.OrganizationInvitation, db_invite)


async def get_invitation_by_link_hash(
    db: AsyncSession,
    link_hash: bytes,
) -> models.OrganizationInvitation | None:
    result = await db.execute(
        select(models.OrganizationInvitation)
        .where(models.OrganizationInvitation.link_hash == link_hash)
        .where(models.OrganizationInvitation.active.is_(True))
    )
    return result.scalars().first()


async def get_active_invitation(
    db: AsyncSession,
    org_id: UUID4,
) -> models.OrganizationInvitation | None:
    result = await db.execute(
        select(models.OrganizationInvitation)
        .where(models.OrganizationInvitation.org_id == str(org_id))
        .where(models.OrganizationInvitation.active.is_(True))
    )
    return result.scalars().first()


async def disable_invitation(
    db: AsyncSession,
    org_id: UUID4,
    invite_id: UUID4,
) -> None:
    await db.execute(
        update(models.OrganizationInvitation)
        .where(models.OrganizationInvitation.id == str(invite_id))
        .where(models.OrganizationInvitation.org_id == str(org_id))
        .values(active=False)
    )
    await db.commit()


async def reset_consumed_minutes(db: AsyncSession, org_id: UUID4) -> None:
    await db.execute(
        update(models.Organization)
        .where(models.Organization.id == str(org_id))
        .values(consumed_minutes=0)
    )
    await db.commit()
