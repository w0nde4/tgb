"""Сервис для работы с изображениями"""
import os
from typing import Dict, Optional
from aiogram.types import FSInputFile
import logging

logger = logging.getLogger(__name__)


class ImageService:
    """Сервис для кеширования и получения изображений"""
    
    def __init__(self, images_dir: str):
        self.images_dir = images_dir
        self.image_cache = {}
        self._load_images()

    def _load_images(self):
        if not os.path.exists(self.images_dir):
            logger.warning(f"Папка с изображениями не найдена: {self.images_dir}")
            return
        
        for filename in os.listdir(self.images_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.jfif')):
                path = os.path.join(self.images_dir, filename)
                try:
                    key = filename.lower()
                    self.image_cache[key] = FSInputFile(path)
                    logger.info(f"Кешировано изображение: {key}")
                except Exception as e:
                    logger.error(f"Ошибка кеширования {filename}: {e}")

    def has_image(self, filename: str) -> bool:
        key = filename.lower()
        exists = key in self.image_cache
        logger.info(f"Проверка изображения '{key}': {'найдено' if exists else 'не найдено'}")
        return exists

    def get_image(self, filename: str) -> Optional[FSInputFile]:
        key = filename.lower()
        img = self.image_cache.get(key)
        if img is None:
            logger.warning(f"Изображение '{key}' не найдено в кеше")
        return img
    
    def has_image(self, filename: str) -> bool:
        """
        Проверяет наличие изображения в кеше
        
        Args:
            filename: Имя файла изображения
            
        Returns:
            bool: True, если изображение есть в кеше
        """
        return filename in self.image_cache