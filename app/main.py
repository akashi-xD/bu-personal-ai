import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.handlers import router
from db.init_db import init_db
from services.scheduler import start_scheduler

load_dotenv()


async def main() -> None:
    await init_db()

    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)

    start_scheduler(bot)

    print("БУ! запущен 👻")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())