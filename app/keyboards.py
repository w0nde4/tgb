from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.encoder import get_callback_data
from app.load_texts import load_texts

(data, options_scale, questions) = load_texts(r'app\ovz.json')


def create_single_option_markup(question):
    builder = InlineKeyboardBuilder()
    
    if 'options' in question:
        for opt in question['options']:
            callback_data = f"single:{get_callback_data(opt)}"
            print(f"Creating button: {opt} with callback: {callback_data}")  # Отладка
            builder.button(
                text=opt,
                callback_data=callback_data
            )
    
    builder.adjust(1)
    return builder.as_markup()


def create_multiple_options_markup(question, selected=None):
    if selected is None:
        selected = []
        
    builder = InlineKeyboardBuilder()
    
    for opt in question['options']:
        builder.button(
            text=f"{'✅ ' if opt in selected else ''}{opt}",
            callback_data=f"multi:{get_callback_data(opt)}"
        )
    
    builder.button(text="✔️ Готово", callback_data="multi_submit")
    builder.adjust(1)
    return builder.as_markup()


def create_level_option_markup(level):
    """Create inline keyboard markup for a level within a question"""
    builder = InlineKeyboardBuilder()
    
    # Определяем варианты ответов для уровня
    if level['options'] == "options_scale":
        options = options_scale
    else:
        options = level['options']
    
    for opt in options:
        builder.button(
            text=opt,
            callback_data=f"level:{get_callback_data(opt)}"
        )
    
    builder.adjust(1)
    return builder.as_markup()