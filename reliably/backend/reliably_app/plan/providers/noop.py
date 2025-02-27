from reliably_app import deployment
from reliably_app.plan import schemas

__all__ = ["delete_plan", "execute_plan"]


async def execute_plan(
    plan: schemas.Plan, dep: deployment.schemas.Deployment
) -> None:  # noqa
    pass


async def delete_plan(
    plan: schemas.Plan, dep: deployment.schemas.Deployment
) -> None:
    pass


async def suspend_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
) -> None:
    pass


async def resume_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
) -> None:
    pass
