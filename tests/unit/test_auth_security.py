
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import jwt
import pytest

from src.api.auth import security

pytestmark = pytest.mark.unit

@pytest.mark.asyncio
async def test_hash_password_is_not_plaintext_and_verifies():
    hashed = await security.hash_password("StrongPass1")
    assert hashed != "StrongPass1"
    assert await security.verify_password("StrongPass1", hashed) is True
    assert await security.verify_password("wrong", hashed) is False

def test_access_token_has_correct_subject_and_type():
    user_id = uuid4()
    token = security.create_access_token(user_id)
    payload = security.decode_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"

def test_refresh_token_has_correct_subject_and_type():
    user_id = uuid4()
    payload = security.decode_token(security.create_refresh_token(user_id))
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"

def test_decode_invalid_token_returns_none():
    assert security.decode_token("not.a.jwt") is None

def test_decode_expired_token_returns_none(monkeypatch):
    token = jwt.encode(
        {"sub": str(uuid4()), "type": "access", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
        security.config.jwt.SECRET_KEY,
        algorithm=security.config.jwt.ALGORITHM,
    )
    assert security.decode_token(token) is None

def test_decode_token_with_wrong_signature_returns_none():
    token = jwt.encode(
        {"sub": str(uuid4()), "type": "access", "exp": datetime.now(timezone.utc)+timedelta(minutes=1)},
        "wrong-secret",
        algorithm=security.config.jwt.ALGORITHM,
    )
    assert security.decode_token(token) is None
