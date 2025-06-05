"""Основной файл для запуска бота"""
import asyncio
import logging
import os
from aiogram import Bot
from dotenv import load_dotenv

from app import setup_bot


async def main():
    """Основная функция запуска бота"""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Получаем токен бота из переменных окружения
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN не установлен в переменных окружения")
    
    # Настраиваем бота
    bot, dp = await setup_bot(token)
    
    # Запускаем опрос событий в режиме long polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}", exc_info=True)