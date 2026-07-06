from pydantic import BaseModel


class SearchResultResponse(BaseModel):
    file_name: str
    page_number: int
    chunk_id: str
    text: str
    score: float


class StatusResponse(BaseModel):
    status: str