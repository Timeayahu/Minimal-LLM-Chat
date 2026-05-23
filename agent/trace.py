"""Agent 运行过程中的 trace 数据结构。"""

from typing import Any, TypedDict


class ToolErrorData(TypedDict):
    """一次工具错误的可保存数据。"""

    kind: str
    message: str
    retryable: bool
    user_visible: bool
    details: dict[str, Any]


class ToolTrace(TypedDict):
    """一次工具调用记录。"""

    created_at: str
    user_input: str
    tool_name: str
    arguments: dict[str, Any]
    ok: bool
    content: str
    error: ToolErrorData | None
    final_answer: str
