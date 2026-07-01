from typing import Optional
from fastapi import APIRouter, Response, Cookie, Depends, Query

from src.api.auth.service import AuthService
from src.api.auth.dependencies import get_auth_service
from src.api.auth.schemas import (
    UserRegisterRequest, UserLoginRequest,
    UserResponse, UserProfileResponse, StatusResponse,
)
from src.api.auth.cookies import set_auth_cookies, set_access_cookie

router = APIRouter(prefix="/api/v1", tags=["auth"])

@router.post("/registration", response_model=UserResponse, status_code=201)
async def registration(
    payload: UserRegisterRequest,
    service: AuthService = Depends(get_auth_service),
):
    return await service.register(payload.username, payload.password)

@router.post("/login", response_model=UserResponse, status_code=200)
async def login(
    payload: UserLoginRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    result = await service.login(payload.username, payload.password)
    set_auth_cookies(response, result.access_token, result.refresh_token)
    return result   # AuthDTO → UserResponse отфильтрует токены, оставит user_id+username


@router.post("/refresh", response_model=StatusResponse, status_code=200)
async def refresh(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None),
    service: AuthService = Depends(get_auth_service),
):
    access_token = await service.refresh(refresh_token)
    set_access_cookie(response, access_token)
    return StatusResponse(status="session_refreshed")

@router.post("/logout", response_model=StatusResponse, status_code=200)
async def logout(
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    return await service.logout(response)   # StatusDTO → StatusResponse

@router.get("/me", response_model=UserProfileResponse, status_code=200)
async def me(
    limit: int = Query(default=20, ge=1),
    offset: int = Query(default=0, ge=0),
    access_token: Optional[str] = Cookie(default=None),
    service: AuthService = Depends(get_auth_service),
):
    return await service.get_profile(access_token, limit, offset)