from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class SearchHistoryDTO:
    id: int
    user_id: UUID
    query: str
    created_at: datetime