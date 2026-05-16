import json
from datetime import datetime
from pathlib import Path

from models import Message, Session
from prompts import SYSTEM_PROMPT


LOGS_DIR = Path("logs")


def generate_session_name() -> str:
    """自动生成会话名称，格式：chat_年月日_时分秒。"""
    now = datetime.now()
    return now.strftime("chat_%Y%m%d_%H%M%S")


def load_history(session_name: str) -> list[Message] | None:
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


def ensure_system_prompt(messages: list[Message] | None) -> list[Message]:
    """确保消息列表包含最新的 system prompt。"""
    if not messages:
        return [{"role": "system", "content": SYSTEM_PROMPT}]

    if messages[0].get("role") == "system":
        messages[0]["content"] = SYSTEM_PROMPT
    else:
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    return messages


def init_messages(session_name: str) -> list[Message]:
    """
    初始化消息列表，加载指定会话的历史记录。

    参数：
        session_name: 要加载的会话名称

    返回：
        包含 system prompt 的消息列表
    """
    messages = load_history(session_name)

    return ensure_system_prompt(messages)


def create_session(session_name: str | None = None) -> Session:
    """创建一个会话；不传名称时自动生成新会话名。"""
    if session_name is None:
        session_name = generate_session_name()

    return {
        "name": session_name,
        "messages": init_messages(session_name),
    }


def check_current_chat_nums(current_memory: list[Message]) -> int:
    """统计当前消息列表里 user 消息的数量。"""
    return sum(1 for msg in current_memory if msg["role"] == "user")


def trim_messages(current_memory: list[Message], chat_limits: int) -> None:
    """
    记忆压缩：最多保留最近 chat_limits 轮对话。

    保留第 0 条 system prompt，每次删除最早的一轮 user + assistant。
    """
    while check_current_chat_nums(current_memory) > chat_limits:
        del current_memory[1:3]


def save_history(messages: list[Message], session_name: str) -> None:
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
