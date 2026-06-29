from typing import Optional
from fastapi import APIRouter, Response, Cookie, Depends

from src.api.auth.service import AuthService
from src.api.auth.dependencies import get_auth_service
from src.api.auth.schemas import (
    UserRegisterRequest, UserLoginRequest,
    UserResponse, UserProfileResponse, StatusResponse,
)
from src.api.auth.cookies import set_auth_cookies, set_access_cookie

router = APIRouter(tags=["auth"])


@router.post("/registration", response_model=UserResponse, status_code=201)
async def registration(
    payload: UserRegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    user = await service.register(payload.username, payload.password)
    return UserResponse(user_id=str(user.user_id), username=user.username)


@router.post("/login", response_model=UserResponse, status_code=200)
async def login(
    payload: UserLoginRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    result = await service.login(payload.username, payload.password)
    set_auth_cookies(response, result.access_token, result.refresh_token)
    return UserResponse(user_id=str(result.user_id), username=result.username)


@router.post("/refresh", response_model=StatusResponse, status_code=200)
async def refresh(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None),
    service: AuthService = Depends(get_auth_service),
) -> StatusResponse:
    access_token = await service.refresh(refresh_token)
    set_access_cookie(response, access_token)
    return StatusResponse(status="session_refreshed")


@router.post("/logout", response_model=StatusResponse, status_code=200)
async def logout(
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> StatusResponse:
    result = await service.logout(response)
    return StatusResponse(status=result.status)


@router.get("/me", response_model=UserProfileResponse, status_code=200)
async def me(
    access_token: Optional[str] = Cookie(default=None),
    service: AuthService = Depends(get_auth_service),
) -> UserProfileResponse:
    profile = await service.get_profile(access_token)
    return UserProfileResponse(user_id=str(profile.user_id), username=profile.username)