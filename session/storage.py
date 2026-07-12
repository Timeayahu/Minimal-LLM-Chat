import json
from datetime import datetime
from pathlib import Path
from typing import Any

from config import SYSTEM_PROMPT
from models import Message


LOGS_DIR = Path("logs")


def generate_session_name() -> str:
    """自动生成会话名称，格式：chat_年月日_时分秒_微秒。"""
    now = datetime.now()
    return now.strftime("chat_%Y%m%d_%H%M%S_%f")


def list_session_names() -> list[str]:
    """列出已经保存过的会话名称。"""
    if not LOGS_DIR.exists():
        return []

    return sorted(file_path.stem for file_path in LOGS_DIR.glob("*.json"))


def init_messages() -> list[Message]:
    """
    初始化全新的消息列表。

    返回：
        只包含 system prompt 的消息列表
    """
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def load_session_data(session_name: str) -> dict[str, Any] | None:
    """
    加载指定会话的完整快照。

    新格式是 dict，包含 name、messages、traces 等字段。
    旧格式是 list，只包含 messages；这里会自动转换成新格式。
    """
    file_path = LOGS_DIR / f"{session_name}.json"

    if not file_path.exists():
        return None

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list):
        return {
            "name": session_name,
            "messages": data,
            "traces": [],
        }

    return data


def save_session_data(session_data: dict[str, Any], session_name: str) -> None:
    """
    保存完整会话快照到指定会话文件。

    参数：
        session_data: JSON 可序列化的会话数据
        session_name: 会话名称
    """
    file_path = LOGS_DIR / f"{session_name}.json"
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(session_data, file, ensure_ascii=False, indent=2)
