from dataclasses import dataclass
from typing import Any, Callable


ToolArguments = dict[str, Any]


@dataclass
class ToolResult:
    """工具执行后的结构化结果。"""

    ok: bool
    content: str
    error_type: str | None = None

    @classmethod
    def success(cls, content: str) -> "ToolResult": # = ToolResult.success(ToolResult, "hi")
        """创建工具成功结果。"""
        return cls(ok=True, content=content)#返回的是类的实例化对象，cls=ToolResult

    @classmethod
    def failure(cls, content: str, error_type: str = "tool_error") -> "ToolResult":
        """创建工具失败结果。"""
        return cls(ok=False, content=content, error_type=error_type)

    def to_text(self) -> str:
        """转换成适合展示或交给模型的文本。"""
        if self.ok:
            return self.content

        return f"工具执行失败：{self.content}"


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
            return ToolResult.failure(str(error), error_type=type(error).__name__)

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
