from uuid import UUID

from fastapi import Response

from src.core.db.uow import UnitOfWork
from src.api.exc.auth import UsernameTaken, Unauthed, UserNotFound
from src.api.auth.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)
from src.api.auth.cookies import clear_auth_cookies
from src.core.db.dto.userDTO import UserDTO, UserProfileDTO, StatusDTO, AuthDTO


class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def register(self, username: str, password: str) -> UserDTO:
        if await self.uow.user.get_by_username(username):
            raise UsernameTaken

        result = await self.uow.user.create(
            username=username,
            password_hash=await hash_password(password),
        )

        return UserDTO(user_id=result.user_id, username=result.username)

    async def login(self, username: str, password: str) -> AuthDTO:
        user = await self.uow.user.get_by_username(username)
        if not user:
            raise Unauthed

        password_hash = await self.uow.user.get_password_hash(username)
        if not await verify_password(password, password_hash):
            raise Unauthed

        access_token = create_access_token(user.user_id)
        refresh_token = create_refresh_token(user.user_id)
        return AuthDTO(
            user_id=user.user_id,
            username=user.username,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh(self, refresh_token: str) -> str:
        if not refresh_token:
            raise Unauthed

        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise Unauthed

        return create_access_token(UUID(payload["sub"]))

    async def logout(self, response: Response) -> StatusDTO:
        clear_auth_cookies(response)
        return StatusDTO(status="logged_out")

    async def get_profile(self, access_token: str, limit: int, offset: int) -> UserProfileDTO:
        user_id = self._get_user_id(access_token)

        user = await self.uow.user.get_by_id(user_id)
        if not user:
            raise Unauthed

        documents = await self.uow.document.list(user_id, limit, offset)

        return UserProfileDTO(
            user_id=user.user_id,
            username=user.username,
            documents=documents,
        )

    def _get_user_id(self, access_token: str) -> UUID:
        if not access_token:
            raise Unauthed

        payload = decode_token(access_token)
        if not payload or payload.get("type") != "access":
            raise Unauthed

        return UUID(payload["sub"])