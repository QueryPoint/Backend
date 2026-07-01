from fastapi import Response
from src.config.config import config


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/api/v1/refresh",
    )


def set_access_cookie(
    response: Response,
    access_token: str,
) -> None:

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/v1/refresh")