"""Фабрика клавиатур для бота"""
from typing import List, Optional
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from app.data.encoder import create_callback
from app.data.data_models import Question, Level


class KeyboardFactory:
    """Фабрика для создания клавиатур"""
    
    @staticmethod
    def create_single_option_markup(question: Question) -> InlineKeyboardMarkup:
        """
        Создает клавиатуру с одиночным выбором
        
        Args:
            question: Объект вопроса
            
        Returns:
            InlineKeyboardMarkup: Клавиатура с вариантами ответов
        """
        builder = InlineKeyboardBuilder()
        
        if question.options:
            for opt in question.options:
                builder.button(
                    text=opt,
                    callback_data=create_callback("single", opt)
                )
        
        builder.adjust(1)  # По одной кнопке в ряду
        return builder.as_markup()
    
    @staticmethod
    def create_multiple_options_markup(question: Question, selected: Optional[List[str]] = None) -> InlineKeyboardMarkup:
        """
        Создает клавиатуру с множественным выбором
        
        Args:
            question: Объект вопроса
            selected: Список выбранных опций
            
        Returns:
            InlineKeyboardMarkup: Клавиатура с вариантами ответов
        """
        if selected is None:
            selected = []
            
        builder = InlineKeyboardBuilder()
        
        if question.options:
            for opt in question.options:
                builder.button(
                    text=f"{'✅ ' if opt in selected else ''}{opt}",
                    callback_data=create_callback("multi", opt)
                )
        
        builder.button(text="✔️ Готово", callback_data="multi_submit")
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def create_level_option_markup(level: Level, options: List[str]) -> InlineKeyboardMarkup:
        """
        Создает клавиатуру для уровня вопроса
        
        Args:
            level: Объект уровня
            options: Список вариантов ответов
            
        Returns:
            InlineKeyboardMarkup: Клавиатура с вариантами ответов
        """
        builder = InlineKeyboardBuilder()
        
        for opt in options:
            builder.button(
                text=opt,
                callback_data=create_callback("level", opt)
            )
        
        builder.adjust(1)
        return builder.as_markup()