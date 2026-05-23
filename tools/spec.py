from dataclasses import dataclass
from typing import Any, Callable


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

    @property #把方法伪装成属性使用
    def error_type(self) -> str | None:
        """兼容旧代码使用的 error_type 读取方式。"""
        if self.error is None:
            return None

        return self.error.kind

    @classmethod
    def success(cls, content: str) -> "ToolResult": # = ToolResult.success(ToolResult, "hi")
        """创建工具成功结果。"""
        return cls(ok=True, content=content)#返回的是类的实例化对象，cls=ToolResult

    @classmethod
    def failure(
        cls,
        content: str,
        error_type: str = "tool_error",
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


ToolFunc = Callable[[ToolArguments], ToolResult]


@dataclass
class ToolSpec:
    """一个工具的定义：它是谁、能做什么、怎么执行。"""

    name: str
    description: str
    func: ToolFunc
    parameters: dict[str, Any]
    strict: bool = True

    def run(self, arguments: ToolArguments) -> ToolResult:
        """执行工具函数。"""
        try:
            return self.func(arguments)
        except Exception as error:
            return ToolResult.failure(
                str(error),
                error_type="tool_exception",
                details={"exception_type": type(error).__name__},
            )

    def run_cli(self, args: list[str]) -> ToolResult:
        """把命令行参数转换成结构化参数后执行工具。"""
        properties = self.parameters.get("properties", {})

        if not properties:
            return self.run({})

        if len(properties) == 1:
            argument_name = next(iter(properties))
            return self.run({argument_name: " ".join(args)})

        return ToolResult.failure(
            f"{self.name} 工具暂不支持命令行手动传入多个结构化参数。",
            error_type="cli_arguments_error",
        )

    def to_openai_tool(self) -> dict[str, Any]:
        """转换成 OpenAI-compatible tools 参数需要的结构。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
                "strict": self.strict,
            },
        }
