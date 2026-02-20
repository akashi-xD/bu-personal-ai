from aiogram import Router, types
from aiogram.filters import Command
from services.openai_service import ask_gpt

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("БУ! 👻 Я твой личный ассистент.")

@router.message()
async def chat_handler(message: types.Message):
    reply = await ask_gpt([{"role": "user", "content": message.text}])
    await message.answer(reply)