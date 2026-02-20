# db/models.py
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)

    title: Mapped[str] = mapped_column(String)
    # ✅ Храним UTC с tzinfo
    due_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    notified: Mapped[bool] = mapped_column(Boolean, default=False)