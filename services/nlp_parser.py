from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, date, time, timezone
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo("Asia/Yakutsk")

RU_MONTHS = {
    "января": 1, "янв": 1,
    "февраля": 2, "фев": 2,
    "марта": 3, "мар": 3,
    "апреля": 4, "апр": 4,
    "мая": 5,
    "июня": 6, "июн": 6,
    "июля": 7, "июл": 7,
    "августа": 8, "авг": 8,
    "сентября": 9, "сен": 9, "сент": 9,
    "октября": 10, "окт": 10,
    "ноября": 11, "ноя": 11,
    "декабря": 12, "дек": 12,
}

DATE_DOT_RE = re.compile(r"\b(\d{1,2})\.(\d{1,2})(?:\.(\d{2,4}))?\b")
DATE_RU_RE = re.compile(r"\b(\d{1,2})\s+([а-яё]+)\b", re.IGNORECASE)
TIME_HHMM_RE = re.compile(r"\b([01]?\d|2[0-3])\s*[:\.]\s*([0-5]\d)\b")
TIME_HH_ONLY_RE = re.compile(r"(?i)\bв\s*([01]?\d|2[0-3])\b")
TIME_SPACE_RE = re.compile(r"\b([01]?\d|2[0-3])\s+([0-5]\d)\b")

@dataclass
class ParsedCreateTask:
    title: str
    due_at_utc: datetime  # ✅ UTC aware
    kind: str  # "deadline" | "task"

def _pick_year(month: int, day: int, now_local: datetime) -> int:
    """Если дата уже прошла в этом году (по локальному времени) — берем следующий год."""
    try:
        d = date(now_local.year, month, day)
    except ValueError:
        return now_local.year
    return now_local.year if d >= now_local.date() else now_local.year + 1


def _extract_time(text: str) -> time | None:
    # HH:MM или HH.MM (19:40 / 19.40)
    m = re.search(r"\b([01]?\d|2[0-3])\s*[:\.]\s*([0-5]\d)\b", text)
    if m:
        return time(int(m.group(1)), int(m.group(2)))

    # "19 40"
    m = re.search(r"\b([01]?\d|2[0-3])\s+([0-5]\d)\b", text)
    if m:
        return time(int(m.group(1)), int(m.group(2)))

    # "в 19"
    m = re.search(r"(?i)\bв\s*([01]?\d|2[0-3])\b", text)
    if m:
        return time(int(m.group(1)), 0)

    return None

def _extract_date(text: str, now_local: datetime) -> date | None:
    m = DATE_DOT_RE.search(text)
    if m:
        d = int(m.group(1))
        mo = int(m.group(2))
        yy = m.group(3)
        if yy:
            y = int(yy)
            if y < 100:
                y += 2000
        else:
            y = _pick_year(mo, d, now_local)
        try:
            return date(y, mo, d)
        except ValueError:
            return None

    m = DATE_RU_RE.search(text)
    if m:
        d = int(m.group(1))
        mon_raw = m.group(2).lower().replace("ё", "е")
        mo = RU_MONTHS.get(mon_raw)
        if not mo:
            return None
        y = _pick_year(mo, d, now_local)
        try:
            return date(y, mo, d)
        except ValueError:
            return None

    low = text.lower().replace("ё", "е")

    def has_word(w: str) -> bool:
        # границы "слова" считаем по буквам/цифрам/подчёркиванию (надежнее, чем \b для Unicode)
        return re.search(rf"(?<![a-zа-я0-9_]){w}(?![a-zа-я0-9_])", low) is not None

    if has_word("послезавтра"):
        return date.fromordinal(now_local.date().toordinal() + 2)

    if has_word("завтра"):
        return date.fromordinal(now_local.date().toordinal() + 1)

    if has_word("сегодня"):
        return now_local.date()

    return None

def _norm(s: str) -> str:
    return " ".join(s.strip().split())

def try_parse_create_task(text: str) -> ParsedCreateTask | None:
    now_local = datetime.now(LOCAL_TZ)
    t = _norm(text)
    low = t.lower()

    # ✅ 1) Сначала пытаемся найти дату
    d = _extract_date(t, now_local)
    if not d:
        return None

    # ✅ 2) Если дата есть — считаем это задачей, если есть хоть один "триггер"
    triggers = ("добав", "созд", "задач", "дедлайн", "напомн", "сдать", "сдач", "календар")
    if not any(trg in low for trg in triggers):
        return None

    is_deadline = any(w in low for w in ("дедлайн", "сдать", "сдача"))
    tm = _extract_time(t) or (time(23, 59) if is_deadline else time(9, 0))

    due_local = datetime(d.year, d.month, d.day, tm.hour, tm.minute, tzinfo=LOCAL_TZ)
    due_utc = due_local.astimezone(timezone.utc)

    title = re.sub(r"(?i)\b(добавь|добавить|создай|создать|запланируй|запланировать)\b", "", t)
    title = re.sub(r"(?i)\b(в календарь|календарь)\b", "", title)
    title = re.sub(r"(?i)\bдедлайн\b", "", title)
    title = _norm(title) or "Задача"

    return ParsedCreateTask(title=title, due_at_utc=due_utc, kind=("deadline" if is_deadline else "task"))