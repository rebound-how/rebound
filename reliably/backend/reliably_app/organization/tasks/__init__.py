import importlib.resources
import logging
import socket
import tempfile
from pathlib import Path

import docker
import docker.errors
import orjson
from kubernetes import config, client
from pydantic import UUID4
from tzlocal import get_localzone_name

import reliably_app
from reliably_app import (
    deployment,
    environment,
    series,
    token,
)
from reliably_app.config import get_settings
from reliably_app.database import SessionLocal
from reliably_app.organization import crud, models, schemas
from reliably_app.organization.tasks import gcp, local


__all__ = [
    "create_resources",
    "create_default_organizations",
    "populate_organization",
]
logger = logging.getLogger("reliably_app")


async def create_resources(org: models.Organization) -> None:
    settings = get_settings()
    strategy = settings.DEPLOYMENT_STRATEGY

    logger.debug(f"Creating resources with strategy: {strategy}")

    match strategy:
        case "gcp":
            return await gcp.create_cloud_resources(org)
        case "local":
            return await local.create_local_resources(org)


async def create_default_organizations(org_names: list[str]) -> None:
    for org_name in org_names:
        async with SessionLocal() as db:
            if await crud.has_name_been_already_taken(db, org_name) is False:
                logger.debug(f"Creating organization '{org_name}'")
                org = await crud.create_org(
                    db, schemas.OrganizationCreate(name=org_name)
                )

                async with SessionLocal() as db:
                    await series.crud.org.initialize_org_series(
                        org.id  # type: ignore
                    )


async def populate_organization(org_id: UUID4, user_id: UUID4) -> None:
    experiments = await populate_default_experiments(org_id)
    deployments = await populate_default_deployments(org_id)
    environments = await populate_default_environments(org_id)
    # tokens = await populate_default_tokens(org_id, user_id)
    await populate_default_templates(org_id)
    plans = await populate_default_plans(
        org_id, experiments, deployments, environments
    )
    await schedule_default_plans(org_id, user_id, plans)


async def populate_default_experiments(
    org_id: UUID4,
) -> list["reliably_app.experiment.models.Experiment"]:
    from reliably_app import experiment

    with importlib.resources.path(
        "reliably_app.data.experiments", "login-page-availability.json"
    ) as p:
        definition = orjson.loads(p.read_bytes())

        hostname = f"http://{socket.gethostname()}:8090"
        definition["configuration"]["base_url"]["default"] = hostname
        content = orjson.dumps(definition).decode("utf-8")

        x = experiment.schemas.ExperimentCreate(definition=content)

        async with SessionLocal() as db:
            xp = await experiment.crud.create_experiment(db, org_id, x)

        await series.crud.experiment.initialize_experiment_series(
            org_id,
            xp.id,  # type: ignore
            definition,
        )

        await series.crud.experiment.consume_experiment(
            org_id,
            definition,
        )

        await series.crud.org.consume_experiment(
            org_id,
            definition,
        )

        async with SessionLocal() as d:
            await crud.update_experiments_count(
                d,
                org_id,
            )

        return [xp]


async def populate_default_deployments(
    org_id: UUID4,
) -> list[deployment.models.Deployment]:
    settings = get_settings()

    deployments = []

    async with SessionLocal() as db:
        d = deployment.schemas.DeploymentCreate(
            name="CLI Runner (Managed)",
            definition=deployment.schemas.DeploymentCLIDefinition(
                type="reliably_cli",
                mode="managed",
                py_version="3.13",
            ),
        )
        d = await deployment.crud.create_deployment(db, org_id, d)  # type: ignore
        deployments.append(d)

    async with SessionLocal() as db:
        d = deployment.schemas.DeploymentCreate(
            name="CLI Runner (Manual)",
            definition=deployment.schemas.DeploymentCLIDefinition(
                type="reliably_cli"
            ),
        )
        d = await deployment.crud.create_deployment(db, org_id, d)  # type: ignore
        deployments.append(d)

    try:
        docker.from_env()
    except docker.errors.DockerException:
        # docker isn't available
        pass
    else:
        if settings.FEATURE_CONTAINER_DEPLOYMENT:
            async with SessionLocal() as db:
                d = deployment.schemas.DeploymentCreate(
                    name="Container Runner",
                    definition=deployment.schemas.DeploymentContainerDefinition(
                        type="container",
                        image="ghcr.io/rebound-how/reliably-job:latest",
                        working_dir=tempfile.gettempdir(),
                        volumes=None,
                    ),
                )
                d = await deployment.crud.create_deployment(db, org_id, d)  # type: ignore
                deployments.append(d)

    k8s_client_configured = False
    try:
        config.load_kube_config()
        k8s_client_configured = True
    except config.config_exception.ConfigException:
        try:
            config.load_incluster_config()
            k8s_client_configured = True
        except config.config_exception.ConfigException:
            try:
                sa_dir = settings.K8S_SERVICE_ACCOUNT_DIR
                if sa_dir and sa_dir.exists():
                    token_filename = sa_dir / Path("token")
                    cert_filename = sa_dir / Path("ca.crt")

                    config.incluster_config.InClusterConfigLoader(
                        token_filename=token_filename,
                        cert_filename=cert_filename,
                        try_refresh_token=True,
                    ).load_and_set()
                    k8s_client_configured = True
            except Exception:
                pass

    if k8s_client_configured:
        if settings.FEATURE_K8S_JOB_DEPLOYMENT:
            ns = settings.K8S_DEFAULT_JOB_NS
            image = settings.K8S_DEFAULT_JOB_IMAGE

            v1 = client.CoreV1Api()

            create_deployment = True
            try:
                v1.create_namespace(
                    body=client.V1Namespace(
                        metadata=client.V1ObjectMeta(name=ns),
                    )
                )
            except client.ApiException as x:
                create_deployment == x.status in [409]
            except Exception:
                logger.debug(
                    "Failed to communicate with Kubernetes API Server",
                    exc_info=True,
                )
            else:
                try:
                    v1.create_namespaced_service_account(
                        body=client.V1ServiceAccount(
                            automount_service_account_token=False,
                            metadata=client.V1ObjectMeta(
                                name="reliably-job",
                                labels={
                                    "app.kubernetes.io/name": "reliably-job"
                                },
                            ),
                        ),
                        namespace=ns,
                    )
                except client.ApiException as x:
                    create_deployment == x.status in [409]
                except Exception:
                    create_deployment = False
                    logger.debug(
                        "Failed to communicate with Kubernetes API Server",
                        exc_info=True,
                    )

                if create_deployment:
                    async with SessionLocal() as db:
                        d = deployment.schemas.DeploymentCreate(
                            name="Kubernetes Runner",
                            definition=deployment.schemas.DeploymentKubernetesJobDefinition(
                                type="k8s_job",
                                image=image,
                                namespace=ns,
                                use_in_cluster_credentials=False,
                            ),
                        )
                        d = await deployment.crud.create_deployment(
                            db,
                            org_id,
                            d,  # type: ignore
                        )
                        deployments.append(d)

    return deployments  # type: ignore


async def populate_default_environments(
    org_id: UUID4,
) -> list[environment.models.Environment]:
    settings = get_settings()
    async with SessionLocal() as db:
        e = environment.schemas.EnvironmentCreate(
            name="Generic",
            envvars=environment.schemas.EnvironmentVars(
                root=[
                    environment.schemas.EnvironmentVar(
                        var_name="BASE_URL", value=settings.RELIABLY_DOMAIN
                    )
                ]
            ),
            secrets=environment.schemas.EnvironmentSecrets(root=[]),
            used_for="plan",
        )
        return [await environment.crud.create_environment(db, org_id, e)]


async def populate_default_plans(
    org_id: UUID4,
    experiments: list["reliably_app.experiment.models.Experiment"],
    deployments: list[deployment.models.Deployment],
    environments: list[environment.models.Environment],
) -> list["reliably_app.plan.models.Plan"]:
    from reliably_app import plan

    plans: list[plan.models.Plan] = []

    async with SessionLocal() as db:
        p = plan.schemas.PlanCreate(
            title="Check Login Page is Available Every Hour",
            environment=plan.schemas.PlanReliablyEnvironment(
                provider="reliably_cloud", id=environments[0].id
            ),
            deployment=plan.schemas.PlanDeployment(
                deployment_id=deployments[0].id,
                deployment_type=deployments[0].definition.get("type"),
            ),
            schedule=plan.schemas.PlanScheduleCron(
                type="cron",
                via_agent=False,
                pattern="0,10,20,30,40,50 9-17 * * 1-5",
                timezone=get_localzone_name(),
            ),
            integrations=[],
            experiments=[experiments[0].id],
        )
        plans.append(await plan.crud.create_plan(db, org_id, p))

    async with SessionLocal() as db:
        p = plan.schemas.PlanCreate(
            title="Check Login Page is Available Once",
            environment=plan.schemas.PlanReliablyEnvironment(
                provider="reliably_cloud", id=environments[0].id
            ),
            deployment=plan.schemas.PlanDeployment(
                deployment_id=deployments[0].id,
                deployment_type=deployments[0].definition.get("type"),
            ),
            schedule=plan.schemas.PlanScheduleNow(
                type="now",
            ),
            integrations=[],
            experiments=[experiments[0].id],
        )
        plans.append(await plan.crud.create_plan(db, org_id, p))

    for pl in plans:
        async with SessionLocal() as db:
            await plan.crud.set_status(
                db,
                pl.id,  # type: ignore
                plan.schemas.PlanStatus.created,
            )

    return plans


async def populate_default_tokens(
    org_id: UUID4, user_id: UUID4
) -> list[token.models.Token]:
    async with SessionLocal() as db:
        t = token.schemas.TokenCreate(
            name="Generated Token",
        )
        return [await token.crud.create_token(db, org_id, user_id, t)]


async def schedule_default_plans(
    org_id: UUID4, user_id: UUID4, plans: list["reliably_app.plan.models.Plan"]
) -> None:
    # prevent circular import
    from reliably_app import plan
    from reliably_app.plan.providers import schedule_plan

    for p in plans:
        await schedule_plan(
            plan.schemas.Plan.model_validate(p, from_attributes=True),
            str(org_id),
            str(user_id),
            request=None,
        )


async def populate_default_templates(
    org_id: UUID4,
) -> list["reliably_app.catalog.models.Catalog"]:
    # prevent circular import
    from reliably_app import catalog

    async with SessionLocal() as db:
        templates = []
        for r in importlib.resources.files(
            "reliably_app.data.templates"
        ).iterdir():
            if not r.name.endswith(".json"):
                continue

            c = catalog.schemas.CatalogItemCreate.model_validate_json(
                r.read_bytes()
            )

            templates.append(await catalog.crud.create_catalog(db, org_id, c))

    return templates
