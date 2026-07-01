from uuid import UUID
from typing import Optional, AsyncIterator

from fastapi import Cookie

from src.core.db.uow import get_uow
from src.api.auth.service import AuthService
from src.api.auth.security import decode_token
from src.api.exc.auth import Unauthed


async def get_auth_service() -> AsyncIterator[AuthService]:
    async with get_uow() as uow:
        yield AuthService(uow)

async def get_current_user_id(access_token: Optional[str] = Cookie(default=None)) -> UUID:
    if not access_token:
        raise Unauthed
    payload = decode_token(access_token)
    if not payload or payload.get("type") != "access":
        raise Unauthed
    return UUID(payload["sub"])