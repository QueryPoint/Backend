from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.repositories.user import UserRepository
from src.core.db.repositories.documents import DocRepository
from src.core.db.database import get_session


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user = UserRepository(self.session)
        self.document = DocRepository(self.session)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def close(self) -> None:
        await self.session.close()


@asynccontextmanager
async def get_uow() -> AsyncIterator[UnitOfWork]:
    async with get_session() as session:
        uow = UnitOfWork(session)
        try:
            yield uow
            await uow.commit()
        except Exception:
            await uow.rollback()
            raise