"""Инициализация приложения и его компонентов"""
import logging
import sys
from typing import Optional, Callable, Awaitable, Dict, Any

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.config import Config
from app.data.data_loader import load_survey_data
from app.services.image_service import ImageService
from app.services.survey_service import SurveyService
from app.ui.keyboards import KeyboardFactory
from app.ui.message_builder import MessageBuilder
from app.handlers import router


def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )


class DependencyMiddleware(BaseMiddleware):
    def __init__(
        self,
        survey_service: SurveyService,
        keyboard_factory: KeyboardFactory,
        message_builder: MessageBuilder
    ):
        self.survey_service = survey_service
        self.keyboard_factory = keyboard_factory
        self.message_builder = message_builder

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data["survey_service"] = self.survey_service
        data["keyboard_factory"] = self.keyboard_factory
        data["message_builder"] = self.message_builder
        return await handler(event, data)


async def setup_bot(token: str, webhook_url: Optional[str] = None):
    """
    Настройка и запуск бота
    
    Args:
        token: API токен бота
        webhook_url: URL для вебхука (опционально)
        
    Returns:
        tuple: (бот, диспетчер)
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Инициализация бота...")
    
    storage = MemoryStorage()
    bot = Bot(token=token)
    dp = Dispatcher(storage=storage)
    
    try:
        survey_data = load_survey_data(Config.DATA_FILE)
        logger.info(f"Данные опроса загружены из {Config.DATA_FILE}")
        
        image_service = ImageService(Config.IMAGES_DIR)
        survey_service = SurveyService(survey_data)
        keyboard_factory = KeyboardFactory()
        message_builder = MessageBuilder(image_service)
        
        dep_middleware = DependencyMiddleware(
            survey_service=survey_service,
            keyboard_factory=keyboard_factory,
            message_builder=message_builder
        )
        
        dp.message.middleware.register(dep_middleware)
        dp.callback_query.middleware.register(dep_middleware)
        
        dp.include_router(router)
        
        if webhook_url:
            await bot.set_webhook(webhook_url)
            logger.info(f"Вебхук установлен на {webhook_url}")
        else:
            await bot.delete_webhook()
            logger.info("Вебхук отключен")
        
        logger.info("Бот успешно инициализирован!")
        return bot, dp
    
    except Exception as e:
        logger.error(f"Ошибка при инициализации бота: {e}", exc_info=True)
        raise