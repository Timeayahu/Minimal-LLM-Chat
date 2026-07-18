from dataclasses import dataclass
from typing import Any, Callable


ERROR_CLI_ARGUMENTS = "cli_arguments_error"
ERROR_INVALID_ARGUMENTS = "invalid_arguments"
ERROR_INVALID_TOOL_SCHEMA = "invalid_tool_schema"
ERROR_TOOL = "tool_error"
ERROR_TOOL_EXCEPTION = "tool_exception"

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
        """转换成适合写入 TraceEvent 和 JSON 的数据。"""
        return {
            "kind": self.kind,
            "message": self.message,
            "retryable": self.retryable,
            "user_visible": self.user_visible,
            "details": self.details or {},
        }

    def to_text(self) -> str:
        """转换成适合展示给用户的失败文本。"""
        return f"工具执行失败：{self.message}"


@dataclass
class ToolResult:
    """工具执行后的结构化成功或失败结果。"""

    ok: bool
    content: str
    error: ToolError | None = None

    @property
    def error_type(self) -> str | None:
        """兼容旧代码使用的 error_type 读取方式。"""
        return self.error.kind if self.error else None

    @classmethod
    def success(cls, content: str) -> "ToolResult":
        """用工具输出文本创建 `ok=True` 且不包含 ToolError 的成功结果。"""
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
        """把错误类型、文本和可重试信息封装为 `ok=False` 的结构化失败结果。"""
        return cls(
            ok=False,
            content=content,
            error=ToolError(
                kind=error_type,
                message=content,
                retryable=retryable,
                user_visible=user_visible,
                details=details,
            ),
        )

    def to_text(self) -> str:
        """转换成适合展示或交给模型的文本。"""
        if self.ok:
            return self.content
        return self.error.to_text() if self.error else f"工具执行失败：{self.content}"


ToolFunc = Callable[[ToolArguments], ToolResult]


ToolPropertySchema = dict[str, Any]


@dataclass
class ToolParameters:
    """一个工具的参数 schema。

    ToolParameters 描述一个工具允许接收什么参数。它有两个工程作用：

    1. 给 planner / 模型看：让模型知道应该生成哪些 arguments。
    2. 给本地执行前校验用：ToolSpec.validate_arguments() 会根据它检查参数
       是否缺失、是否多传、类型是否匹配。

    字段说明：

    - properties:
      参数字段定义表。key 是参数名，value 是该参数的 schema 描述，例如：

      {
          "text": {
              "type": "string",
              "description": "要原样返回的文本。",
          }
      }

      properties 决定了工具“认识哪些参数”，也提供每个参数的类型、说明等信息。
      planner 会把它作为参数生成依据；validate_arguments() 会用它检查未知参数
      和参数类型。

    - required:
      必填参数列表。这里保存的是 properties 里的参数名，例如 ["text"]。
      如果 arguments 缺少 required 里的字段，validate_arguments() 会返回
      ERROR_INVALID_ARGUMENTS，而不会真正执行工具函数。

    - additional_properties:
      是否允许传入 properties 之外的额外参数。
    
      False 表示参数必须严格限制在 properties 定义的范围内；如果模型多生成了
      不认识的字段，本地校验会拒绝执行。这个默认值更适合工具调用场景，因为
      Agent 的工具参数应该明确、可控、可复盘。

      True 表示允许额外参数，适合少数“透传型”或“开放配置型”工具。但开启后
      工具函数自己就需要承担更多校验责任。

    - schema_type:
      参数 schema 的顶层类型。当前工具系统期望顶层是 "object"，也就是工具参数
      应该是一组命名字段组成的 dict。
      这个字段保留为可配置，是为了让 schema 表达更完整；但当前
      validate_arguments() 只支持 object 作为顶层结构。如果不是 "object"，
      会返回 ERROR_INVALID_TOOL_SCHEMA，避免工具在不受支持的参数结构下执行。
    """

    properties: dict[str, ToolPropertySchema]
    required: list[str]
    additional_properties: bool = False
    schema_type: str = "object"

    def to_dict(self) -> dict[str, Any]:
        """转换成 OpenAI-compatible tool parameters 需要的 dict。"""
        return {
            "type": self.schema_type,
            "properties": self.properties,
            "required": self.required,
            "additionalProperties": self.additional_properties,
        }


@dataclass
class ToolSpec:
    """一个工具的定义：它是谁、能做什么、怎么执行。

    字段说明：

    - name: 
      工具名。planner 会输出这个名字，Agent 也会用这个名字从工具注册表里
      找到对应工具，所以它是工具调用的稳定标识。

    - description: 
      给模型看的工具说明。planner 会根据 description 判断什么时候该选这个工具。

    - func: 
      真正执行工具逻辑的函数。ToolSpec.run() 校验参数通过后，会调用它。

    - parameters: 
      工具参数 schema。它同时服务两件事：一是告诉模型应该生成什么参数；
      二是让 ToolSpec.validate_arguments() 在执行前做最小参数校验。

    - strict: 
      是否要求模型严格遵守 parameters 描述的 schema。这个字段主要用于
      转换成 OpenAI-compatible tool 定义时的 strict 标记，表示工具调用
      参数应该尽量严格匹配 schema。

      在当前项目里，strict 不直接参与 ToolSpec.run() 的本地校验；真正的
      本地校验由 validate_arguments() 完成。可以把 strict 理解成“给模型
      和上游工具调用协议看的约束”，而 validate_arguments() 是“本程序自己
      执行前的防线”。

    - is_readonly: 
      工具是否只读。只读工具通常不会修改外部状态，比如查询时间；非只读工具
      可能写文件、发请求、删除数据。planner 可以把它作为安全边界信息使用。

    - requires_confirmation:
      工具执行前是否需要用户确认。适合用在有副作用、可能敏感、或者教学阶段
      想让用户明确观察工具调用的场景。

    - timeout_seconds:
      工具执行超时时间，单位是秒。它的设计目的是防止工具长时间卡住，比如网络
      请求、文件处理、外部命令等。
      当前项目里 timeout_seconds 只是工具定义中的元信息，还没有真正接入
      ToolSpec.run() 的超时控制。也就是说，它现在会被 planner 看到，作为
      工具安全边界的一部分，但还不会自动中断运行中的工具。后续如果要工程化，
      可以在 ToolSpec.run() 或工具执行器层统一实现超时。
    """

    name: str
    description: str
    func: ToolFunc
    parameters: ToolParameters
    strict: bool = True
    is_readonly: bool = True
    requires_confirmation: bool = False
    timeout_seconds: int | None = None

    def run(self, arguments: ToolArguments) -> ToolResult:
        """先按 ToolParameters 校验结构化参数，通过后执行工具并将异常转为 ToolResult。"""
        validation_error = self.validate_arguments(arguments)
        if validation_error is not None:
            return validation_error

        try:
            return self.func(arguments)
        except Exception as error:
            return ToolResult.failure(
                str(error),
                error_type=ERROR_TOOL_EXCEPTION,
                details={"exception_type": type(error).__name__},
            )

    def run_cli(self, args: list[str]) -> ToolResult:
        """把命令行参数转换成结构化参数后执行工具。"""
        properties = self.parameters.properties

        if not properties:
            return self.run({})

        if len(properties) == 1:
            argument_name = next(iter(properties))
            return self.run({argument_name: " ".join(args)})

        return ToolResult.failure(
            f"{self.name} 工具暂不支持命令行手动传入多个结构化参数。",
            error_type=ERROR_CLI_ARGUMENTS,
        )

    def validate_arguments(self, arguments: ToolArguments) -> ToolResult | None:
        """根据当前工具的 parameters 做最小参数校验。"""
        schema_type = self.parameters.schema_type
        if schema_type != "object":
            return ToolResult.failure(
                f"{self.name} 工具的参数 schema 顶层 type 必须是 object。",
                error_type=ERROR_INVALID_TOOL_SCHEMA,
                details={"schema": self.parameters.to_dict()},
            )

        properties = self.parameters.properties
        required = self.parameters.required
        missing_names = [name for name in required if name not in arguments]
        if missing_names:
            return ToolResult.failure(
                f"{self.name} 工具缺少必填参数：{', '.join(missing_names)}。",
                error_type=ERROR_INVALID_ARGUMENTS,
                retryable=True,
                details={"missing": missing_names},
            )

        if not self.parameters.additional_properties:
            extra_names = [name for name in arguments if name not in properties]
            if extra_names:
                return ToolResult.failure(
                    f"{self.name} 工具收到了不支持的参数：{', '.join(extra_names)}。",
                    error_type=ERROR_INVALID_ARGUMENTS,
                    retryable=True,
                    details={"extra": extra_names},
                )

        for name, value in arguments.items():
            property_schema = properties.get(name)
            if not isinstance(property_schema, dict):
                continue

            expected_type = property_schema.get("type")
            if not _matches_json_schema_type(value, expected_type):
                return ToolResult.failure(
                    f"{self.name} 工具参数 {name} 类型错误，期望 {expected_type}。",
                    error_type=ERROR_INVALID_ARGUMENTS,
                    retryable=True,
                    details={
                        "argument": name,
                        "expected_type": expected_type,
                        "actual_type": type(value).__name__,
                    },
                )

        return None

    def to_openai_tool(self) -> dict[str, Any]:
        """转换成 OpenAI-compatible tools 参数需要的结构。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters.to_dict(),
                "strict": self.strict,
            },
        }


def _matches_json_schema_type(value: Any, expected_type: Any) -> bool:
    """检查 Python 值是否符合最小 JSON Schema type。"""
    if expected_type is None:
        return True

    if isinstance(expected_type, list):
        return any(_matches_json_schema_type(value, item) for item in expected_type)

    if expected_type == "string":
        return isinstance(value, str)

    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)

    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    if expected_type == "boolean":
        return isinstance(value, bool)

    if expected_type == "object":
        return isinstance(value, dict)

    if expected_type == "array":
        return isinstance(value, list)

    if expected_type == "null":
        return value is None

    return True
