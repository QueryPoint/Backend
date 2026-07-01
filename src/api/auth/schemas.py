import re
from pydantic import BaseModel, Field, field_validator

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=25)
    password: str = Field(..., min_length=6)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValueError("Only latin letters, digits and underscores are allowed")
        if not value[0].isalpha():
            raise ValueError("Username must start with a letter")
        if value.endswith("_"):
            raise ValueError("Username must not end with an underscore")
        if "__" in value:
            raise ValueError("Username must not contain consecutive underscores")
        return value

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    username: str

    model_config = {"from_attributes": True}

class UserProfileResponse(BaseModel):
    user_id: str
    username: str

class StatusResponse(BaseModel):
    status: str

