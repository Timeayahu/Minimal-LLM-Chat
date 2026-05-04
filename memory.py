import json
from pathlib import Path


HISTORY_FILE = Path("logs/history.json")


def load_history(): #path -> textio -> list
    if not HISTORY_FILE.exists():
        return None

    with HISTORY_FILE.open("r", encoding="utf-8") as file: #TextIOWrapper
        
        return json.load(file) # change to list obj


def save_history(messages): #上一个过程反过来
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with HISTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=2)
