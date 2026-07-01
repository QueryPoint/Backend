from typing import AsyncIterator

from src.core.db.uow import get_uow
from src.api.auth.service import AuthService


async def get_auth_service() -> AsyncIterator[AuthService]:
    async with get_uow() as uow:
        yield AuthService(uow)