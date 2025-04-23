from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile 
from asyncio import Lock

import app.keyboards as kb
from app.load_texts import load_texts
from app.encoder import get_callback_data

import os

router = Router()

question_lock = Lock()

(data, options_scale, questions) = load_texts(r'app\ovz.json')


class SurveyStates(StatesGroup):
    in_progress = State()
    
   
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(state=SurveyStates.in_progress)
    await state.update_data(
        current_module = 'modul_1',
        current_question_id = 1,
        answers = {},
        selected_options = []
    )
    await ask_question(message, state)


@router.message(Command('stop'))
async def cmd_stop(message: Message, state: FSMContext):
    await message.answer("Завершение")
    await state.clear()


async def ask_question(message: Message, state: FSMContext):
    user_data = await state.get_data()
    module = user_data['current_module']
    q_id = user_data['current_question_id']
    question = questions[module][q_id]
    current_level = user_data.get('current_level', 0)

    if 'levels' in question and current_level < len(question['levels']):
        level = question['levels'][current_level]
        
        # Формируем текст для текущего уровня
        if current_level == 0:
            level_text = f"{question['text']}\n\n"
        else:
            level_text = ""
            
        if 'height' in level:
            level_text += f"• {level['height']}"
        elif 'angle' in level:
            level_text += f"• {level['angle']}"
        elif 'surface' in level:
            level_text += f"• {level['surface']}"
        
        # Получаем варианты ответов для текущего уровня
        if 'options' in level:
            markup = kb.create_level_option_markup(level)

            # Отправляем сообщение для текущего уровня
            if 'image' in level:
                image_path = f"app/images/{level['image']}"
                if os.path.exists(image_path):
                    try:
                        photo = FSInputFile(image_path)
                        await message.answer_photo(
                            photo=photo,
                            caption=level_text,
                            reply_markup=markup
                        )
                    except Exception as e:
                        await message.answer(
                            f"{level_text} (ошибка загрузки изображения)",
                            reply_markup=markup
                        )
                else:
                    await message.answer(level_text, reply_markup=markup)
            else:
                await message.answer(level_text, reply_markup=markup)
        else:
            # Если опций нет, просто показываем информацию и переходим к следующему уровню
            await message.answer(level_text)
            await state.update_data(current_level=current_level + 1)
            await ask_question(message, state)  # Рекурсивно вызываем для следующего уровня
        
        return
    
    # Если это обычный вопрос или все уровни обработаны,
    # сбрасываем current_level и продолжаем как обычно
    await state.update_data(current_level=0)

    if question['type'] == 'single_option':
        markup = kb.create_single_option_markup(question)
    elif question['type'] == 'multiple_options':
        selected = user_data.get('selected_options', [])
        markup = kb.create_multiple_options_markup(question, selected)

    try:
        if 'image' in question:
            # Handle image path
            image_path = f"app/images/{question['image']}"
            
            # Make sure the directory exists
            if not os.path.exists(image_path):
                await message.answer(f"Ошибка: Изображение не найдено - {question['image']}")
                image_path = None
            
            if image_path:
                await message.answer_photo(
                    photo=FSInputFile(image_path),
                    caption=question['text'],
                    reply_markup=markup
                )
            else:
                # Fallback if image doesn't exist
                await message.answer(
                    f"{question['text']} (изображение недоступно)",
                    reply_markup=markup
                )
        elif 'levels' in question:
            # For questions with levels that might have images
            level_texts = []
            for level in question['levels']:
                if 'height' in level:
                    level_texts.append(f"• {level['height']}")
                elif 'angle' in level:
                    level_texts.append(f"• {level['angle']}")
                elif 'surface' in level:
                    # For surface questions with individual images
                    if 'image' in level:
                        image_path = f"app/images/{level['image']}"
                        try:
                            await message.answer_photo(
                                photo=image_path,
                                caption=f"{level['surface']}"
                            )
                        except Exception:
                            await message.answer(f"{level['surface']} (изображение недоступно)")
                    else:
                        level_texts.append(f"• {level['surface']}")
            
            if level_texts:
                full_text = f"{question['text']}\n\n" + "\n".join(level_texts)
                await message.answer(full_text, reply_markup=markup)
            else:
                await message.answer(question['text'], reply_markup=markup)
        else:
            await message.answer(question['text'], reply_markup=markup)
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")


@router.callback_query(F.data.startswith("single:"))
async def handle_single_option_select(callback: CallbackQuery, state: FSMContext):
    global question_lock

    if question_lock.locked():
        await callback.answer("Подождите, обрабатывается предыдущий ответ")
        return
    
    hashed_opt = callback.data.split(":", 1)[1]
    data = await state.get_data()
    module = data['current_module']
    q_id = data['current_question_id']
    question = questions[module][q_id]

    print(f"Processing question: {question['text']}")
    print(f"Received hash: {hashed_opt}")
    
    # Find the original option text from the hash
    original_opt = None
    
    # Check in direct options
    if 'options' in question:
        for opt in question['options']:
            opt_hash = get_callback_data(opt)
            print(f"Option: {opt}, Hash: {opt_hash}")  # Отладка
            if opt_hash == hashed_opt:
                original_opt = opt
                break
    
    if not original_opt:
        await callback.answer("Ошибка выбора!")
        return
    
    # Save the answer
    answers = data['answers']
    key = f"{module}_{q_id}"
    answers[key] = original_opt
    await state.update_data(answers=answers)
    
    # Process next question
    await handle_next_question(callback.message, state)
    await callback.answer()


@router.callback_query(F.data.startswith("multi:"))
async def handle_multi_select(callback: CallbackQuery, state: FSMContext):
    global question_lock

    if question_lock.locked():
        await callback.answer("Подождите, обрабатывается предыдущий ответ")
        return
    
    hashed_opt = callback.data.split(":", 1)[1]
    data = await state.get_data()
    module = data['current_module']
    q_id = data['current_question_id']
    question = questions[module][q_id]
    
    original_opt = next(
        (opt for opt in question['options'] 
         if get_callback_data(opt) == hashed_opt),
        None
    )
    
    if not original_opt:
        await callback.answer("Ошибка выбора!")
        return
    
    selected = data.get('selected_options', [])
    
    if original_opt in selected:
        selected.remove(original_opt)
    else:
        selected.append(original_opt)
    
    await state.update_data(selected_options=selected)
    
    # Update the keyboard
    markup = kb.create_multiple_options_markup(question, selected)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data == "multi_submit")
async def handle_multi_submit(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get('selected_options', [])

    if not selected:
        await callback.answer("Пожалуйста, выберите хотя бы один вариант", show_alert=True)
        return
    
    # Save the multi-choice answer
    module = data['current_module']
    q_id = data['current_question_id']
    answers = data['answers']
    key = f"{module}_{q_id}"
    answers[key] = selected
    
    # Clear selected options for next question
    await state.update_data(answers=answers, selected_options=[])
    
    # Move to next question
    await handle_next_question(callback.message, state)
    await callback.answer()


async def handle_next_question(message: Message, state: FSMContext):
    global question_lock

    if question_lock.locked():
        print("DEBUG: Question lock is locked, returning")
        return
    
    print("DEBUG: Entering handle_next_question")
    
    async with question_lock:
        data = await state.get_data()
        module = data['current_module']
        q_id = data['current_question_id']

        print(f"DEBUG: Current module: {module}, Current question ID: {q_id}")

        question = questions[module][q_id]
        next_q = None
        next_module = module

        import asyncio
        await asyncio.sleep(0.5)
    
    # Check for conditional navigation
    if 'if' in question:
        answer = data['answers'].get(f"{module}_{q_id}")

        print(f"DEBUG: Found conditional navigation. Answer: {answer}")

        if isinstance(answer, list) and answer:
            # For multiple_options, use the first selected option
            answer = answer[0]
        
        if answer in question['if']:
            next_q = question['if'][answer].get('id')
            print(f"DEBUG: Condition matched. Next question ID: {next_q}")
    
    # If no condition matched or no conditional navigation
    if not next_q:
        ids = sorted(list(questions[module].keys()))
        idx = ids.index(q_id)

        print(f"DEBUG: Current question index: {idx}, Total questions: {len(ids)}")

        if idx + 1 < len(ids):
            next_q = ids[idx + 1]
            print(f"DEBUG: Moving to next question in module: {next_q}")
        else:
            # End of current module
            if module == 'modul_1':
                next_module = 'modul_2'
                next_q = 1
                print(f"DEBUG: End of module 1, moving to module 2, question 1")
            else:
                print(f"DEBUG: End of survey, clearing state")
                # End of survey
                await message.answer("Опрос завершен! Спасибо за участие.")
                
                # Output answers for debugging
                answers = data['answers']
                await message.answer(f"Всего получено ответов: {len(answers)}")
                
                await state.clear()
                return
    
    print(f"DEBUG: Updating state - Module: {next_module}, Question ID: {next_q}, resetting level to 0")
    await state.update_data(
        current_module=next_module,
        current_question_id=next_q,
        current_level = 0
    )

    print(f"DEBUG: Calling ask_question")
    await ask_question(message, state)


@router.callback_query(F.data.startswith("level:"))
async def handle_level_option_select(callback: CallbackQuery, state: FSMContext):
    global question_lock
    
    if question_lock.locked():
        await callback.answer("Подождите, обрабатывается предыдущий ответ")
        return
    
    async with question_lock:
        hashed_opt = callback.data.split(":", 1)[1]
        data = await state.get_data()
        module = data['current_module']
        q_id = data['current_question_id']
        current_level = data.get('current_level', 0)

        print(f"DEBUG: Handling level option - Module: {module}, Question ID: {q_id}, Level: {current_level}")

        question = questions[module][q_id]
        
        if 'levels' not in question or current_level >= len(question['levels']):
            await callback.answer("Ошибка: уровень не найден")
            return

        level = question['levels'][current_level]
        
        # Определяем варианты ответов для текущего уровня
        if level['options'] == "options_scale":
            options = options_scale
        else:
            options = level['options']
        
        # Находим выбранный вариант
        original_opt = next(
            (opt for opt in options if get_callback_data(opt) == hashed_opt),
            None
        )

        print(f"DEBUG: Selected option: {original_opt}")
        
        if not original_opt:
            await callback.answer("Ошибка выбора!")
            return
        
        # Сохраняем ответ для текущего уровня
        answers = data['answers']
        key = f"{module}_{q_id}_level_{current_level}"
        answers[key] = original_opt
        
        # Переходим к следующему уровню или вопросу
        next_level = current_level + 1

        print(f"DEBUG: Next level would be: {next_level}, Total levels: {len(question['levels'])}")

        if next_level < len(question['levels']):
            print(f"DEBUG: Moving to next level: {next_level}")
            # Переходим к следующему уровню
            await state.update_data(answers=answers, current_level=next_level)
        else:
            print(f"DEBUG: All levels completed, moving to next question")
            key = f"{module}_{q_id}"
            answers[key] = "completed all levels"
            # Все уровни закончились, переходим к следующему вопросу
            await state.update_data(answers=answers, current_level=0)

        if next_level < len(question['levels']):
            should_go_to_next_level = True
        else:
            should_go_to_next_level = False
    
    if should_go_to_next_level:
        await ask_question(callback.message, state)
    else:
        await handle_next_question(callback.message, state)
        
    await callback.answer()