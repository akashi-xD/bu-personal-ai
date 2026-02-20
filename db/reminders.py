# db/reminders.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy import select, update
from db.database import SessionLocal
from db.models import Task


async def get_due_tasks(now: datetime, limit: int = 50) -> list[Task]:
    async with SessionLocal() as session:
        stmt = (
            select(Task)
            .where(
                Task.due_time.is_not(None),
                Task.due_time <= now,
                Task.completed == False,  # noqa: E712
                Task.notified == False,   # noqa: E712
            )
            .order_by(Task.due_time.asc())
            .limit(limit)
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())


async def mark_notified(task_id: int) -> None:
    async with SessionLocal() as session:
        await session.execute(update(Task).where(Task.id == task_id).values(notified=True))
        await session.commit()