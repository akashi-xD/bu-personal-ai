import os
from typing import List, Dict

# Выбираем провайдера по наличию ключей
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "")

# Определяем активный провайдер
if YANDEX_API_KEY and YANDEX_API_KEY != "placeholder":
    PROVIDER = "yandex"
elif OPENAI_API_KEY and not OPENAI_API_KEY.startswith("sk-placeholder"):
    PROVIDER = "openai"
else:
    PROVIDER = "none"

# Инициализация клиентов
openai_client = None
if PROVIDER == "openai":
    from openai import AsyncOpenAI
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def ask_gpt(messages: List[Dict]) -> str:
    """Универсальная функция для запросов к AI"""
    
    if PROVIDER == "yandex":
        from services.yandex_service import ask_yandexgpt
        return await ask_yandexgpt(messages)
    
    elif PROVIDER == "openai":
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message.content
    
    else:
        return "[TEST MODE] AI not configured. Add YANDEX_API_KEY or OPENAI_API_KEY to .env"