"""Загрузка данных опроса из JSON файла"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from app.data.data_models import SurveyData, Module, Question, Level


def _convert_to_level(level_data: Dict[str, Any]) -> Level:
    """Преобразует словарь в объект Level"""
    return Level(
        options=level_data.get("options", []),
        image=level_data.get("image"),
        height=level_data.get("height"),
        angle=level_data.get("angle"),
        surface=level_data.get("surface")
    )


def _convert_to_question(question_data: Dict[str, Any]) -> Question:
    """Преобразует словарь в объект Question"""
    levels = None
    if "levels" in question_data:
        levels = [_convert_to_level(level) for level in question_data["levels"]]

    return Question(
        id=question_data["id"],
        text=question_data["text"],
        type=question_data["type"],
        options=question_data.get("options"),
        levels=levels,
        if_conditions=question_data.get("if"),
        image=question_data.get("image")
    )


def load_survey_data(file_path: str) -> SurveyData:
    """
    Загружает данные опроса из JSON файла
    
    Args:
        file_path: Путь к JSON файлу
        
    Returns:
        SurveyData: Структурированные данные опроса
        
    Raises:
        FileNotFoundError: Если файл не найден
        ValueError: Если формат JSON некорректен
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            
            # Создаем модули с вопросами
            modules = {}
            for module_name in ["modul_1", "modul_2"]:
                if module_name in data:
                    questions = {q["id"]: _convert_to_question(q) for q in data[module_name]}
                    modules[module_name] = Module(questions=questions)
            
            # Создаем объект данных опроса
            return SurveyData(
                modules=modules,
                options_scale=data.get("options_scale", [])
            )
            
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл {file_path} не найден.")
    except json.JSONDecodeError:
        raise ValueError(f"Файл {file_path} содержит некорректный JSON.")
    except KeyError as e:
        raise ValueError(f"В файле отсутствует обязательное поле: {str(e)}")