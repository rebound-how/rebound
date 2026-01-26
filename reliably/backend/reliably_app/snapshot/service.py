import logging
import sys
from typing import Any, Dict, List, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import (
    account,
    agent,
    environment,
    integration,
    job,
    organization,
)
from reliably_app.database import SessionLocal
from reliably_app.dependencies.auth import with_user_in_org
from reliably_app.dependencies.database import get_db
from reliably_app.dependencies.org import valid_org
from reliably_app.snapshot import crud, models, schemas, tasks, validators
from reliably_app.snapshot.tasks import query_snapshot

__all__ = ["extend_routers"]

logger = logging.getLogger("reliably_app")
router = APIRouter()


def extend_routers(web: APIRouter, api: APIRouter) -> None:
    web.include_router(router, prefix="/snapshots", include_in_schema=False)
    api.include_router(router, prefix="/snapshots")


@router.get(
    "",
    response_model=schemas.Snapshots,
    status_code=status.HTTP_200_OK,
    description="Retrieve all organization's systems snapshots",
    tags=["Snapshot"],
    summary="Retrieve all organization's snapshots",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Snapshots,
            "description": "Ok Response",
        }
    },
)
async def index(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, int | List[models.JSONB]]:
    snapshot = await crud.get_latest_snapshot(db, org.id)  # type: ignore

    if not snapshot:
        return {"count": 0, "items": []}

    page = max((page or 1) - 1, 0) * 10
    limit = limit or 10

    count = len(snapshot.snapshot["resources"])
    resources = snapshot.snapshot["resources"][page : page + limit]

    return {"count": count, "items": resources}  # type: ignore


@router.get(
    "/search",
    response_model=schemas.Snapshots,
    status_code=status.HTTP_200_OK,
    description="Search through snapshot resources' names",
    tags=["Snapshot"],
    summary="Search through snapshot resources' names",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Snapshots,
            "description": "Ok Response",
        },
    },
)
async def search_resources_by_name(
    pattern: str = Query(min_length=1),
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, int | List[models.JSONB]]:
    snapshot = await crud.get_latest_snapshot(db, org.id)  # type: ignore
    if not snapshot:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    page = max((page or 1) - 1, 0) * 10
    limit = limit or 10

    count = await crud.count_resources_by_name(
        db,
        org.id,  # type: ignore
        snapshot.id,  # type: ignore
        pattern,
    )

    resources = (
        await crud.search_resources_by_name(
            db,
            org.id,  # type: ignore
            snapshot.id,  # type: ignore
            pattern,
            page=page,
            limit=limit,
        )
        or []
    )

    return {"count": count, "items": resources}  # type: ignore


@router.get(
    "/latest",
    response_model=schemas.Snapshot | None,
    status_code=status.HTTP_200_OK,
    description="Get the most recent snapshot",
    tags=["Snapshot"],
    summary="Get the most recent snapshot",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Snapshot | None,
            "description": "Ok Response",
        }
    },
)
async def latest_snaphot(
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> models.Snapshot | None:
    return await crud.get_latest_snapshot(db, org.id)  # type: ignore


@router.get(
    "/config",
    response_model=schemas.SnapshotConfig | None,
    status_code=status.HTTP_200_OK,
    description="Get the current snapshot configuration",
    tags=["Snapshot"],
    summary="Get the current snapshot configuration",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.SnapshotConfig | None,
            "description": "Ok Response",
        }
    },
)
async def current_config(
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> dict[str, environment.models.Environment] | None:
    current_job = await job.crud.get_most_recent_job_by_type(
        db,
        org.id,  # type: ignore
        "snapshot",
    )
    if not current_job:
        return None

    int_id = current_job.definition["integration_id"]
    intg = await integration.crud.get_integration(db, int_id)  # type: ignore
    if not intg:
        return None

    env = await environment.crud.get_environment(db, intg.environment_id)  # type: ignore
    if not env:
        return None

    return {"env": env, "name": intg.name, "integration_id": str(int_id)}  # type: ignore


@router.get(
    "/refresh",
    name="refresh_resources",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Refresh resources now",
    tags=["Snapshot"],
    summary="Refresh resources now",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Resource was not found",
        },
    },
)
async def refresh_snapshot(
    org: organization.models.Organization = Depends(valid_org),
    user: account.models.User = Depends(with_user_in_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    j = await job.crud.get_most_recent_job_by_type(db, org.id, "snapshot")  # type: ignore
    if not j:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    j = job.schemas.Job.model_validate(j)  # type: ignore

    try:
        await tasks.schedule_discovery(
            j.definition.integration_id,
            j.org_id,  # type: ignore
            user.id,  # type: ignore
            None,
        )
    except Exception:
        logger.error(
            f"User {user.id} requested to refresh snapshot job {j.id} which "
            "failed",
            exc_info=True,
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get(
    "/resources/data",
    name="get_resource_data",
    response_model=schemas.ResourceCandidates,
    status_code=status.HTTP_200_OK,
    description="Retrieve candidates from a given jsonpath query",
    tags=["Snapshot"],
    summary="Retrieve candidates from a given jsonpath query",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ResourceCandidates,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Resource was not found",
        },
    },
)
async def get_data(
    query: str,
    params: dict[str, str] | None = None,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> dict[str, int | list[dict[str, str]]]:
    candidates = await crud.get_resource_data(db, org.id, query, params) or []  # type: ignore

    if candidates:
        c = candidates[0]  # type: ignore
        if isinstance(c, str):
            candidates = sorted(set(candidates))
        elif isinstance(c, dict):
            converted_candidates = []
            for c in candidates:
                converted_candidates.extend([f"{k}={v}" for k, v in c.items()])  # type: ignore
            candidates = sorted(set(converted_candidates))

    return {
        "count": len(candidates),
        "items": [{"val": c, "label": c} for c in candidates],
    }


@router.get(
    "/current",
    response_model=schemas.ResourceValue,
    status_code=status.HTTP_200_OK,
    description="Query the latest snapshot",
    tags=["Snapshot"],
    summary="Query the latest snapshot",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ResourceValue,
            "description": "Ok Response",
        }
    },
)
async def current_resource_value(
    path: str = Query(),
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> List[Any]:
    snapshot = await crud.get_latest_snapshot(db, org.id)  # type: ignore
    if not snapshot:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return query_snapshot(
        schemas.Snapshot.model_validate(snapshot, from_attributes=True), path
    )


@router.post(
    "",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    description="Add a new snapshot configuration",
    tags=["Snapshot"],
    summary="Add a new snapshot configuration",
    responses={
        status.HTTP_201_CREATED: {
            "model": None,
            "description": "Created",
        },
    },
)
async def create(
    create: schemas.SnapshotCreate,
    user: account.models.User = Depends(with_user_in_org),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    if create.agent_id:
        await agent.validators.valid_agent(create.agent_id, org, db)

    int_id = create.integration_id

    intg = await integration.crud.get_integration(db, int_id)
    if not intg:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    task_def = job.schemas.JobCreate(
        user_id=user.id,
        pattern=create.pattern,
        definition=job.schemas.JobSnapshot(
            type="snapshot",
            integration_id=intg.id,
            agent_id=create.agent_id,
        ),
    )

    await job.crud.enqueue_job(org.id, task_def)  # type: ignore


@router.put(
    "/from/{integration_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Update a snapshot configuration froman integration",
    tags=["Snapshot"],
    summary="Update a snapshot configuration froman integration",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Created",
        },
    },
)
async def update_config(
    env: environment.schemas.EnvironmentCreate,
    intg: integration.models.Integration = Depends(
        integration.validators.valid_integration
    ),
    user: account.models.User = Depends(with_user_in_org),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    intr = integration.schemas.Integration.model_validate(
        intg, from_attributes=True
    )

    async with SessionLocal() as d:
        await integration.crud.set_integration_name(
            d,
            intg.org_id,  # type: ignore
            intg.id,  # type: ignore
            env.name,
        )

    async with SessionLocal() as d:
        await environment.crud.set_environment(d, intr.environment_id, env)  # type: ignore

    async with SessionLocal() as d:
        j = await job.crud.get_most_recent_job_by_type(db, org.id, "snapshot")  # type: ignore
        pattern = j.pattern  # type: ignore
        agent_id = j.definition.get("agent_id")  # type: ignore

        if j:
            await job.crud.remove_job(d, j.org_id, j.id)  # type: ignore

    task_def = job.schemas.JobCreate(
        user_id=user.id,
        pattern=pattern,
        definition=job.schemas.JobSnapshot(
            type="snapshot",
            integration_id=intg.id,
            agent_id=agent_id,
        ),
    )

    await job.crud.enqueue_job(org.id, task_def)  # type: ignore


@router.get(
    "/{snapshot_id}",
    response_model=schemas.Snapshot,
    status_code=status.HTTP_200_OK,
    description="Retrieve a snapshot in an organization",
    tags=["Snapshot"],
    summary="Retrieve a snapshot",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Snapshot,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Snapshot was not found",
        },
    },
)
async def get_snapshot(
    snapshot: models.Snapshot = Depends(validators.valid_snapshot),
) -> models.Snapshot:
    return snapshot


@router.delete(
    "/{snapshot_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Delete the given snapshot",
    tags=["Snapshot"],
    summary="Delete the given snapshot",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
    },
)
async def delete(
    snapshot_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    if not await crud.does_snapshot_belong_to_org(
        db,
        org.id,  # type: ignore
        snapshot_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await crud.delete_snapshot(db, snapshot_id)


@router.get(
    "/resources/{resource_id}",
    name="get_resource",
    response_model=schemas.Resource,
    status_code=status.HTTP_200_OK,
    description="Retrieve a resource in an organization",
    tags=["Snapshot"],
    summary="Retrieve a resource",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Resource,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Resource was not found",
        },
    },
)
async def get_single_resource(
    resource_id: str,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    r = await crud.get_snapshot_resource(db, org.id, resource_id)  # type: ignore
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return cast(dict[str, Any], r["resource"])


@router.get(
    "/resources/{resource_id}/previous",
    name="get_previous_resource",
    response_model=schemas.Resource,
    status_code=status.HTTP_200_OK,
    description="Retrieve the previous version of a resource",
    tags=["Snapshot"],
    summary="Retrieve the previous version of a resource",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Resource,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Resource was not found",
        },
    },
)
async def get_previous_resource(
    resource_id: str,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    r = await crud.get_snapshot_previous_resource(db, org.id, resource_id)  # type: ignore
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return r


@router.get(
    "/resources/{resource_id}/links",
    name="get_resource_links",
    response_model=schemas.LinkInfos,
    status_code=status.HTTP_200_OK,
    description="Retrieve link information for the resource",
    tags=["Snapshot"],
    summary="Retrieve link information for the resource",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.LinkInfos,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Resource was not found",
        },
    },
)
async def get_resource_links(
    resource_id: str,
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=50),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> dict[str, int | list[dict[str, Any]]]:
    resource = await crud.get_snapshot_resource(db, org.id, resource_id)  # type: ignore
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    page = max((page or 1) - 1, 0) * 10
    limit = limit or 10

    links = resource["resource"].get("links", [])
    count = len(links)
    if not count:
        return {"count": 0, "items": []}

    linked = links[page : page + limit]
    if not linked:
        return {"count": count, "items": []}

    link_ids = list(set([str(l["id"]) for l in linked]))  # noqa: E741

    r = await crud.get_snapshot_resource_links_info(
        db,
        org.id,  # type: ignore
        resource["id"],
        link_ids,
    )

    return {"count": count, "items": r}
