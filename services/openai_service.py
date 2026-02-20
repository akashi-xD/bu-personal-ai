import os
from typing import Dict, List, Optional

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "").strip()

PROVIDER: str
if YANDEX_API_KEY and YANDEX_API_KEY != "placeholder":
    PROVIDER = "yandex"
elif OPENAI_API_KEY and not OPENAI_API_KEY.startswith("sk-placeholder"):
    PROVIDER = "openai"
else:
    PROVIDER = "none"

openai_client: Optional[object] = None
if PROVIDER == "openai":
    from openai import AsyncOpenAI
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def ask_gpt(messages: List[Dict]) -> str:
    """Универсальная функция для запросов к AI."""
    if PROVIDER == "yandex":
        from services.yandex_service import ask_yandexgpt
        return await ask_yandexgpt(messages)

    if PROVIDER == "openai":
        assert openai_client is not None
        resp = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        return resp.choices[0].message.content or ""

    return (
        "[TEST MODE] AI not configured.\n"
        "Add YANDEX_API_KEY or OPENAI_API_KEY to .env"
    )