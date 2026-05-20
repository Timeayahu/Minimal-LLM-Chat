from datetime import datetime

from app_context import AppContext
from chat import handle_chat_message
from config import MAX_HISTORY_ROUNDS
from tools.planner import answer_with_tool_result, decide_tool_call


def handle_agent_message(context: AppContext, user_input: str) -> None:
    """处理普通用户输入，并由 Agent 判断是否需要调用工具。
    
    1. decide_tool_call: 决定是否调用
    2. 若调用，判断边界情况，无问题就执行tool
    3. 把执行结果，用户输入，和工具一起发给模型，得到最终回复
     
    """

    session = context["session"]
    tools = context["tools"]
    plan = decide_tool_call(user_input, tools)
    tool_name = plan.get("tool")

    if tool_name is None:
        handle_chat_message(session, user_input)
        return

    if not isinstance(tool_name, str):
        print(f"工具计划格式错误：{plan}")
        return

    tool = tools.get(tool_name)
    if tool is None:
        print(f"模型选择了未知工具：{tool_name}")
        return

    tool_arguments = plan.get("arguments", {})
    if not isinstance(tool_arguments, dict):
        print(f"工具参数格式错误：{plan}")
        return

    session.messages.append({"role": "user", "content": user_input})
    session.trim(MAX_HISTORY_ROUNDS)

    result = tool.run(tool_arguments)
    tool_result_text = result.to_text()
    print(f"Tool[{tool_name}]: {tool_result_text}")

    if not result.ok:
        final_answer = tool_result_text
        print(f"AI: {final_answer}")
        session.add_tool_trace(
            {
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "user_input": user_input,
                "tool_name": tool_name,
                "arguments": tool_arguments,
                "ok": result.ok,
                "content": result.content,
                "error_type": result.error_type,
                "final_answer": final_answer,
            }
        )
        session.messages.append({"role": "assistant", "content": final_answer})
        return

    final_answer = answer_with_tool_result(user_input, tool_name, tool_result_text)
    print(f"AI: {final_answer}")
    session.add_tool_trace(
        {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "user_input": user_input,
            "tool_name": tool_name,
            "arguments": tool_arguments,
            "ok": result.ok,
            "content": result.content,
            "error_type": result.error_type,
            "final_answer": final_answer,
        }
    )
    session.messages.append({"role": "assistant", "content": final_answer})
