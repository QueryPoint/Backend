import json
from uuid import UUID

import aio_pika

from src.core.rabbitmq.client import rabbitmq_client, BACK_TO_LLM_QUEUE

async def _publish(payload: dict) -> None:
    message = aio_pika.Message(
        body=json.dumps(payload).encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )
    await rabbitmq_client.channel.default_exchange.publish(
        message, routing_key=BACK_TO_LLM_QUEUE
    )

async def publish_prompt(user_id: UUID, prompt: str, doc: str | None) -> None:
    await _publish({
        "type": "prompt",
        "user_id": str(user_id),
        "prompt": prompt,
        "doc": doc,
    })

async def publish_delete(user_id: UUID) -> None:
    await _publish({
        "type": "delete",
        "user_id": str(user_id),
    })