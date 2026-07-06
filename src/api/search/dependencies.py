from typing import AsyncIterator

from src.core.db.uow import get_uow
from src.api.search.service import SearchService

async def get_search_service() -> AsyncIterator[SearchService]:
    async with get_uow() as uow:
        yield SearchService(uow)