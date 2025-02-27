import logging
from typing import Any, Dict, List, cast

from starlette.requests import Request

from reliably_app import deployment, environment, experiment, integration
from reliably_app.database import SessionLocal
from reliably_app.plan import errors, schemas

__all__ = [
    "get_deployment_from_plan",
    "get_experiment",
    "get_experiment_direct_url",
    "get_environment_from_plan",
    "get_integrations_from_plan",
]
logger = logging.getLogger("reliably_app")


async def get_experiment(plan: schemas.Plan) -> Dict[str, Any]:  # noqa
    exp_id = plan.definition.experiments[0]

    async with SessionLocal() as db:
        x = await experiment.crud.get_experiment(db, exp_id)
        if not x:
            raise errors.PlanFailedError(
                str(plan.id), f"Experiment {exp_id} could not be found"
            )

        return cast(Dict, x.definition)


def get_experiment_direct_url(
    plan: schemas.Plan, org_id: str, request: Request
) -> str:
    exp_id = plan.definition.experiments[0]
    return str(
        request.url_for("get_raw_experiment", exp_id=str(exp_id), org_id=org_id)
    )


async def get_deployment_from_plan(
    plan: schemas.Plan,
) -> deployment.schemas.Deployment:  # noqa
    async with SessionLocal() as db:
        dep = await deployment.crud.get_deployment(
            db, plan.definition.deployment.deployment_id
        )
        if not dep:  # noqa
            raise deployment.errors.DeploymentNotFoundError()

        return deployment.schemas.Deployment.model_validate(
            dep, from_attributes=True
        )


async def get_environment_from_plan(
    plan: schemas.Plan,
) -> environment.schemas.Environment | None:  # noqa
    if not plan.definition.environment:
        return None

    if not plan.definition.environment.id:
        return None

    async with SessionLocal() as db:
        env = await environment.crud.get_environment(
            db, plan.definition.environment.id
        )
        if not env:  # noqa
            raise environment.errors.EnvironmentNotFoundError()

        return environment.schemas.Environment.model_validate(
            env, from_attributes=True
        )


async def get_integrations_from_plan(
    plan: schemas.Plan,
) -> List[integration.schemas.IntegrationFull]:  # noqa
    if not plan.definition.integrations:
        return []

    async with SessionLocal() as db:
        integrations = await integration.crud.get_many_integrations(
            db, plan.org_id, plan.definition.integrations
        )

        results = []
        for i in integrations:
            e = await environment.crud.get_environment(
                db,
                i.environment_id,  # type: ignore
            )
            if not e:
                logger.warning(
                    f"Integration {str(i.id)} uses an environment that is "
                    f"missing: {str(i.environment_id)}"
                )
                continue

            results.append(
                integration.schemas.IntegrationFull(
                    id=i.id,
                    org_id=plan.org_id,
                    name=i.name,
                    provider=i.provider,
                    environment=environment.schemas.Environment.model_validate(
                        e, from_attributes=True
                    ),
                )
            )

        return results


async def get_plan_max_duration(org_id: str) -> int:
    return 3600
