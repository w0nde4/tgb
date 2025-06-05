"""Обработчики вопросов опроса"""
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

logger = logging.getLogger(__name__)

router = Router()
question_lock = Lock()


async def ask_question(
    message: Message, 
    state: FSMContext, 
    survey_service: SurveyService = None, 
    keyboard_factory: KeyboardFactory = None,
    message_builder: MessageBuilder = None
):
    """
    Отправляет пользователю текущий вопрос
    
    Args:
        message: Объект сообщения
        state: Контекст FSM
        survey_service: Сервис опроса
        keyboard_factory: Фабрика клавиатур
        message_builder: Построитель сообщений
    """
    try:
        # Получаем данные пользователя
        user_data = await state.get_data()
        module = user_data['current_module']
        question_id = user_data['current_question_id']
        current_level = user_data.get('current_level', 0)

        # Получаем вопрос
        question = survey_service.get_question(module, question_id)
        if not question:
            await message.answer("Ошибка: вопрос не найден. Пожалуйста, начните опрос заново с помощью /start")
            await state.clear()
            return

        # Для вопросов с уровнями
        if question.levels and current_level < len(question.levels):
            level = question.levels[current_level]
            
            # Формируем текст для текущего уровня
            if current_level == 0:
                level_text = f"{question.text}\n\n"
            else:
                level_text = ""
                
            if level.height:
                level_text += f"• {level.height}"
            elif level.angle:
                level_text += f"• {level.angle}"
            elif level.surface:
                level_text += f"• {level.surface}"
            
            # Получаем варианты ответов для уровня
            options = survey_service.get_options_for_level(level)
            if options:
                # Создаем клавиатуру
                markup = keyboard_factory.create_level_option_markup(level, options)
                
                # Отправляем сообщение для уровня
                await message_builder.send_level_message(message, level, level_text, markup)
            else:
                # Если опций нет, показываем информацию и переходим к следующему уровню
                await message.answer(level_text)
                await state.update_data(current_level=current_level + 1)
                await ask_question(message, state, survey_service, keyboard_factory, message_builder)
            
            return

        # Сбрасываем current_level если это обычный вопрос или все уровни обработаны
        await state.update_data(current_level=0)

        # Создаем клавиатуру в зависимости от типа вопроса
        if question.type == 'single_option':
            markup = keyboard_factory.create_single_option_markup(question)
        elif question.type == 'multiple_options':
            selected = user_data.get('selected_options', [])
            markup = keyboard_factory.create_multiple_options_markup(question, selected)
        else:
            await message.answer(f"Ошибка: неизвестный тип вопроса: {question.type}")
            return

        # Отправляем сообщение с вопросом
        await message_builder.send_question_message(message, question, markup)
            
    except Exception as e:
        logger.error(f"Ошибка при отправке вопроса: {e}", exc_info=True)
        await message.answer(f"Произошла ошибка при загрузке вопроса: {str(e)}")


async def handle_next_question(
    message: Message, 
    state: FSMContext, 
    survey_service: SurveyService = None, 
    keyboard_factory: KeyboardFactory = None,
    message_builder: MessageBuilder = None
):
    """
    Определяет и отправляет следующий вопрос
    
    Args:
        message: Объект сообщения
        state: Контекст FSM
        survey_service: Сервис опроса
        keyboard_factory: Фабрика клавиатур
        message_builder: Построитель сообщений
    """
    if question_lock.locked():
        logger.debug("Question lock is locked, returning")
        return
    
    async with question_lock:
        try:
            # Получаем текущие данные пользователя
            data = await state.get_data()
            module = data['current_module']
            question_id = data['current_question_id']
            
            # Получаем ответ на текущий вопрос
            key = f"{module}_{question_id}"
            answer = data['answers'].get(key)
            
            # Для множественного выбора используем первый выбранный вариант для навигации
            if isinstance(answer, list) and answer:
                answer = answer[0]
            
            # Определяем следующий вопрос
            next_module, next_question_id = survey_service.get_next_question(module, question_id, answer)
            
            # Если следующего вопроса нет, опрос завершен
            if next_module is None or next_question_id is None:
                # Завершаем опрос
                await message.answer("Опрос завершен! Спасибо за участие.")
                
                # Выводим статистику ответов для отладки
                answers = data['answers']
                await message.answer(f"Всего получено ответов: {len(answers)}")
                
                # Очищаем состояние
                await state.clear()
                return
            
            # Обновляем данные пользователя для следующего вопроса
            await state.update_data(
                current_module=next_module,
                current_question_id=next_question_id,
                current_level=0
            )
            
            # Отправляем следующий вопрос
            await ask_question(message, state, survey_service, keyboard_factory, message_builder)
            
        except Exception as e:
            logger.error(f"Ошибка при переходе к следующему вопросу: {e}", exc_info=True)
            await message.answer(f"Произошла ошибка при обработке вопроса: {str(e)}")


@router.callback_query(SurveyStates.in_progress, F.data.startswith("single:"))
async def handle_single_option_select(
    callback: CallbackQuery, 
    state: FSMContext, 
    survey_service: SurveyService,
    keyboard_factory: KeyboardFactory,
    message_builder: MessageBuilder
):
    """
    Обработчик выбора варианта с одиночным выбором
    
    Args:
        callback: Объект callback запроса
        state: Контекст FSM
        survey_service: Сервис опроса
        keyboard_factory: Фабрика клавиатур
        message_builder: Построитель сообщений
    """
    if question_lock.locked():
        await callback.answer("Подождите, обрабатывается предыдущий ответ")
        return
    
    try:
        # Получаем хеш выбранного варианта
        hashed_opt = callback.data.split(":", 1)[1]
        
        # Получаем текущие данные пользователя
        data = await state.get_data()
        module = data['current_module']
        question_id = data['current_question_id']
        
        # Получаем текущий вопрос
        question = survey_service.get_question(module, question_id)
        if not question or not question.options:
            await callback.answer("Ошибка: вопрос не найден")
            return
        
        # Находим выбранный вариант по хешу
        original_opt = None
        for opt in question.options:
            if get_callback_data(opt) == hashed_opt:
                original_opt = opt
                break
        
        if not original_opt:
            await callback.answer("Ошибка выбора!")
            return
        
        # Сохраняем ответ
        answers = data['answers']
        key = f"{module}_{question_id}"
        answers[key] = original_opt
        await state.update_data(answers=answers)
        
        await callback.answer()
        
        # Переходим к следующему вопросу
        await handle_next_question(callback.message, state, survey_service, keyboard_factory, message_builder)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке одиночного выбора: {e}", exc_info=True)
        await callback.answer("Произошла ошибка при обработке ответа")


@router.callback_query(SurveyStates.in_progress, F.data.startswith("multi:"))
async def handle_multi_select(
    callback: CallbackQuery, 
    state: FSMContext, 
    survey_service: SurveyService,
    keyboard_factory: KeyboardFactory
):
    """
    Обработчик выбора варианта с множественным выбором
    
    Args:
        callback: Объект callback запроса
        state: Контекст FSM
        survey_service: Сервис опроса
        keyboard_factory: Фабрика клавиатур
    """
    if question_lock.locked():
        await callback.answer("Подождите, обрабатывается предыдущий ответ")
        return
    
    try:
        # Получаем хеш выбранного варианта
        hashed_opt = callback.data.split(":", 1)[1]
        
        # Получаем текущие данные пользователя
        data = await state.get_data()
        module = data['current_module']
        question_id = data['current_question_id']
        
        # Получаем текущий вопрос
        question = survey_service.get_question(module, question_id)
        if not question or not question.options:
            await callback.answer("Ошибка: вопрос не найден")
            return
        
        # Находим выбранный вариант по хешу
        original_opt = None
        for opt in question.options:
            if get_callback_data(opt) == hashed_opt:
                original_opt = opt
                break
        
        if not original_opt:
            await callback.answer("Ошибка выбора!")
            return
        
        # Обновляем список выбранных вариантов
        selected = data.get('selected_options', [])
        
        if original_opt in selected:
            selected.remove(original_opt)
        else:
            selected.append(original_opt)
        
        await state.update_data(selected_options=selected)
        
        # Обновляем клавиатуру
        markup = keyboard_factory.create_multiple_options_markup(question, selected)
        await callback.message.edit_reply_markup(reply_markup=markup)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при обработке множественного выбора: {e}", exc_info=True)
        await callback.answer("Произошла ошибка при обработке ответа")


@router.callback_query(SurveyStates.in_progress, F.data == "multi_submit")
async def handle_multi_submit(
    callback: CallbackQuery, 
    state: FSMContext, 
    survey_service: SurveyService,
    keyboard_factory: KeyboardFactory,
    message_builder: MessageBuilder
):
    """
    Обработчик подтверждения множественного выбора
    
    Args:
        callback: Объект callback запроса
        state: Контекст FSM
        survey_service: Сервис опроса
        keyboard_factory: Фабрика клавиатур
        message_builder: Построитель сообщений
    """
    try:
        # Получаем текущие данные пользователя
        data = await state.get_data()
        selected = data.get('selected_options', [])
        
        # Проверяем, выбран ли хотя бы один вариант
        if not selected:
            await callback.answer("Пожалуйста, выберите хотя бы один вариант", show_alert=True)
            return
        
        # Сохраняем ответ с множественным выбором
        module = data['current_module']
        question_id = data['current_question_id']
        answers = data['answers']
        key = f"{module}_{question_id}"
        answers[key] = selected
        
        # Очищаем список выбранных вариантов для следующего вопроса
        await state.update_data(answers=answers, selected_options=[])
        
        await callback.answer()
        
        # Переходим к следующему вопросу
        await handle_next_question(callback.message, state, survey_service, keyboard_factory, message_builder)
        
    except Exception as e:
        logger.error(f"Ошибка при подтверждении множественного выбора: {e}", exc_info=True)
        await callback.answer("Произошла ошибка при обработке ответа")