import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers.base import router as base_router
from handlers.profile import router as profile_router
from middlewares.middleware import LoggingMiddleware

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(base_router)
dp.include_router(profile_router)

dp.message.middleware(LoggingMiddleware())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
