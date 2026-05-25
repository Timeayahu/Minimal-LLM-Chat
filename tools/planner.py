import json
from typing import Any

from llm_client import ask_llm
from tools.error_codes import ERROR_PLANNER_INVALID_JSON
from tools.spec import ToolSpec


def decide_tool_call(user_input: str, tools: dict[str, ToolSpec]) -> dict[str, Any]:
    """
    让模型判断是否需要调用工具。

    返回值示例：
    - {"tool": "time", "arguments": {}}
    - {"tool": "echo", "arguments": {"text": "hello"}}
    - {"tool": None, "answer": "不需要工具时的直接回答"}
    """
    tool_lines = [] #实际传入的工具说明表（name, description, parameters）
    for tool in tools.values():
        parameters_json = json.dumps(tool.parameters.to_dict(), ensure_ascii=False)
        tool_lines.append(
            f"- {tool.name}: {tool.description}\n"
            f"  参数 schema: {parameters_json}"
        )

    messages = [
        {
            "role": "system",
            "content": (
                "你是一个工具调用规划器。"
                "你只能输出 JSON，不要输出 Markdown，不要解释。"
                "如果用户问题需要工具，输出："
                '{"tool": "工具名", "arguments": {"参数名": "参数值"}}。'
                "如果不需要工具，输出："
                '{"tool": null, "answer": "直接回答"}。'
                "arguments 必须符合对应工具的参数 schema。"
            ),
        },
        {
            "role": "user",
            "content": (
                "可用工具：\n"
                + "\n".join(tool_lines)
                + f"\n\n用户问题：{user_input}"
            ),
        },
    ]

    raw_answer = ask_llm(messages)

    try:
        return json.loads(raw_answer)
    except json.JSONDecodeError:
        return {
            "tool": None,
            "answer": f"模型没有返回合法 JSON：{raw_answer}",
            "error": {
                "kind": ERROR_PLANNER_INVALID_JSON,
                "message": "模型没有返回合法 JSON 工具计划。",
                "details": {"raw_answer": raw_answer},
            },
        }


def decide_agent_step(
    user_input: str,
    tools: dict[str, ToolSpec],
    observations: list[str],
) -> dict[str, Any]:
    """
    让模型决定 Agent Loop 的下一步。

    返回值示例：
    - {"action": "tool", "tool": "time", "arguments": {}}
    - {"action": "final", "answer": "最终回答"}
    """
    tool_lines = []
    for tool in tools.values():
        parameters_json = json.dumps(tool.parameters.to_dict(), ensure_ascii=False)
        safety_text = (
            f"只读: {tool.is_readonly}; "
            f"需要确认: {tool.requires_confirmation}; "
            f"超时秒数: {tool.timeout_seconds}"
        )
        tool_lines.append(
            f"- {tool.name}: {tool.description}\n"
            f"  参数 schema: {parameters_json}\n"
            f"  安全边界: {safety_text}"
        )

    if observations:
        observation_text = "\n".join(
            f"{index}. {observation}"
            for index, observation in enumerate(observations, start=1)
        )
    else:
        observation_text = "暂无。"

    messages = [
        {
            "role": "system",
            "content": (
                "你是一个多步 Agent Loop 规划器。"
                "你只能输出 JSON，不要输出 Markdown，不要解释。"
                "每一步只能选择一个动作。"
                "如果还需要调用工具，输出："
                '{"action": "tool", "tool": "工具名", "arguments": {"参数名": "参数值"}}。'
                "如果已有足够信息回答用户，输出："
                '{"action": "final", "answer": "最终回答"}。'
                "arguments 必须符合对应工具的参数 schema。"
                "不要重复调用已经得到足够观察结果的工具。"
            ),
        },
        {
            "role": "user",
            "content": (
                "可用工具：\n"
                + "\n".join(tool_lines)
                + f"\n\n用户问题：{user_input}"
                + f"\n\n已有观察结果：\n{observation_text}"
            ),
        },
    ]

    raw_answer = ask_llm(messages)

    try:
        return json.loads(raw_answer)
    except json.JSONDecodeError:
        return {
            "action": "final",
            "answer": f"模型没有返回合法 JSON：{raw_answer}",
            "error": {
                "kind": ERROR_PLANNER_INVALID_JSON,
                "message": "模型没有返回合法 JSON Agent 步骤。",
                "details": {"raw_answer": raw_answer},
            },
        }


def answer_with_tool_result(user_input: str, tool_name: str, tool_result: str) -> str:
    """把工具执行结果交回模型，让模型组织最终回答。"""
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个 AI 助手。"
                "用户的问题已经通过工具得到结果。"
                "请基于工具结果回答用户，不要编造工具结果之外的信息。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"用户问题：{user_input}\n"
                f"工具名称：{tool_name}\n"
                f"工具结果：{tool_result}"
            ),
        },
    ]

    return ask_llm(messages)
