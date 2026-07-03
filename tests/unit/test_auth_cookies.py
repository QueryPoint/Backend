
from fastapi import Response
from src.api.auth.cookies import set_auth_cookies, set_access_cookie, clear_auth_cookies

def _headers(response):
    return "\n".join(response.headers.getlist("set-cookie")).lower()

def test_set_auth_cookies_sets_http_only_and_expected_paths():
    response = Response()
    set_auth_cookies(response, "access", "refresh")
    headers = _headers(response)
    assert "access_token=access" in headers
    assert "refresh_token=refresh" in headers
    assert "httponly" in headers
    assert "samesite=lax" in headers
    assert "path=/" in headers
    assert "path=/api/v1/refresh" in headers

def test_set_access_cookie_does_not_set_refresh_cookie():
    response = Response()
    set_access_cookie(response, "access")
    headers = _headers(response)
    assert "access_token=access" in headers
    assert "refresh_token" not in headers

def test_clear_auth_cookies_marks_both_cookies_deleted():
    response = Response()
    clear_auth_cookies(response)
    headers = _headers(response)
    assert "access_token=" in headers
    assert "refresh_token=" in headers
    assert "max-age=0" in headers
