# bot/handlers.py
from __future__ import annotations

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from zoneinfo import ZoneInfo

from bot.keyboards import confirm_proposal_kb
from db.crud import create_task, list_open_tasks, complete_task
from services.nlp_parser import try_parse_create_task
from services.openai_service import ask_gpt

import uuid

router = Router()

# MVP-хранилище предложений (до подтверждения)
# proposal_id -> dict(...)
PENDING: dict[str, dict] = {}
LOCAL_TZ = ZoneInfo("Asia/Yakutsk")

@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("БУ! 👻 LOCAL BUILD 2026-02-20 ✅")

@router.message(Command("list"))
async def list_handler(message: types.Message):
    tasks = await list_open_tasks(message.chat.id)
    if not tasks:
        await message.answer("Пока нет активных задач.")
        return
    lines = ["📌 Активные задачи:"]
    for t in tasks:
        due = t.due_time.strftime("%Y-%m-%d %H:%M") if t.due_time else "без срока"
        lines.append(f"#{t.id} — {t.title} — ⏰ {due}")
    await message.answer("\n".join(lines))


@router.message(Command("done"))
async def done_handler(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Используй: /done <id>\nНапример: /done 3")
        return
    ok = await complete_task(message.chat.id, int(parts[1]))
    await message.answer("✅ Отметил выполненной." if ok else "Не нашёл такую задачу.")


@router.callback_query(F.data.startswith("confirm:"))
async def confirm_callback(call: CallbackQuery):
    proposal_id = call.data.split(":", 1)[1]
    p = PENDING.pop(proposal_id, None)
    if not p:
        await call.message.edit_text("Это предложение уже неактуально.")
        await call.answer()
        return

    task = await create_task(chat_id=p["chat_id"], title=p["title"], due_time=p["due_time"])
    due = task.due_time.strftime("%Y-%m-%d %H:%M") if task.due_time else "без срока"
    await call.message.edit_text(f"✅ Создал задачу #{task.id}\n• {task.title}\n• ⏰ {due}")
    await call.answer()
    print("CONFIRM:", call.data)


@router.callback_query(F.data.startswith("cancel:"))
async def cancel_callback(call: CallbackQuery):
    proposal_id = call.data.split(":", 1)[1]
    PENDING.pop(proposal_id, None)
    await call.message.edit_text("❌ Ок, отменил.")
    await call.answer()


@router.message()
async def text_handler(message: types.Message):
    # 1) Пытаемся разобрать локально (дешево)
    parsed = try_parse_create_task(message.text)
    print("TEXT:", message.text, "PARSED:", bool(parsed))
    if parsed:
        proposal_id = str(uuid.uuid4())
        print("SENDING PROPOSAL", proposal_id, parsed.title, parsed.due_at_utc)
        PENDING[proposal_id] = {
            "chat_id": message.chat.id,
            "title": parsed.title,
            "due_time": parsed.due_at_utc,
        }

        due = parsed.due_at_utc.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M")
        header = "🧾 Предложение: создать дедлайн" if parsed.kind == "deadline" else "🧾 Предложение: создать задачу"
        await message.answer(
            f"{header}\n• Название: {parsed.title}\n• Срок: {due}\n\nПодтвердить?",
            reply_markup=confirm_proposal_kb(proposal_id),
        )
        return

    # 2) Если не распознали — fallback на LLM (пока просто чат)
    reply = await ask_gpt(
        [
            {"role": "system", "content": "Ты поддерживающий AI ассистент по имени БУ!"},
            {"role": "user", "content": message.text},
        ]
    )
    await message.answer(reply)