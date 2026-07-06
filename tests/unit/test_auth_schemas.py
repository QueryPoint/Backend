
import pytest
from pydantic import ValidationError
from src.api.auth.schemas import UserRegisterRequest

pytestmark = pytest.mark.unit

@pytest.mark.parametrize("username", ["abc", "a1_", "student2026", "A"*25])
def test_registration_accepts_valid_usernames(username):
    payload = UserRegisterRequest(username=username, password="123456")
    assert payload.username == username

@pytest.mark.parametrize("username", ["ab", "A"*26, "иван", "ivan petrov", "ivan-petrov", "ivan@gmail.com", "1ivan", "_ivan", "", "a!"])
def test_registration_rejects_invalid_usernames(username):
    with pytest.raises(ValidationError):
        UserRegisterRequest(username=username, password="123456")

@pytest.mark.parametrize("password", ["", "1", "12345"])
def test_registration_rejects_password_shorter_than_six(password):
    with pytest.raises(ValidationError):
        UserRegisterRequest(username="student", password=password)

@pytest.mark.parametrize("password", ["123456", "a"*1000])
def test_registration_accepts_password_at_or_above_minimum(password):
    assert UserRegisterRequest(username="student", password=password).password == password
