# services/nlp_parser.py
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
TIME_RE = re.compile(r"\b([01]?\d|2[0-3])[:\.]([0-5]\d)\b")


@dataclass
class ParsedCreateTask:
    title: str
    due_at_utc: datetime  # ✅ UTC aware
    kind: str  # "deadline" | "task"


def _normalize_spaces(s: str) -> str:
    return " ".join(s.strip().split())


def _pick_year(month: int, day: int, now_local: datetime) -> int:
    """Если дата уже прошла в этом году (по локальному времени) — берем следующий год."""
    try:
        d = date(now_local.year, month, day)
    except ValueError:
        return now_local.year
    return now_local.year if d >= now_local.date() else now_local.year + 1


def _extract_time(text: str) -> time | None:
    m = TIME_RE.search(text)
    if not m:
        return None
    return time(int(m.group(1)), int(m.group(2)))


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

    low = text.lower()
    if "послезавтра" in low:
        return date.fromordinal(now_local.date().toordinal() + 2)
    if "завтра" in low:
        return date.fromordinal(now_local.date().toordinal() + 1)
    if "сегодня" in low:
        return now_local.date()

    return None


def try_parse_create_task(text: str) -> ParsedCreateTask | None:
    """
    Парсим фразы типа:
    - "добавь дедлайн 08 марта по сдаче СРС по ЦОС"
    - "создай задачу завтра в 18:30 сделать лабораторную"
    """
    now_local = datetime.now(LOCAL_TZ)

    t = _normalize_spaces(text)
    low = t.lower()

    has_create_verb = any(k in low for k in ("добавь", "добавить", "создай", "создать", "запланируй", "запланировать"))
    has_task_words = any(k in low for k in ("дедлайн", "задача", "напомни", "напоминание", "сдать", "сдача"))

    if not (has_create_verb or has_task_words):
        return None

    is_deadline = "дедлайн" in low or "сдать" in low or "сдача" in low

    d = _extract_date(t, now_local)
    if not d:
        return None

    tm = _extract_time(t)
    if tm is None:
        tm = time(23, 59) if is_deadline else time(9, 0)

    # ✅ Локальное время Якутска → UTC
    due_local = datetime(d.year, d.month, d.day, tm.hour, tm.minute, tzinfo=LOCAL_TZ)
    due_utc = due_local.astimezone(timezone.utc)

    title = re.sub(r"(?i)\b(добавь|добавить|создай|создать|запланируй|запланировать)\b", "", t)
    title = re.sub(r"(?i)\b(в календарь|календарь)\b", "", title)
    title = re.sub(r"(?i)\bдедлайн\b", "", title)
    title = _normalize_spaces(title)

    if not title:
        title = "Задача"

    return ParsedCreateTask(
        title=title,
        due_at_utc=due_utc,
        kind=("deadline" if is_deadline else "task"),
    )