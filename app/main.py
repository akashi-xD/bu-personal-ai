import asyncio
from aiogram import Bot, Dispatcher
from bot.handlers import router
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    dp.include_router(router)

    print("БУ! запущен 👻")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())