import redis.asyncio as redis
from src.config.config import config

redis_client = redis.Redis(
    host=config.redis.HOST,
    port=config.redis.PORT,
    password=config.redis.PASSWORD,
    decode_responses=True,
)