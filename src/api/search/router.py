from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.auth.dependencies import get_current_user_id
from src.api.search.dependencies import get_search_service
from src.api.search.service import SearchService
from src.api.search.schemas import SearchResultResponse, StatusResponse

router = APIRouter(prefix="/api/v1", tags=["search"])

@router.get("/search", response_model=list[SearchResultResponse], status_code=200)
async def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: UUID = Depends(get_current_user_id),
    service: SearchService = Depends(get_search_service),
) -> list[dict]:
    return await service.search(user_id, q, limit, offset)


@router.delete("/history", response_model=StatusResponse, status_code=200)
async def clear_history(
    user_id: UUID = Depends(get_current_user_id),
    service: SearchService = Depends(get_search_service),
) -> StatusResponse:
    await service.delete(user_id)
    return StatusResponse(status="history_cleared")