import logging
import sys
from os import getenv

import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from routers import registration, commands, testing

load_dotenv(".env")
TOKEN = getenv("BOT_TOKEN")

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_routers(registration.registrationRouter,
                       commands.commandRouter,
                       testing.testingRouter)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())