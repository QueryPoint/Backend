"""Real RabbitMQ -> backend consumer -> Redis state -> WebSocket routing flow."""
from __future__ import annotations

import asyncio
import json
from urllib.parse import urlparse

import aio_pika
import pytest
import websocket

from ._helpers import qa_settings as _settings_fixture

pytestmark = pytest.mark.integration


def _ws_url(backend_url: str) -> str:
    parsed = urlparse(backend_url)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    return f"{scheme}://{parsed.netloc}/api/v1/ws"


@pytest.mark.asyncio
async def test_rabbitmq_result_is_delivered_to_matching_websocket(qa_users, qa_settings):
    user = await qa_users()
    access_token = user["client"].cookies.get("access_token")
    assert access_token, "Login did not return access_token cookie"

    ws = await asyncio.to_thread(
        websocket.create_connection,
        _ws_url(qa_settings.backend_url),
        cookie=f"access_token={access_token}",
        timeout=15,
    )
    try:
        payload = {"user_id": str(user["user_id"]), "type": "answer", "answer": "qa-rabbitmq-ws-token"}
        connection = await aio_pika.connect_robust(qa_settings.rabbitmq_url)
        try:
            channel = await connection.channel()
            await channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(payload).encode("utf-8")),
                routing_key="llm_to_back",
            )
        finally:
            await connection.close()

        raw = await asyncio.to_thread(ws.recv)
        received = json.loads(raw)
        assert received == payload
    finally:
        await asyncio.to_thread(ws.close)
