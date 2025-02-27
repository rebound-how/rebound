from fastapi import Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import experiment
from reliably_app.dependencies.database import get_db
from reliably_app.execution import crud, models

__all__ = [
    "valid_execution",
    "valid_execution_without_log",
    "valid_execution_without_log_nor_journal",
]


async def valid_execution(
    exec_id: UUID4,
    exp: experiment.models.Experiment = Depends(
        experiment.validators.valid_experiment
    ),
    db: AsyncSession = Depends(get_db),
) -> models.Execution:
    if not await crud.is_execution_linked_to_experiment(
        db,
        exp.id,  # type: ignore
        exec_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    exec = await crud.get_execution(db, exec_id)
    if not exec:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)  # noqa

    return exec


async def valid_execution_without_log(
    exec_id: UUID4,
    exp: experiment.models.Experiment = Depends(
        experiment.validators.valid_experiment
    ),
    db: AsyncSession = Depends(get_db),
) -> Row:
    if not await crud.is_execution_linked_to_experiment(
        db,
        exp.id,  # type: ignore
        exec_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    exec = await crud.get_execution_without_log(db, exec_id)
    if not exec:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)  # noqa

    return exec


async def valid_execution_without_log_nor_journal(
    exec_id: UUID4,
    exp: experiment.models.Experiment = Depends(
        experiment.validators.valid_experiment
    ),
    db: AsyncSession = Depends(get_db),
) -> Row:
    if not await crud.is_execution_linked_to_experiment(
        db,
        exp.id,  # type: ignore
        exec_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    exec = await crud.get_execution_without_log_nor_journal(db, exec_id)
    if not exec:  # pragma: no cover
        raise HTTPException(status.HTTP_404_NOT_FOUND)  # noqa

    return exec
