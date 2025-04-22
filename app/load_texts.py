import json
from pathlib import Path

def load_texts(file_path: str) -> tuple:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            options_scale = data.get('options_scale', [])
            questions = {
                'modul_1': {q['id']: q for q in data['modul_1']},
                'modul_2': {q['id']: q for q in data['modul_2']}
            }
            return (data, options_scale, questions)
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл {file_path} не найден.")
    except json.JSONDecodeError:
        raise ValueError(f"Файл {file_path} содержит некорректный JSON.")