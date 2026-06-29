from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, text, Enum
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db.database import Base

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("TIMEZONE('utc', NOW())"),
    )
