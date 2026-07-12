import json
from typing import Any

from llm import ask_llm
from models.errors import ERROR_PLANNER_INVALID_JSON
from tools.spec import ToolSpec


def decide_agent_step(
    user_input: str,
    tools: dict[str, ToolSpec],
    observations: list[str],
    long_term_memory_text: str = "暂无长期记忆。",
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
                + f"\n\n长期记忆：\n{long_term_memory_text}"
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
