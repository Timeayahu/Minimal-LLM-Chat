import json
from datetime import datetime
from pathlib import Path


LOGS_DIR = Path("logs")


def generate_session_name():
    """自动生成会话名称，格式：chat_年月日_时分秒。"""
    now = datetime.now()
    return now.strftime("chat_%Y%m%d_%H%M%S")


def load_history(session_name="default"):
    """
    加载指定会话的历史记录。

    参数：
        session_name: 会话名称（默认 "default"）

    返回：
        历史消息列表，如果不存在则返回 None

    数据流：
        session_name -> 生成文件路径 -> 读取 JSON -> 返回 list
    """
    file_path = LOGS_DIR / f"{session_name}.json"

    if not file_path.exists():
        return None

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_history(messages, session_name="default"):
    """
    保存消息列表到指定会话文件。

    参数：
        messages: 要保存的消息列表
        session_name: 会话名称（默认 "default"）

    数据流：
        session_name -> 生成文件路径 -> 创建目录 -> 写入 JSON
    """
    file_path = LOGS_DIR / f"{session_name}.json"
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=2)
