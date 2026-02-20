from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def ask_gpt(prompt: str):
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты поддерживающий AI ассистент по имени БУ!"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content