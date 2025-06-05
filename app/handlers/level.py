"""Обработчики для уровней вопросов"""
import logging
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from asyncio import Lock

from app.states.survey_states import SurveyStates
from app.data.encoder import get_callback_data
from app.services.survey_service import SurveyService
from app.ui.keyboards import KeyboardFactory
from app.ui.message_builder import MessageBuilder
from app.handlers.question import handle_next_question, ask_question

logger = logging.getLogger(__name__)

router = Router()
level_lock = Lock()


@router.callback_query(SurveyStates.in_progress, F.data.startswith("level:"))
async def handle_level_option_select(
    callback: CallbackQuery, 
    state: FSMContext, 
    survey_service: SurveyService,
    keyboard_factory: KeyboardFactory,
    message_builder: MessageBuilder
):
    """
    Обработчик выбора варианта для уровня вопроса
    
    Args:
        callback: Объект callback запроса
        state: Контекст FSM
        survey_service: Сервис опроса
        keyboard_factory: Фабрика клавиатур
        message_builder: Построитель сообщений
    """
    if level_lock.locked():
        await callback.answer("Подождите, обрабатывается предыдущий ответ")
        return
    
    async with level_lock:
        try:
            # Получаем хеш выбранного варианта
            hashed_opt = callback.data.split(":", 1)[1]
            
            # Получаем текущие данные пользователя
            data = await state.get_data()
            module = data['current_module']
            question_id = data['current_question_id']
            current_level = data.get('current_level', 0)
            
            # Получаем текущий уровень вопроса
            level = survey_service.get_level(module, question_id, current_level)
            if not level:
                await callback.answer("Ошибка: уровень не найден")
                return
            
            # Получаем варианты ответов для уровня
            options = survey_service.get_options_for_level(level)
            
            # Находим выбранный вариант по хешу
            original_opt = None
            for opt in options:
                if get_callback_data(opt) == hashed_opt:
                    original_opt = opt
                    break
            
            if not original_opt:
                await callback.answer("Ошибка выбора!")
                return
            
            # Сохраняем ответ для текущего уровня
            answers = data['answers']
            level_key = f"{module}_{question_id}_level_{current_level}"
            answers[level_key] = original_opt
            
            # Определяем, есть ли следующий уровень
            question = survey_service.get_question(module, question_id)
            if not question or not question.levels:
                await callback.answer("Ошибка: вопрос не найден")
                return
                
            next_level = current_level + 1
            should_go_to_next_level = next_level < len(question.levels)
            
            # Обновляем данные пользователя
            if should_go_to_next_level:
                await state.update_data(answers=answers, current_level=next_level)
            else:
                # Если это был последний уровень, сохраняем общий ответ на вопрос
                key = f"{module}_{question_id}"
                answers[key] = "completed all levels"
                await state.update_data(answers=answers, current_level=0)
            
            await callback.answer()
            
            # Переходим к следующему уровню или вопросу
            if should_go_to_next_level:
                await ask_question(
                    callback.message,
                    state,
                    survey_service,
                    keyboard_factory,
                    message_builder)
            else:
                await handle_next_question(
                    callback.message,
                    state,
                    survey_service,
                    keyboard_factory,
                    message_builder)
                
        except Exception as e:
            logger.error(f"Ошибка при обработке выбора уровня: {e}", exc_info=True)
            await callback.answer("Произошла ошибка при обработке ответа")