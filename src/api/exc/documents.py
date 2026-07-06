from fastapi import HTTPException, status

class InvalidDocument(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document")

class DocumentNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

class DocumentForbidden(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

class S3Error(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Storage error")