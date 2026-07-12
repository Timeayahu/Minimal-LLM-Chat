"""会话层：当前对话窗口（Session）及其文件持久化。

与 memory 包区分：session 负责单次会话的消息窗口与 trace，
memory 负责跨会话的长期记忆。
"""

from session.session import Session
from session.storage import (
    generate_session_name,
    init_messages,
    list_session_names,
    load_session_data,
    save_session_data,
)

__all__ = [
    "Session",
    "generate_session_name",
    "init_messages",
    "list_session_names",
    "load_session_data",
    "save_session_data",
]
