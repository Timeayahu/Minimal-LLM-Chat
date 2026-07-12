"""工具执行相关的核心数据结构。

ToolResult / ToolError 是纯数据模型，不依赖具体工具实现，
所以放在 models 包，供 tools（定义/执行）和 agent（编排/记录）共用。
"""

from dataclasses import dataclass
from typing import Any, Callable

from models.errors import ERROR_TOOL, ERROR_TOOL_EXCEPTION


ToolArguments = dict[str, Any]


@dataclass
class ToolError:
    """工具失败时的结构化错误。"""

    kind: str
    message: str
    retryable: bool = False
    user_visible: bool = True
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """转换成适合写入 trace / JSON 的数据。"""
        return {
            "kind": self.kind,
            "message": self.message,
            "retryable": self.retryable,
            "user_visible": self.user_visible,
            "details": self.details or {},
        }

    def to_text(self) -> str:
        """转换成适合展示给用户的文本。"""
        return f"工具执行失败：{self.message}"


@dataclass
class ToolResult:
    """工具执行后的结构化结果。"""

    ok: bool
    content: str
    error: ToolError | None = None

    @property  # 把方法伪装成属性使用
    def error_type(self) -> str | None:
        """兼容旧代码使用的 error_type 读取方式。"""
        if self.error is None:
            return None

        return self.error.kind

    @classmethod
    def success(cls, content: str) -> "ToolResult":
        """创建工具成功结果。"""
        return cls(ok=True, content=content)

    @classmethod
    def failure(
        cls,
        content: str,
        error_type: str = ERROR_TOOL,
        retryable: bool = False,
        user_visible: bool = True,
        details: dict[str, Any] | None = None,
    ) -> "ToolResult":
        """创建工具失败结果。"""
        error = ToolError(
            kind=error_type,
            message=content,
            retryable=retryable,
            user_visible=user_visible,
            details=details,
        )
        return cls(ok=False, content=content, error=error)

    def to_text(self) -> str:
        """转换成适合展示或交给模型的文本。"""
        if self.ok:
            return self.content

        if self.error is None:
            return f"工具执行失败：{self.content}"

        return self.error.to_text()


ToolFunc = Callable[[ToolArguments], "ToolResult"]
