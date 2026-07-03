import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel

from src.config.config import config

BACK_TO_LLM_QUEUE = "back_to_llm"
LLM_TO_BACK_QUEUE = "llm_to_back"


class RabbitMQClient:
    def __init__(self) -> None:
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractRobustChannel | None = None

    async def connect(self) -> None:
        if self._connection is not None:
            return
        self._connection = await aio_pika.connect_robust(config.rabbitmq.url)
        self._channel = await self._connection.channel()
        await self._channel.declare_queue(BACK_TO_LLM_QUEUE, durable=True)
        await self._channel.declare_queue(LLM_TO_BACK_QUEUE, durable=True)

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None
            self._channel = None

    @property
    def channel(self) -> AbstractRobustChannel:
        if self._channel is None:
            raise RuntimeError("RabbitMQ not connected")
        return self._channel


rabbitmq_client = RabbitMQClient()