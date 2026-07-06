import re
from uuid import UUID
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
        return value

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    user_id: UUID
    username: str

class StatusResponse(BaseModel):
    model_config = {"from_attributes": True}

    status: str

class DocumentResponse(BaseModel):
    model_config = {"from_attributes": True}

    doc_id: UUID
    doc_name: str
    doc_viewlink: str
    doc_size: int
    doc_type: str

class UserProfileResponse(BaseModel):
    model_config = {"from_attributes": True}

    user_id: UUID
    username: str
    documents: list[DocumentResponse]
