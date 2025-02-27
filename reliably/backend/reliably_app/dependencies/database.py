from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app.database import SessionLocal

__all__ = ["get_db"]


async def get_db() -> AsyncIterator[AsyncSession]:
    """
    Yields a session to access to the database and open an explicit transaction.

    Close the session upon completion.
    """
    async with SessionLocal() as db:
        async with db.begin():
            yield db
