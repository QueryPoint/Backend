
from uuid import uuid4
from unittest.mock import MagicMock
import jwt
from src.api.ws.router import _get_user_id
from src.api.auth.security import config

def test_ws_rejects_missing_cookie():
    assert _get_user_id(MagicMock(cookies={})) is None

def test_ws_rejects_non_access_token():
    token=jwt.encode({"sub":str(uuid4()),"type":"refresh"},config.jwt.SECRET_KEY,algorithm=config.jwt.ALGORITHM)
    assert _get_user_id(MagicMock(cookies={"access_token":token})) is None

def test_ws_extracts_user_id_from_valid_access_cookie():
    from src.api.auth.security import create_access_token
    user_id=uuid4()
    assert _get_user_id(MagicMock(cookies={"access_token":create_access_token(user_id)}))==user_id
