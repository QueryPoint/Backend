from dataclasses import dataclass
from uuid import UUID

@dataclass
class AuthDTO:
    user_id: UUID
    username: str
    access_token: str
    refresh_token: str

@dataclass
class UserDTO:
    user_id: UUID
    username: str

@dataclass
class UserProfileDTO:
    user_id: UUID
    username: str


@dataclass
class StatusDTO:
    status: str