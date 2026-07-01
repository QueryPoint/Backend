from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db.database import Base
from src.core.db.enums import DocType

if TYPE_CHECKING:
    from src.core.db.models.user import User


class Document(Base):
    __tablename__ = "documents"

    doc_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    doc_name: Mapped[str] = mapped_column(String, nullable=False)
    doc_viewlink: Mapped[str] = mapped_column(String, nullable=False)
    doc_size: Mapped[int] = mapped_column(Integer, nullable=False)
    doc_type: Mapped[DocType] = mapped_column(Enum(DocType), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("TIMEZONE('utc', NOW())"),
        nullable=False,
    )

    owner: Mapped["User"] = relationship(back_populates="documents")