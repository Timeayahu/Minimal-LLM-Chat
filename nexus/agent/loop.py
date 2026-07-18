"""AgentRuntime 的函数式兼容入口。"""

from nexus.agent.runtime import AgentRuntime
from nexus.app import AppContext


def handle_agent_message(context: AppContext, user_input: str) -> None:
    """使用 AgentRuntime 启动一条新的普通用户请求。"""
    AgentRuntime(context).run(user_input)


def continue_agent_loop_after_confirmed_tool(
    context: AppContext,
    user_input: str,
    confirmed_step: int,
    tool_name: str,
    tool_arguments: dict,
    tool_result_text: str,
    tool_ok: bool,
    run_id: str,
) -> None:
    """使用 AgentRuntime 和原 run_id 恢复确认后的 Agent Loop。"""
    AgentRuntime(context).continue_after_confirmed_tool(
        user_input=user_input,
        confirmed_step=confirmed_step,
        tool_name=tool_name,
        tool_arguments=tool_arguments,
        tool_result_text=tool_result_text,
        tool_ok=tool_ok,
        run_id=run_id,
    )
