"""Построитель сообщений для опроса"""
from typing import Optional, Union
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup

from app.data.data_models import Level, Question
from app.services.image_service import ImageService

import logging

logger = logging.getLogger(__name__)


class MessageBuilder:
    """Класс для построения сообщений с вопросами"""
    
    def __init__(self, image_service: ImageService):
        """
        Инициализирует построитель сообщений
        
        Args:
            image_service: Сервис для работы с изображениями
        """
        self.image_service = image_service
    
    async def send_level_message(
        self, 
        message: Message, 
        level: Level, 
        level_text: str, 
        markup: InlineKeyboardMarkup
    ) -> Message:
        """
        Отправляет сообщение для уровня вопроса
        
        Args:
            message: Объект сообщения для ответа
            level: Объект уровня
            level_text: Текст уровня
            markup: Клавиатура
            
        Returns:
            Message: Отправленное сообщение
        """
        if level.image and self.image_service.has_image(level.image):
            return await message.answer_photo(
                photo=self.image_service.get_image(level.image),
                caption=level_text,
                reply_markup=markup
            )
        else:
            return await message.answer(
                text=level_text,
                reply_markup=markup
            )
    
    async def send_question_message(
    self, 
    message: Message, 
    question: Question, 
    markup: InlineKeyboardMarkup,
    current_level: Optional[int] = None,
    level_text: Optional[str] = None
) -> Message:
        """
        Отправляет сообщение с вопросом
        
        Args:
            message: Объект сообщения для ответа
            question: Объект вопроса
            markup: Клавиатура
            current_level: Текущий уровень для вопросов с уровнями
            level_text: Текст для уровня (если применимо)
            
        Returns:
            Message: Отправленное сообщение
        """
         # --- Вопрос с уровнями ---
        if question.levels and current_level is not None and 0 <= current_level < len(question.levels):
            level = question.levels[current_level]

            if not level_text:
                level_text = f"{question.text}\n\n" if current_level == 0 else ""
                if level.height:
                    level_text += f"• {level.height}"
                elif level.angle:
                    level_text += f"• {level.angle}"
                elif level.surface:
                    level_text += f"• {level.surface}"

            # Если на первом уровне есть общее изображение — присылаем его
            if current_level == 0 and question.image and self.image_service.has_image(question.image):
                return await message.answer_photo(
                    photo=self.image_service.get_image(question.image),
                    caption=level_text,
                    reply_markup=markup
                )

            # Иначе как обычный уровень
            return await self.send_level_message(message, level, level_text, markup)

        # --- Обычный вопрос без уровней ---
        # Если у вопроса есть изображение — присылаем с caption
        if question.image:
            if self.image_service.has_image(question.image):
                return await message.answer_photo(
                    photo=self.image_service.get_image(question.image),
                    caption=question.text,
                    reply_markup=markup
                )
            else:
                logger.warning(f"Изображение не найдено в кеше: {question.image}")

        # Обработка уровней (без current_level), если они есть (например, для сбора изображений)
        level_texts = []
        level_images = []
        if question.levels:
            for level in question.levels:
                if level.height:
                    level_texts.append(f"• {level.height}")
                elif level.angle:
                    level_texts.append(f"• {level.angle}")
                elif level.surface:
                    level_texts.append(f"• {level.surface}")
                if level.image:
                    level_images.append(level.image)

            # Удаляем дубликаты, сохраняем порядок
            unique_images = list(dict.fromkeys(level_images))
            for img in unique_images:
                if self.image_service.has_image(img):
                    await message.answer_photo(photo=self.image_service.get_image(img))
                else:
                    logger.warning(f"Уровневое изображение не найдено в кеше: {img}")

        # Отправляем текст вопроса с вариантами
        full_text = question.text
        if level_texts:
            full_text += "\n\n" + "\n".join(level_texts)

        return await message.answer(full_text, reply_markup=markup)