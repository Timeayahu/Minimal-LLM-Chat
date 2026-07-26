"""Agent Planner 与 Runtime 共享的动作协议和解析边界。"""

import json
from dataclasses import dataclass
from typing import Any, Literal, TypeAlias, TypedDict

from nexus.agent.errors import (
    ERROR_INVALID_AGENT_ACTION,
    ERROR_INVALID_FINAL_ANSWER,
    ERROR_INVALID_TOOL_ARGUMENTS,
    ERROR_INVALID_TOOL_NAME,
    ERROR_PLANNER_INVALID_JSON,
)


ACTION_TOOL = "tool"
ACTION_FINAL = "final"
AGENT_ACTION_NAMES = (ACTION_TOOL, ACTION_FINAL)


class ToolAction(TypedDict):
    """请求 Runtime 调用一个工具。"""

    action: Literal["tool"]
    tool: str
    arguments: dict[str, Any]


class FinalAction(TypedDict):
    """请求 Runtime 返回最终回答。"""

    action: Literal["final"]
    answer: str


AgentAction: TypeAlias = ToolAction | FinalAction


@dataclass(frozen=True)
class AgentActionParseError:
    """Planner 输出无法解析成合法 AgentAction 时的结构化错误。"""

    kind: str
    message: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """转换成 RunRecorder 可持久化的错误结构。"""
        return {
            "kind": self.kind,
            "message": self.message,
            "details": self.details,
        }


def parse_agent_action(payload: str | object) -> AgentAction | AgentActionParseError:
    """集中完成 JSON 解析、动作白名单和动作字段校验。"""
    raw_payload = payload
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return AgentActionParseError(
                kind=ERROR_PLANNER_INVALID_JSON,
                message="模型没有返回合法 JSON Agent 步骤。",
                details={"raw_answer": raw_payload},
            )

    if not isinstance(payload, dict):
        return AgentActionParseError(
            kind=ERROR_INVALID_AGENT_ACTION,
            message="Agent 步骤必须是 JSON object。",
            details={"payload": payload},
        )

    # 兼容旧版 Planner 返回的 {"error": {...}} 信封，避免升级期间把失败误当 final。
    legacy_error = payload.get("error")
    if isinstance(legacy_error, dict):
        details = legacy_error.get("details")
        return AgentActionParseError(
            kind=str(legacy_error.get("kind") or ERROR_INVALID_AGENT_ACTION),
            message=str(legacy_error.get("message") or "Agent 动作解析失败。"),
            details=details if isinstance(details, dict) else {"plan": payload},
        )

    action = payload.get("action")
    if action == ACTION_FINAL:
        answer = payload.get("answer")
        if not isinstance(answer, str) or not answer:
            return AgentActionParseError(
                kind=ERROR_INVALID_FINAL_ANSWER,
                message="final 动作的 answer 必须是非空字符串。",
                details={"plan": payload},
            )
        return {"action": ACTION_FINAL, "answer": answer}

    if action == ACTION_TOOL:
        tool_name = payload.get("tool")
        if not isinstance(tool_name, str) or not tool_name:
            return AgentActionParseError(
                kind=ERROR_INVALID_TOOL_NAME,
                message="tool 动作的 tool 必须是非空字符串。",
                details={"plan": payload},
            )

        if "arguments" not in payload or not isinstance(payload["arguments"], dict):
            return AgentActionParseError(
                kind=ERROR_INVALID_TOOL_ARGUMENTS,
                message="tool 动作的 arguments 必须是 JSON object。",
                details={"plan": payload},
            )

        return {
            "action": ACTION_TOOL,
            "tool": tool_name,
            "arguments": payload["arguments"],
        }

    return AgentActionParseError(
        kind=ERROR_INVALID_AGENT_ACTION,
        message=f"Agent 步骤里的 action 必须是 {' 或 '.join(AGENT_ACTION_NAMES)}。",
        details={"plan": payload},
    )
