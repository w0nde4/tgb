"""Функции для кодирования callback данных"""
import hashlib
from typing import Any


def get_callback_data(text: str) -> str:
    """
    Создаёт хеш для использования в качестве callback_data
    
    Args:
        text: Текст для хеширования
        
    Returns:
        str: Хеш длиной 16 символов
    """
    if not isinstance(text, str):
        text = str(text)
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def create_callback(prefix: str, value: Any) -> str:
    """
    Создаёт callback строку с префиксом
    
    Args:
        prefix: Префикс для callback data
        value: Значение для хеширования
        
    Returns:
        str: Callback data в формате "prefix:hash"
    """
    return f"{prefix}:{get_callback_data(str(value))}"