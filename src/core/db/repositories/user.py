from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models.user import User
from src.core.db.dto.dto import UserDTO


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> UserDTO | None:
        result = await self.session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if not user:
            return None
        return UserDTO(user_id=user.user_id, username=user.username)

    async def get_password_hash(self, username: str) -> str | None:
        result = await self.session.execute(select(User.password_hash).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> UserDTO | None:
        result = await self.session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        return UserDTO(user_id=user.user_id, username=user.username)

    async def create(self, username: str, password_hash: str) -> UserDTO:
        user = User(username=username, password_hash=password_hash)
        self.session.add(user)
        await self.session.flush()
        return UserDTO(user_id=user.user_id, username=user.username)