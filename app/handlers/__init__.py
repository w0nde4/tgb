
"""Инициализация роутеров и обработчиков"""
from aiogram import Router

from app.handlers import base, question, level

# Регистрация обработчиков в главном роутере
router = Router()
router.include_router(base.router)
router.include_router(question.router)
router.include_router(level.router)