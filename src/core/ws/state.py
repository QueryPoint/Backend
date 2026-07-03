from uuid import UUID

from src.core.redis.redis_service import redis_service
from src.core.ws.enums import WSStatus

def _conn_key(user_id: UUID) -> str:
    return f"ws:user:{user_id}:connection_id"

def _status_key(user_id: UUID) -> str:
    return f"ws:user:{user_id}:status"

async def set_connection(user_id: UUID, connection_id: str) -> None:
    await redis_service.set(_conn_key(user_id), connection_id)

async def get_connection(user_id: UUID) -> str | None:
    return await redis_service.get(_conn_key(user_id))

async def delete_connection(user_id: UUID) -> None:
    await redis_service.delete(_conn_key(user_id))

async def set_status(user_id: UUID, status: WSStatus) -> None:
    await redis_service.set(_status_key(user_id), status.value)

async def get_status(user_id: UUID) -> str | None:
    return await redis_service.get(_status_key(user_id))

async def delete_status(user_id: UUID) -> None:
    await redis_service.delete(_status_key(user_id))