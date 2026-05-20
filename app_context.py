from typing import Any, TypedDict

from memory import Session
from tools.spec import ToolSpec


class AppContext(TypedDict):
    """命令执行时能访问的应用上下文。"""

    session: Session
    commands: dict[str, Any]
    tools: dict[str, ToolSpec]
