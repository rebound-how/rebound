import logging
import math
import sys
from datetime import datetime, timezone
from typing import Annotated, Any, Dict, List, cast

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from reliably_app import (
    account,
    agent,
    experiment,
    notification,
    organization,
    plan,
    series,
)
from reliably_app.dependencies.auth import with_user_in_org
from reliably_app.dependencies.database import SessionLocal, get_db
from reliably_app.dependencies.org import valid_org
from reliably_app.execution import crud, models, schemas, validators
from reliably_app.observability import span

__all__ = ["extend_routers"]

logger = logging.getLogger("reliably_app")
router = APIRouter()
org_exec_router = APIRouter()
plan_exec_router = APIRouter()


def extend_routers(web: APIRouter, api: APIRouter) -> None:
    web.include_router(
        router,
        prefix="/experiments/{exp_id}/executions",
        include_in_schema=False,
    )
    api.include_router(router, prefix="/experiments/{exp_id}/executions")

    web.include_router(
        org_exec_router, prefix="/executions", include_in_schema=False
    )
    api.include_router(org_exec_router, prefix="/executions")


@router.get(
    "",
    response_model=schemas.Executions,
    status_code=status.HTTP_200_OK,
    description="Retrieve all exzeriment's executions",
    tags=["Execution"],
    summary="Retrieve all exzeriment's executions",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Executions,
            "description": "Ok Response",
        }
    },
)
async def index(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    db: AsyncSession = Depends(get_db),
    exp: experiment.models.Experiment = Depends(
        experiment.validators.valid_experiment
    ),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, int | List[models.Execution]]:
    count = int(exp.executions_count or 0)

    if not count:
        return {"count": 0, "items": []}

    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    if (limit * page) > count:
        return {"count": count, "items": []}

    executions = await crud.get_executions_by_experiment(
        db,
        exp.id,  # type: ignore
        page=limit * page,
        limit=limit,
    )

    return {"count": count, "items": executions}


@router.post(
    "",
    response_model=schemas.Execution,
    status_code=status.HTTP_201_CREATED,
    description="Add a new execution",
    tags=["Execution"],
    summary="Add a new execution",
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.Execution,
            "description": "Created",
        }
    },
)
async def create(
    exec: schemas.ExecutionCreate,
    user: account.models.User = Depends(with_user_in_org),
    exp: experiment.models.Experiment = Depends(
        experiment.validators.valid_experiment
    ),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Execution:
    in_plan = False
    if exec.plan_id:
        p = await plan.crud.get_plan(db, exec.plan_id, status=None)
        if p and str(exp.id) not in p.definition["experiments"]:
            raise HTTPException(status.HTTP_400_BAD_REQUEST)
        in_plan = True

    fix_start_date(cast(Dict[str, Any], exec.result))
    async with SessionLocal() as session:
        user_id: str | None = str(user.id)
        agt = await agent.crud.get_from_user_id(
            db,
            org.id,  # type: ignore
            user.id,  # type: ignore
        )
        if agt:
            actual_user = await account.crud.get_user(
                db,
                agt.from_user_id,  # type: ignore
            )
            if actual_user:
                user_id = str(actual_user.id)

        x = await crud.create_execution(
            session,
            org.id,  # type: ignore
            exp.id,  # type: ignore
            user_id,  # type: ignore
            exec,
        )

    async with SessionLocal() as session:
        await organization.crud.update_executions_count(
            session,
            org.id,  # type: ignore
        )

    async with SessionLocal() as session:
        await experiment.crud.update_executions_count(
            session,
            org.id,  # type: ignore
            exp.id,  # type: ignore
        )

    if in_plan:
        try:
            async with SessionLocal() as session:
                await plan.crud.update_executions_count(
                    session,
                    org.id,  # type: ignore
                    str(exec.plan_id),  # type: ignore
                )

            async with SessionLocal() as session:
                await plan.crud.update_last_running_execution_info(
                    session,
                    org.id,  # type: ignore
                    str(exec.plan_id),  # type: ignore
                    x.id,  # type: ignore
                    x.created_date.isoformat(),
                )
        except Exception:
            logger.error("Failed to update plan stats", exc_info=True)

    return x


@router.put(
    "/{exec_id}/results",
    status_code=status.HTTP_200_OK,
    description="Set execution results",
    tags=["Execution"],
    summary="Set execution results",
    responses={
        status.HTTP_200_OK: {
            "description": "Updated",
        }
    },
)
async def replace(
    result: schemas.ExecutionCreate,
    exp: experiment.models.Experiment = Depends(
        experiment.validators.valid_experiment
    ),
    exec: models.Execution = Depends(validators.valid_execution_without_log),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    if not await crud.is_execution_linked_to_experiment(
        db,
        exp.id,  # type: ignore
        exec.id,  # type: ignore
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    fix_start_date(
        cast(Dict[str, Any], result.result), cast(datetime, exec.created_date)
    )
    await crud.update_execution_result(
        db,
        org.id,  # type: ignore
        exp.id,  # type: ignore
        exec.id,  # type: ignore
        result,
    )


@router.get(
    "/{exec_id}/state",
    response_model=schemas.ExecutionTerminateState
    | schemas.ExecutionPauseState
    | schemas.ExecutionPendingState
    | schemas.ExecutionRunningState
    | schemas.ExecutionFinishedState
    | schemas.ExecutionResumeState,
    status_code=status.HTTP_200_OK,
    description="Get execution user state",
    tags=["Execution"],
    summary="Get execution user state",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ExecutionTerminateState
            | schemas.ExecutionPauseState
            | schemas.ExecutionPendingState
            | schemas.ExecutionRunningState
            | schemas.ExecutionFinishedState
            | schemas.ExecutionResumeState,
            "description": "Ok",
        }
    },
)
async def get_user_state(
    request: Request,
    exp: experiment.models.Experiment = Depends(
        experiment.validators.valid_experiment
    ),
    exec: models.Execution = Depends(
        validators.valid_execution_without_log_nor_journal
    ),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any] | None:
    if not await crud.is_execution_linked_to_experiment(
        db,
        exp.id,  # type: ignore
        exec.id,  # type: ignore
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return await crud.get_user_state(db, org.id, exec.id)  # type: ignore


@router.put(
    "/{exec_id}/state",
    status_code=status.HTTP_200_OK,
    description="Set execution user state",
    tags=["Execution"],
    summary="Set execution user state",
    responses={
        status.HTTP_200_OK: {
            "description": "Updated",
        }
    },
)
async def set_user_state(
    state: Annotated[
        schemas.ExecutionTerminateState
        | schemas.ExecutionPauseState
        | schemas.ExecutionPendingState
        | schemas.ExecutionRunningState
        | schemas.ExecutionFinishedState
        | schemas.ExecutionResumeState,
        Body(embed=False),
    ],
    request: Request,
    user: account.models.User = Depends(with_user_in_org),
    exp: experiment.models.Experiment = Depends(
        experiment.validators.valid_experiment
    ),
    exec: models.Execution = Depends(
        validators.valid_execution_without_log_nor_journal
    ),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    attrs = {
        "org_id": str(org.id),
        "exp_id": str(exp.id),
        "exec_id": str(exec.id),
        "user_id": str(user.id),
        "state": state.current,
    }
    with span("set-execution-state", attributes=attrs):
        if not await crud.is_execution_linked_to_experiment(
            db,
            exp.id,  # type: ignore
            exec.id,  # type: ignore
        ):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        logger.debug(f"Storing execution {str(exec.id)} state: {state.current}")

        if state.current in ("terminate", "pause", "resume"):
            state.user = schemas.ExecutionStateUser(  # type: ignore
                name=user.username, id=str(user.id)
            )

        async with SessionLocal() as session:
            await crud.set_user_state(
                session,
                org.id,  # type: ignore
                exec.id,  # type: ignore
                state.model_dump(),
            )

        async with SessionLocal() as session:
            await organization.crud.update_running_executions_count(
                session,
                org.id,  # type: ignore
            )

        if (
            state.current in ("pending", "running", "finished")
            and state.plan_id
        ):
            async with SessionLocal() as session:
                await plan.crud.update_executions_count(
                    session,
                    org.id,  # type: ignore
                    state.plan_id,
                )

        if state.current == "finished":
            try:
                async with SessionLocal() as session:
                    x = await crud.get_execution(
                        session,
                        exec.id,  # type: ignore
                    )
                    if x:
                        journal = cast(Dict, x.result)

                        start = cast(datetime, x.created_date).replace(
                            tzinfo=timezone.utc
                        )
                        end = datetime.now(tz=timezone.utc)
                        fix_end_date(journal, end)
                        flag_modified(x, "result")
                        duration = math.ceil(
                            (end - start).total_seconds() / 60.0
                        )

                async with SessionLocal() as session:
                    await organization.crud.update_consumed_minutes(
                        session,
                        org.id,  # type: ignore
                        duration,
                    )

                await series.crud.experiment.consume_execution(
                    org.id,  # type: ignore
                    exp.id,  # type: ignore
                    exec.id,  # type: ignore
                    exec.plan_id,  # type: ignore
                    journal,
                )

                await series.crud.org.consume_execution(
                    org.id,  # type: ignore
                    exp.id,  # type: ignore
                    exec.id,  # type: ignore
                    journal,
                )

                async with SessionLocal() as session:
                    await plan.crud.update_last_completed_execution_info(
                        session,
                        org.id,  # type: ignore
                        state.plan_id,  # type: ignore
                        exec.id,  # type: ignore
                        state.finished_on.isoformat(),
                    )

                async with SessionLocal() as db:
                    p = await plan.crud.get_plan(db, exec.plan_id, status=None)  # type: ignore
                    if p:
                        p = plan.schemas.Plan.model_validate(  # type: ignore
                            p, from_attributes=True
                        )

                        summary = await experiment.crud.get_experiment_summary(
                            db,
                            org.id,  # type: ignore
                            exp.id,  # type: ignore
                        )

                        if state.status == "completed":
                            await notification.tasks.notify_event(
                                notification.schemas.PlanEvent(
                                    org_id=org.id,
                                    kind="plan-phases",
                                    plan=p,
                                    deployment=None,
                                    experiment=summary,
                                    execution_id=exec.id,
                                    status=state.status,
                                )
                            )
                        else:
                            await notification.tasks.notify_event(
                                notification.schemas.PlanEvent(
                                    org_id=org.id,
                                    kind="plan-phases",
                                    plan=p,
                                    deployment=None,
                                    experiment=summary,
                                    execution_id=exec.id,
                                    deviated=journal.get("deviated"),
                                    status=state.status,
                                )
                            )

            except Exception:
                logger.error("Failed to update plan stats", exc_info=True)


@router.get(
    "/{exec_id}",
    response_model=schemas.Execution,
    status_code=status.HTTP_200_OK,
    description="Retrieve an execution in an organinzation",
    tags=["Execution"],
    summary="Retrieve an execution",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Execution,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Token was not found",
        },
    },
)
async def get(
    exec: models.Execution = Depends(validators.valid_execution_without_log),
) -> models.Execution:
    return exec


@router.get(
    "/{exec_id}/log",
    status_code=status.HTTP_200_OK,
    description="Retrieve an execution's log",
    tags=["Execution"],
    summary="Retrieve an execution's log",
    responses={
        status.HTTP_200_OK: {
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Execution was not found",
        },
    },
)
async def get_log(
    exec: models.Execution = Depends(validators.valid_execution),
) -> PlainTextResponse:
    return PlainTextResponse(content=cast(str, exec.log))


@router.get(
    "/{exec_id}/results",
    response_model=schemas.ChaosToolkitResults,
    status_code=status.HTTP_200_OK,
    description="Retrieve an execution's result",
    tags=["Execution"],
    summary="Retrieve an execution's result",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ChaosToolkitResults,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Execution was not found",
        },
    },
)
async def get_result(
    exec: models.Execution = Depends(validators.valid_execution),
) -> Dict[str, Any]:
    return cast(Dict[str, Any], exec.result)


@router.delete(
    "/{exec_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Delete the given execution",
    tags=["Execution"],
    summary="Delete the given execution",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
    },
)
async def delete(
    exp: experiment.models.Experiment = Depends(
        experiment.validators.valid_experiment
    ),
    exec: models.Execution = Depends(validators.valid_execution),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await series.crud.experiment.drop_execution(
            org.id,  # type: ignore
            exp.id,  # type: ignore
            exec.id,  # type: ignore
            exec.result,  # type: ignore
        )
    finally:
        await crud.delete_execution(db, exec.id)  # type: ignore

    async with SessionLocal() as session:
        await experiment.crud.update_executions_count(
            session,
            org.id,  # type: ignore
            exp.id,  # type: ignore
        )

    async with SessionLocal() as session:
        await organization.crud.update_executions_count(
            session,
            org.id,  # type: ignore
        )

    async with SessionLocal() as session:
        await organization.crud.update_running_executions_count(
            session,
            org.id,  # type: ignore
        )

    if exec.plan_id:
        async with SessionLocal() as session:
            p = await plan.crud.get_plan(
                session,
                exec.plan_id,  # type: ignore
                status=None,
            )
            if p:
                await plan.crud.update_executions_count(
                    session,
                    org.id,  # type: ignore
                    p.id,  # type: ignore
                )


@org_exec_router.get(
    "",
    response_model=schemas.Executions,
    status_code=status.HTTP_200_OK,
    description="Retrieve all organization's executions",
    tags=["Execution"],
    summary="Retrieve all organization's executions",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Executions,
            "description": "Ok Response",
        }
    },
)
async def index_by_org(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, int | List[models.Execution]]:
    count = int(org.executions_count)

    if not count:
        return {"count": 0, "items": []}

    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    if (limit * page) > count:
        return {"count": count, "items": []}

    executions = await crud.get_executions_by_org(
        db,
        org.id,  # type: ignore
        page=limit * page,
        limit=limit,
    )
    return {"count": count, "items": executions}


################################################################################
# Private functions
################################################################################
def fix_date(
    target: str, journal: Dict[str, Any], with_date: datetime | None = None
) -> None:
    reset_it_with: datetime | None = None

    if not with_date:
        reset_it_with = datetime.now(tz=timezone.utc)
    else:
        reset_it_with = with_date.replace(tzinfo=timezone.utc)

    journal[target] = reset_it_with.replace(tzinfo=None).isoformat()


def fix_start_date(
    journal: Dict[str, Any], created_date: datetime | None = None
) -> None:
    return fix_date("start", journal, created_date)


def fix_end_date(journal: Dict[str, Any], end_date: datetime) -> None:
    return fix_date("end", journal, end_date)
