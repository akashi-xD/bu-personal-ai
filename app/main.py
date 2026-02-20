import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.handlers import router

load_dotenv()


async def main() -> None:
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)

    print("БУ! запущен 👻")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())