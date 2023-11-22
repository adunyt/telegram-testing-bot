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
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())

#TODO: 
# + 1. Сделать re проверку на инлайн запросах (вуз\ /w+ или чето такое)
# + 2. Спроектировать адаптер для бека с псевдо выводом
# + 3. Подключить адаптер к боту
# + 4. Доделать регистрацию

# +- 5. Проверки в боте (существование теста, регистрация пользователя)
# + 6. Тестирование
# +-7. Сохранение и отправка результатов
# + 8. Статистика