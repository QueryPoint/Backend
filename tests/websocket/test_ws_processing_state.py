
from unittest.mock import AsyncMock
import pytest
from src.api.ws.router import _handle_delete
from src.core.ws.enums import WSStatus

@pytest.mark.asyncio
async def test_delete_resets_status_to_idle(monkeypatch,user_id):
    publish=AsyncMock();status=AsyncMock()
    monkeypatch.setattr("src.api.ws.router.publish_delete",publish)
    monkeypatch.setattr("src.api.ws.router.set_status",status)
    await _handle_delete(user_id)
    publish.assert_awaited_once_with(user_id)
    status.assert_awaited_once_with(user_id,WSStatus.idle)
