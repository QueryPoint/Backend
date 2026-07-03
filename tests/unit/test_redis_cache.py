
import pytest
from src.core.redis.redis_service import RedisService

pytestmark = pytest.mark.unit

@pytest.mark.asyncio
async def test_set_get_delete_exists(fake_redis):
    service = RedisService(fake_redis)
    await service.set("k", "v", ttl=12)
    fake_redis.set.assert_awaited_once_with("k", "v", ex=12)
    fake_redis.get.return_value = "v"
    assert await service.get("k") == "v"
    await service.delete("k")
    fake_redis.delete.assert_awaited_once_with("k")

@pytest.mark.asyncio
async def test_json_round_trip_and_empty_value(fake_redis):
    service = RedisService(fake_redis)
    await service.set_json("k", [{"x":"тест"}], ttl=300)
    fake_redis.get.return_value = '[{"x": "тест"}]'
    assert await service.get_json("k") == [{"x":"тест"}]
    fake_redis.get.return_value = None
    assert await service.get_json("k") is None
