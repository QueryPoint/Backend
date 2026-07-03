
from unittest.mock import AsyncMock, MagicMock
import pytest
from src.core.ws.manager import ConnectionManager

@pytest.mark.asyncio
async def test_manager_returns_false_for_unknown_connection():
    assert await ConnectionManager().send("missing",{"x":1}) is False

@pytest.mark.asyncio
async def test_manager_send_and_remove():
    manager=ConnectionManager();ws=MagicMock();ws.send_json=AsyncMock()
    manager.add("id",ws)
    assert await manager.send("id",{"ok":True}) is True
    ws.send_json.assert_awaited_once()
    manager.remove("id")
    assert await manager.send("id",{}) is False
