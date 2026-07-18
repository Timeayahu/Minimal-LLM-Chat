from datetime import datetime
from typing import Any

from nexus.tools.core import ERROR_INVALID_ARGUMENTS, ToolResult


def get_current_time(arguments: dict[str, Any]) -> ToolResult:
    """拒绝非空参数；无参数时把当前本地时间格式化并返回成功 ToolResult。"""
    if arguments:
        return ToolResult.failure(
            "time 工具暂时不需要参数。",
            error_type=ERROR_INVALID_ARGUMENTS,
            retryable=True,
        )

    now = datetime.now()
    return ToolResult.success(now.strftime("%Y-%m-%d %H:%M:%S"))


def echo_text(arguments: dict[str, Any]) -> ToolResult:
    """把收到的参数原样返回，方便观察工具参数。"""
    text = arguments.get("text")
    if not isinstance(text, str) or not text:
        return ToolResult.failure(
            "echo 工具需要 text 参数。",
            error_type=ERROR_INVALID_ARGUMENTS,
            retryable=True,
        )

    return ToolResult.success(text)
