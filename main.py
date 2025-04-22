import asyncio
from aiogram import Bot, Dispatcher

from app.handlers import router
from app.database.models import async_main

async def main():
    await async_main()
    
    TOKEN = None
    with open(r'C:\Users\oleg7\tgb\app\token.txt') as f:
        TOKEN = f.read().strip()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')