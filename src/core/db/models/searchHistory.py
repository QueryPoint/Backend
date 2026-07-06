from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, String, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db.database import Base
if TYPE_CHECKING:
    from src.core.db.models.user import User

class SearchHistory(Base):
    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    query: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("TIMEZONE('utc', NOW())"),
    )

    user: Mapped["User"] = relationship(back_populates="search_history")

