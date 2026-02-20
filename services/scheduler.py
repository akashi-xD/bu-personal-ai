# services/scheduler.py
from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from db.reminders import get_due_tasks, mark_notified

LOCAL_TZ = ZoneInfo("Asia/Yakutsk")


def start_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=timezone.utc)

    async def check_due_tasks():
        now_utc = datetime.now(timezone.utc)
        tasks = await get_due_tasks(now=now_utc)

        for t in tasks:
            due_local = t.due_time.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M") if t.due_time else "без срока"
            await bot.send_message(
                t.chat_id,
                "⏰ Напоминание!\n"
                f"#{t.id} — {t.title}\n"
                f"Срок (Якутск): {due_local}\n\n"
                f"Когда сделаешь — напиши: /done {t.id}",
            )
            await mark_notified(t.id)

    scheduler.add_job(check_due_tasks, IntervalTrigger(seconds=60), id="due_tasks")
    scheduler.start()
    return scheduler