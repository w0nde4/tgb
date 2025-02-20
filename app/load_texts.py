import json
from pathlib import Path

def load_texts(file_path: str) -> dict:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл {file_path} не найден.")
    except json.JSONDecodeError:
        raise ValueError(f"Файл {file_path} содержит некорректный JSON.")