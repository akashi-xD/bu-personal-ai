# services/yandex_service.py
import os
from typing import List, Dict
import httpx

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
MODEL_URI = f"gpt://{YANDEX_FOLDER_ID}/yandexgpt/rc"  # Твоя модель

async def ask_yandexgpt(messages: List[Dict]) -> str:
    """Асинхронно отправляет запрос к YandexGPT"""

    if not YANDEX_API_KEY or YANDEX_API_KEY == "placeholder":
        return "[YANDEX MODE] API key not configured. Add YANDEX_API_KEY to .env"

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "x-folder-id": YANDEX_FOLDER_ID,
        "Content-Type": "application/json"
    }

    # Конвертируем формат сообщений
    yandex_messages = []
    for msg in messages:
        role = "assistant" if msg.get("role") == "assistant" else "user"
        yandex_messages.append({
            "role": role,
            "text": msg.get("content", "")
        })

    data = {
        "modelUri": MODEL_URI,
        "completionOptions": {
            "temperature": 0.7,
            "maxTokens": 2000
        },
        "messages": yandex_messages
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()

        # Извлекаем текст ответа
        alternatives = result.get("result", {}).get("alternatives", [])
        if alternatives:
            return alternatives[0].get("message", {}).get("text", "No response")
        return "Empty response from YandexGPT"

    except Exception as e:
        return f"[YANDEX ERROR] {str(e)}"