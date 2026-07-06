
import pytest
from src.core.ws import state
from src.core.ws.enums import WSStatus

pytestmark = pytest.mark.unit

@pytest.mark.asyncio
async def test_connection_and_status_keys_are_user_scoped(fake_redis, user_id, other_user_id, monkeypatch):
    monkeypatch.setattr(state, "redis_service", type("R", (), {"set":fake_redis.set,"get":fake_redis.get,"delete":fake_redis.delete})())
    await state.set_connection(user_id, "conn")
    await state.set_status(user_id, WSStatus.processing)
    calls = [str(c) for c in fake_redis.set.await_args_list]
    assert str(user_id) in calls[0] and str(other_user_id) not in calls[0]
    assert "processing" in calls[1]

@pytest.mark.asyncio
async def test_delete_connection_and_status(fake_redis, user_id, monkeypatch):
    monkeypatch.setattr(state, "redis_service", type("R", (), {"set":fake_redis.set,"get":fake_redis.get,"delete":fake_redis.delete})())
    await state.delete_connection(user_id)
    await state.delete_status(user_id)
    assert fake_redis.delete.await_count == 2
