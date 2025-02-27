import logging

from starlette.requests import Request

from reliably_app import deployment
from reliably_app.database import SessionLocal
from reliably_app.observability import span
from reliably_app.plan import crud, errors, schemas
from reliably_app.plan.providers import cli, container, github, k8s, noop, rbly
from reliably_app.plan.providers.utils import (
    get_deployment_from_plan,
    get_environment_from_plan,
    get_integrations_from_plan,
)

__all__ = ["delete_plan", "schedule_plan"]

logger = logging.getLogger("reliably_app")


async def schedule_plan(
    plan: schemas.Plan, org_id: str, user_id: str, request: Request | None
) -> None:
    attrs = {"plan_id": str(plan.id), "org_id": org_id, "user_id": user_id}
    with span("plan-create-schedule", attributes=attrs):
        try:
            dep = await get_deployment_from_plan(plan)
        except deployment.errors.DeploymentNotFoundError:
            async with SessionLocal() as db:
                dep_id = plan.definition.deployment.deployment_id
                await crud.set_status(
                    db,
                    plan.id,
                    schemas.PlanStatus.creation_error,
                    error=f"deployment '{dep_id}' not found",
                )
            raise

        # do not schedule from here when the deployment is carried by the agent
        if plan.definition.schedule.via_agent:
            async with SessionLocal() as db:
                await crud.mark_schedulable(
                    db, org_id, plan.id, dep.definition.type
                )
            return None

        integrations = await get_integrations_from_plan(plan)

        try:
            try:
                env = await get_environment_from_plan(plan)
            except Exception as x:
                raise errors.PlanFailedError(
                    str(plan.id),
                    f"failed to fetch environment: {str(x)}",
                ) from x

            match dep.definition.type:  # noqa
                case "github":
                    await github.execute_plan(plan, dep, org_id)
                case "reliably_cloud":
                    await rbly.execute_plan(
                        plan, dep, env, integrations, org_id, user_id, request
                    )
                case "container":
                    await container.execute_plan(
                        plan,
                        dep,
                        env,
                        integrations,
                        org_id,
                        user_id,
                    )
                case "reliably_cli":
                    await cli.execute_plan(plan, dep, env, org_id, user_id)  # type: ignore
                case "k8s_job":
                    await k8s.execute_plan(
                        plan, dep, env, integrations, org_id, user_id
                    )
                case "noop":  # noqa
                    await noop.execute_plan(plan, dep)
        except errors.PlanFailedError as x:
            async with SessionLocal() as db:
                await crud.set_status(
                    db,
                    plan.id,
                    schemas.PlanStatus.creation_error,
                    error=x.message,
                )
            raise
        except Exception as x:
            m = str(x)
            logger.error(
                f"Failed to create plan '{plan.id}': {m}", exc_info=True
            )

            if dep.definition.type == "reliably_cloud":
                m = ""

            async with SessionLocal() as db:
                dep_id = plan.definition.deployment.deployment_id
                await crud.set_status(
                    db,
                    plan.id,
                    schemas.PlanStatus.creation_error,
                    error=f"failed to create plan '{plan.id}': {m}",
                )
            raise
        else:
            async with SessionLocal() as db:
                await crud.set_status(db, plan.id, schemas.PlanStatus.created)


async def delete_plan(plan: schemas.Plan, org_id: str) -> None:
    attrs = {"plan_id": str(plan.id), "org_id": org_id}
    with span("plan-delete-schedule", attributes=attrs):
        async with SessionLocal() as db:
            await crud.set_status(db, plan.id, schemas.PlanStatus.deleting)

        try:
            dep = await get_deployment_from_plan(plan)
        except deployment.errors.DeploymentNotFoundError:
            dep_id = plan.definition.deployment.deployment_id
            logger.warning(
                f"Plan {plan.id} was referencing deployment {dep_id} "
                f"which does not exist. Some resources may remain undeleted."
            )
            async with SessionLocal() as db:
                await crud.set_status(db, plan.id, schemas.PlanStatus.deleted)
            return None

        if plan.definition.schedule.via_agent:
            async with SessionLocal() as db:
                await crud.set_status(db, plan.id, schemas.PlanStatus.deleted)
            return None

        try:
            try:
                env = await get_environment_from_plan(plan)
            except Exception as x:
                raise errors.PlanFailedError(
                    str(plan.id),
                    f"failed to fetch environment: {str(x)}",
                ) from x

            match dep.definition.type:
                case "github":
                    await github.delete_plan(plan, dep, org_id)
                case "reliably_cloud":
                    await rbly.delete_plan(plan, dep, env)
                case "container":
                    await container.delete_plan(plan, dep, env)
                case "k8s_job":
                    await k8s.delete_plan(plan, dep, env)
                case "reliably_cli":
                    await cli.delete_plan(plan, dep)
                case "noop":  # noqa
                    await noop.delete_plan(plan, dep)
        except errors.PlanFailedError as e:
            logger.error(f"Failed to delete plan '{plan.id}'", exc_info=True)
            async with SessionLocal() as db:
                await crud.set_status(
                    db,
                    plan.id,
                    schemas.PlanStatus.deleted,
                    error=e.message,
                )
            raise
        except Exception as x:
            m = str(x)
            logger.error(
                f"Failed to delete plan '{plan.id}': {m}", exc_info=True
            )

            if dep.definition.type == "reliably_cloud":
                m = ""

            async with SessionLocal() as db:
                dep_id = plan.definition.deployment.deployment_id
                await crud.set_status(
                    db,
                    plan.id,
                    schemas.PlanStatus.deleted,
                    error=f"failed to delete plan '{plan.id}': {m}",
                )
            raise
        else:
            async with SessionLocal() as db:
                await crud.set_status(db, plan.id, schemas.PlanStatus.deleted)


async def suspend_plan(
    plan: schemas.Plan,
    org_id: str,
    user_id: str,
) -> None:
    attrs = {"plan_id": str(plan.id), "org_id": org_id, "user_id": user_id}
    with span("plan-suspend-schedule", attributes=attrs):
        async with SessionLocal() as db:
            await crud.set_status(db, plan.id, schemas.PlanStatus.suspending)

        try:
            dep = await get_deployment_from_plan(plan)
        except deployment.errors.DeploymentNotFoundError:
            dep_id = plan.definition.deployment.deployment_id
            logger.warning(
                f"Plan {plan.id} was referencing deployment {dep_id} "
                f"which does not exist."
            )
            async with SessionLocal() as db:
                await crud.set_status(
                    db, plan.id, schemas.PlanStatus.suspend_error
                )
            return None

        try:
            match dep.definition.type:
                case "github":
                    await github.suspend_plan(plan, dep)
                case "reliably_cloud":
                    await rbly.suspend_plan(plan, dep)
                case "container":
                    await container.suspend_plan(plan, dep)
                case "k8s_job":
                    await k8s.suspend_plan(plan, dep)
                case "reliably_cli":
                    await cli.suspend_plan(plan, dep)
                case "noop":  # noqa
                    await noop.suspend_plan(plan, dep)
        except errors.PlanFailedError as e:
            logger.error(f"Failed to suspend plan '{plan.id}'", exc_info=True)
            async with SessionLocal() as db:
                await crud.set_status(
                    db,
                    plan.id,
                    schemas.PlanStatus.suspend_error,
                    error=e.message,
                )
            raise
        except Exception as x:
            m = str(x)
            logger.error(
                f"Failed to suspend plan '{plan.id}': {m}", exc_info=True
            )

            if dep.definition.type == "reliably_cloud":
                m = ""

            async with SessionLocal() as db:
                dep_id = plan.definition.deployment.deployment_id
                await crud.set_status(
                    db,
                    plan.id,
                    schemas.PlanStatus.suspend_error,
                    error=f"failed to suspend plan '{plan.id}': {m}",
                )
            raise
        else:
            async with SessionLocal() as db:
                await crud.set_status(db, plan.id, schemas.PlanStatus.suspended)


async def resume_plan(
    plan: schemas.Plan,
    org_id: str,
    user_id: str,
) -> None:
    attrs = {"plan_id": str(plan.id), "org_id": org_id, "user_id": user_id}
    with span("plan-resume-schedule", attributes=attrs):
        async with SessionLocal() as db:
            await crud.set_status(db, plan.id, schemas.PlanStatus.resuming)

        try:
            dep = await get_deployment_from_plan(plan)
        except deployment.errors.DeploymentNotFoundError:
            dep_id = plan.definition.deployment.deployment_id
            logger.warning(
                f"Plan {plan.id} was referencing deployment {dep_id} "
                f"which does not exist."
            )
            async with SessionLocal() as db:
                await crud.set_status(
                    db, plan.id, schemas.PlanStatus.resuming_error
                )
            return None

        try:
            match dep.definition.type:
                case "github":
                    await github.resume_plan(plan, dep)
                case "reliably_cloud":
                    await rbly.resume_plan(plan, dep)
                case "container":
                    await container.resume_plan(plan, dep)
                case "k8s_job":
                    await k8s.resume_plan(plan, dep)
                case "reliably_cli":
                    await cli.resume_plan(plan, dep)
                case "noop":  # noqa
                    await noop.resume_plan(plan, dep)
        except errors.PlanFailedError as e:
            logger.error(f"Failed to suspend plan '{plan.id}'", exc_info=True)
            async with SessionLocal() as db:
                await crud.set_status(
                    db,
                    plan.id,
                    schemas.PlanStatus.resuming_error,
                    error=e.message,
                )
            raise
        except Exception as x:
            m = str(x)
            logger.error(
                f"Failed to resume plan '{plan.id}': {m}", exc_info=True
            )

            if dep.definition.type == "reliably_cloud":
                m = ""

            async with SessionLocal() as db:
                dep_id = plan.definition.deployment.deployment_id
                await crud.set_status(
                    db,
                    plan.id,
                    schemas.PlanStatus.resuming_error,
                    error=f"failed to suspend plan '{plan.id}': {m}",
                )
            raise
        else:
            async with SessionLocal() as db:
                await crud.set_status(db, plan.id, schemas.PlanStatus.created)
