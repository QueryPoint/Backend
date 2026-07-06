import json

from aio_pika.abc import AbstractIncomingMessage

from src.core.rabbitmq.client import rabbitmq_client, LLM_TO_BACK_QUEUE
from src.core.ws.manager import connection_manager
from src.core.ws import state
from src.core.ws.enums import WSStatus

async def _handle_message(message: AbstractIncomingMessage) -> None:
    async with message.process():
        payload = json.loads(message.body.decode())

        user_id = payload["user_id"]
        warning = payload.get("warning", 0)

        if warning >= 100:
            await state.set_status(user_id, WSStatus.blocked)
        else:
            await state.set_status(user_id, WSStatus.idle)

        connection_id = await state.get_connection(user_id)
        if not connection_id:
            return

        await connection_manager.send(connection_id, payload)
        if warning >= 100:
            await connection_manager.send(connection_id, {
                "type": "error",
                "data": "Контекст исчерпан, сбросьте чат",
            })

async def start_consumer() -> None:
    queue = await rabbitmq_client.channel.declare_queue(LLM_TO_BACK_QUEUE, durable=True)
    await queue.consume(_handle_message)