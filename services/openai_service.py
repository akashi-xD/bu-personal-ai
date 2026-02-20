# services/openai_service.py
import os
from openai import AsyncOpenAI

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "").strip()
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID", "").strip()
YANDEX_MODEL = os.getenv("YANDEX_MODEL", "").strip()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()


def _make_client() -> AsyncOpenAI | None:
    # Yandex (приоритет)
    if YANDEX_API_KEY and YANDEX_FOLDER_ID:
        return AsyncOpenAI(
            api_key=YANDEX_API_KEY,
            base_url="https://ai.api.cloud.yandex.net/v1",
            default_headers={
                "x-folder-id": YANDEX_FOLDER_ID,
                "x-data-logging-enabled": "false",
            },
        )

    # OpenAI (на будущее)
    if OPENAI_API_KEY:
        return AsyncOpenAI(api_key=OPENAI_API_KEY)

    return None


client = _make_client()


async def ask_gpt(messages: list[dict]) -> str:
    if client is None:
        return "[TEST MODE] Укажи YANDEX_API_KEY + YANDEX_FOLDER_ID + YANDEX_MODEL в .env"

    model = YANDEX_MODEL or "gpt-4o-mini"  # если вдруг будешь юзать OpenAI
    resp = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.4,
    )
    return resp.choices[0].message.content or ""