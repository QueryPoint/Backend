
from uuid import uuid4
from unittest.mock import AsyncMock
import pytest
from src.api.search.service import SearchService, SEARCH_CACHE_TTL

pytestmark = pytest.mark.unit

@pytest.mark.asyncio
async def test_search_saves_history_and_returns_cache(fake_uow, user_id, monkeypatch):
    service = SearchService(fake_uow)
    monkeypatch.setattr("src.api.search.service.redis_service.get_json", AsyncMock(return_value=[{"cached":True}]))
    monkeypatch.setattr("src.api.search.service.elastic_service.search", AsyncMock())
    result = await service.search(user_id, "базы данных")
    assert result == [{"cached":True}]
    fake_uow.search_history.create.assert_awaited_once_with(user_id=user_id, query="базы данных")

@pytest.mark.asyncio
async def test_search_calls_es_and_caches_cache_miss(fake_uow, user_id, monkeypatch):
    service = SearchService(fake_uow)
    es = AsyncMock(return_value=[{"result": 1}])
    set_json = AsyncMock()
    monkeypatch.setattr("src.api.search.service.redis_service.get_json", AsyncMock(return_value=None))
    monkeypatch.setattr("src.api.search.service.elastic_service.search", es)
    monkeypatch.setattr("src.api.search.service.redis_service.set_json", set_json)
    assert await service.search(user_id, "sql") == [{"result":1}]
    es.assert_awaited_once_with(user_id=user_id, query="sql")
    assert set_json.await_args.kwargs["ttl"] == SEARCH_CACHE_TTL

def test_cache_key_is_deterministic_and_user_isolated(user_id, other_user_id):
    a = SearchService._cache_key(user_id, "sql")
    assert a == SearchService._cache_key(user_id, "sql")
    assert a != SearchService._cache_key(other_user_id, "sql")
    assert a != SearchService._cache_key(user_id, "postgres")

@pytest.mark.asyncio
async def test_delete_history_only_for_given_user(fake_uow, user_id):
    await SearchService(fake_uow).delete(user_id)
    fake_uow.search_history.delete_by_user.assert_awaited_once_with(user_id=user_id)
