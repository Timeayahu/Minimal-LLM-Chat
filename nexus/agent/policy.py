"""Agent 工具请求的校验与确认策略。"""

from dataclasses import dataclass

from nexus.agent.errors import (
    ERROR_INVALID_TOOL_ARGUMENTS,
    ERROR_INVALID_TOOL_NAME,
    ERROR_UNKNOWN_TOOL,
)
from nexus.tools import ToolError, ToolSpec


@dataclass(frozen=True) # frozen=true: 对象字段初始化后不可再做更改
class ToolRequest:
    """已经通过 Agent 本地校验、可以等待确认或执行的工具请求。"""

    name: str
    arguments: dict
    tool: ToolSpec

    @property
    def requires_confirmation(self) -> bool:
        """返回该工具是否必须获得用户确认后才能执行。"""
        return self.tool.requires_confirmation


def resolve_tool_request(
    plan: dict,
    tools: dict[str, ToolSpec],
) -> ToolRequest | ToolError:
    """校验 上游planner 生成的工具计划，并解析成 ToolRequest 或结构化错误。
    核心包括三件事：
    1. 检查工具名称是否正确
    2. 根据名称查找真正注册的工具
    3. 检查上游生成的工具参数是否为字典
    
    
    """
    tool_name = plan.get("tool")
    if not isinstance(tool_name, str):
        return ToolError(
            kind=ERROR_INVALID_TOOL_NAME,
            message=f"工具计划里的 tool 字段必须是字符串：{plan}",
            retryable=True,
            details={"plan": plan},
        )

    tool = tools.get(tool_name)
    if tool is None:
        return ToolError(
            kind=ERROR_UNKNOWN_TOOL,
            message=f"模型选择了未知工具：{tool_name}",
            retryable=True,
            details={"available_tools": list(tools.keys())},
        )

    arguments = plan.get("arguments", {})
    if not isinstance(arguments, dict):
        return ToolError(
            kind=ERROR_INVALID_TOOL_ARGUMENTS,
            message=f"工具参数必须是 dict：{plan}",
            retryable=True,
            details={"plan": plan},
        )

    return ToolRequest(name=tool_name, arguments=arguments, tool=tool)
