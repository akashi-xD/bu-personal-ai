# db/crud.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy import select, update
from db.database import SessionLocal
from db.models import Task


async def create_task(chat_id: int, title: str, due_time: datetime | None) -> Task:
    async with SessionLocal() as session:
        task = Task(chat_id=chat_id, title=title, due_time=due_time, completed=False)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task


async def list_open_tasks(chat_id: int, limit: int = 20) -> list[Task]:
    async with SessionLocal() as session:
        stmt = (
            select(Task)
            .where(Task.chat_id == chat_id, Task.completed == False)  # noqa: E712
            .order_by(Task.due_time.is_(None), Task.due_time.asc())
            .limit(limit)
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())


async def complete_task(chat_id: int, task_id: int) -> bool:
    async with SessionLocal() as session:
        stmt = (
            update(Task)
            .where(Task.chat_id == chat_id, Task.id == task_id)
            .values(completed=True)
        )
        res = await session.execute(stmt)
        await session.commit()
        return (res.rowcount or 0) > 0