from uuid import UUID

from sqlalchemy import delete

from src.core.db.models.searchHistory import SearchHistory
from src.core.db.dto.searchDTO import SearchHistoryDTO
from src.core.db.repositories.base import BaseRepository

class SearchHistoryRepository(BaseRepository):

    async def create(self, user_id: UUID, query: str) -> SearchHistoryDTO:
        record = SearchHistory(user_id=user_id, query=query)
        self._session.add(record)
        await self._session.flush()
        return self._to_dto(record)

    async def delete_by_user(self, user_id: UUID) -> None:
        await self._session.execute(
            delete(SearchHistory).where(SearchHistory.user_id == user_id)
        )

    @staticmethod
    def _to_dto(record: SearchHistory) -> SearchHistoryDTO:
        return SearchHistoryDTO(
            id=record.id,
            user_id=record.user_id,
            query=record.query,
            created_at=record.created_at,
        )