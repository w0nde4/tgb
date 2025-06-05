"""Базовые обработчики команд"""
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from app.states.survey_states import SurveyStates
from app.config import Config
from app.services.survey_service import SurveyService
from app.ui.keyboards import KeyboardFactory
from app.ui.message_builder import MessageBuilder
from app.handlers.question import ask_question

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message,
    state: FSMContext,
    survey_service: SurveyService,
    keyboard_factory: KeyboardFactory,
    message_builder: MessageBuilder):
    """
    Обработчик команды /start
    
    Args:
        message: Объект сообщения
        state: Контекст FSM
    """
    logger.info(f"Пользователь {message.from_user.id} начал опрос")
    
    # Устанавливаем начальное состояние опроса
    await state.set_state(SurveyStates.in_progress)
    
    # Инициализируем данные пользователя
    await state.update_data(
        current_module=Config.DEFAULT_MODULE,
        current_question_id=Config.DEFAULT_QUESTION_ID,
        answers={},
        selected_options=[],
        current_level=0
    )
    
    # Задаем первый вопрос
    await ask_question(message,
        state,
        survey_service,
        keyboard_factory,
        message_builder)


@router.message(Command('stop'))
async def cmd_stop(message: Message, state: FSMContext):
    """
    Обработчик команды /stop
    
    Args:
        message: Объект сообщения
        state: Контекст FSM
    """
    logger.info(f"Пользователь {message.from_user.id} остановил опрос")
    
    current_state = await state.get_state()
    if current_state:
        # Очищаем состояние FSM
        await state.clear()
        await message.answer("Опрос остановлен. Чтобы начать заново, используйте команду /start")
    else:
        await message.answer("Нет активного опроса. Чтобы начать, используйте команду /start")