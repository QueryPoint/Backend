import asyncio
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from uuid import UUID

from src.config.config import config


async def hash_password(password: str) -> str:
    hashed = await asyncio.to_thread(bcrypt.hashpw, password.encode(), bcrypt.gensalt())
    return hashed.decode()


async def verify_password(password: str, password_hash: str) -> bool:
    return await asyncio.to_thread(bcrypt.checkpw, password.encode(), password_hash.encode())


def create_access_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=config.jwt.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "type": "access", "exp": expire}
    return jwt.encode(payload, config.jwt.SECRET_KEY, algorithm=config.jwt.ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=config.jwt.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "type": "refresh", "exp": expire}
    return jwt.encode(payload, config.jwt.SECRET_KEY, algorithm=config.jwt.ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, config.jwt.SECRET_KEY, algorithms=[config.jwt.ALGORITHM])
    except jwt.PyJWTError:
        return None