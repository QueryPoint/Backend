
from unittest.mock import AsyncMock, MagicMock
import pytest
from src.api.ws.router import _handle_prompt
from src.core.ws.enums import WSStatus

pytestmark=pytest.mark.websocket

@pytest.mark.asyncio
async def test_prompt_blocks_when_other_prompt_processing(monkeypatch,user_id):
    ws=MagicMock();ws.send_json=AsyncMock()
    monkeypatch.setattr("src.api.ws.router.get_status",AsyncMock(return_value=WSStatus.processing.value))
    await _handle_prompt(ws,user_id,{"type":"prompt","prompt":"hello"})
    ws.send_json.assert_awaited_once_with({"type":"error","data":"Prompt already processing"})

@pytest.mark.asyncio
async def test_prompt_blocks_when_chat_blocked(monkeypatch,user_id):
    ws=MagicMock();ws.send_json=AsyncMock()
    monkeypatch.setattr("src.api.ws.router.get_status",AsyncMock(return_value=WSStatus.blocked.value))
    await _handle_prompt(ws,user_id,{"type":"prompt","prompt":"hello"})
    ws.send_json.assert_awaited_once_with({"type":"error","data":"Chat blocked, reset required"})

@pytest.mark.asyncio
async def test_prompt_sets_processing_and_publishes(monkeypatch,user_id):
    ws=MagicMock();ws.send_json=AsyncMock()
    set_status=AsyncMock(); publish=AsyncMock()
    monkeypatch.setattr("src.api.ws.router.get_status",AsyncMock(return_value=WSStatus.idle.value))
    monkeypatch.setattr("src.api.ws.router.set_status",set_status)
    monkeypatch.setattr("src.api.ws.router.publish_prompt",publish)
    await _handle_prompt(ws,user_id,{"type":"prompt","prompt":"hello","doc":"d"})
    set_status.assert_awaited_once_with(user_id,WSStatus.processing)
    publish.assert_awaited_once_with(user_id=user_id,prompt="hello",doc="d")
