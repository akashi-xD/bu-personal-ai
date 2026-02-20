import os
from openai import AsyncOpenAI

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "").strip()
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID", "").strip()
YANDEX_MODEL = os.getenv("YANDEX_MODEL", "yandexgpt-lite").strip()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

def _make_client() -> AsyncOpenAI:
    # Если есть Yandex — используем его (приоритет)
    if YANDEX_API_KEY and YANDEX_FOLDER_ID:
        return AsyncOpenAI(
            api_key=YANDEX_API_KEY,
            base_url="https://ai.api.cloud.yandex.net/v1",
            project=YANDEX_FOLDER_ID,
            # можно отключить логирование данных (опционально)
            default_headers={"x-data-logging-enabled": "false"},
        )
    # Иначе (на будущее) — обычный OpenAI
    if OPENAI_API_KEY:
        return AsyncOpenAI(api_key=OPENAI_API_KEY)

    # Иначе тестовый режим
    return None  # type: ignore

client = _make_client()

async def ask_gpt(prompt: str) -> str:
    if client is None:
        return "[TEST MODE] Укажи YANDEX_API_KEY и YANDEX_FOLDER_ID в .env"

    resp = await client.chat.completions.create(
        model=YANDEX_MODEL,
        messages=[
            {"role": "system", "content": "Ты поддерживающий AI ассистент по имени БУ!"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )
    return resp.choices[0].message.content or ""