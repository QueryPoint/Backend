import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.rabbitmq import to_llm

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_publish_prompt_serializes_expected_payload(monkeypatch, user_id):
    publish = AsyncMock()
    channel = MagicMock(default_exchange=MagicMock(publish=publish))
    # channel is a read-only property.  Patch its backing field instead.
    monkeypatch.setattr(to_llm.rabbitmq_client, "_channel", channel)

    await to_llm.publish_prompt(user_id, "hello", "doc-id")

    message = publish.await_args.args[0]
    payload = json.loads(message.body.decode())
    assert payload == {
        "type": "prompt",
        "user_id": str(user_id),
        "prompt": "hello",
        "doc": "doc-id",
    }


@pytest.mark.asyncio
async def test_publish_delete_serializes_expected_payload(monkeypatch, user_id):
    publish = AsyncMock()
    channel = MagicMock(default_exchange=MagicMock(publish=publish))
    monkeypatch.setattr(to_llm.rabbitmq_client, "_channel", channel)

    await to_llm.publish_delete(user_id)

    payload = json.loads(publish.await_args.args[0].body.decode())
    assert payload == {"type": "delete", "user_id": str(user_id)}
