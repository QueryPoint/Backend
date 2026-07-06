import hashlib
from uuid import UUID

from src.core.db.uow import UnitOfWork
from src.core.redis.redis_service import redis_service
from src.core.elasticsearch.es_servise import elastic_service

SEARCH_CACHE_TTL = 300

class SearchService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def search(self, user_id: UUID, query: str, limit: int = 10, offset: int = 0) -> list[dict]:
        if offset == 0:
            await self.uow.search_history.create(user_id=user_id, query=query)

        key = self._cache_key(user_id=user_id, query=query, limit=limit, offset=offset)
        redis_result = await redis_service.get_json(key=key)
        if redis_result is not None:
            return redis_result

        es_result = await elastic_service.search(user_id=user_id, query=query, limit=limit, offset=offset)

        await redis_service.set_json(key=key, value=es_result, ttl=SEARCH_CACHE_TTL)
        return es_result

    async def delete(self, user_id: UUID) -> None:
        await self.uow.search_history.delete_by_user(user_id=user_id)

    @staticmethod
    def _cache_key(user_id: UUID, query: str, limit: int = 10, offset: int = 0) -> str:
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return f"search:{user_id}:{query_hash}:{limit}:{offset}"



