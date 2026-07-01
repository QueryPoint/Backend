from fastapi import HTTPException, status

class Unauthed(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

class UsernameTaken(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

class UserNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")