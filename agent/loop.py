from dataclasses import dataclass
from datetime import datetime

from agent.chat import handle_chat_message
from agent.planner import decide_agent_step
from app_context import AppContext
from config import MAX_HISTORY_ROUNDS
from models import ToolError
from models.errors import (
    ERROR_INVALID_AGENT_ACTION,
    ERROR_INVALID_FINAL_ANSWER,
    ERROR_INVALID_TOOL_ARGUMENTS,
    ERROR_INVALID_TOOL_NAME,
    ERROR_PLANNER,
    ERROR_TOOL_REQUIRES_CONFIRMATION,
    ERROR_UNKNOWN_TOOL,
)


MAX_AGENT_STEPS = 3


@dataclass
class AgentLoopState:
    """一次 Agent Loop 运行中的可变状态。"""

    user_input: str
    observations: list[str]
    has_saved_user_input: bool
    fallback_to_chat: bool


def continue_agent_loop_after_confirmed_tool(
    context: AppContext,
    user_input: str,
    confirmed_step: int,
    tool_name: str,
    tool_arguments: dict,
    tool_result_text: str,
    tool_ok: bool,
) -> None:
    """用户确认工具执行后，带着工具观察结果继续 Agent Loop。"""
    if not tool_ok:
        final_answer = tool_result_text
        print(f"AI: {final_answer}")
        _attach_final_answer_to_latest_trace(context, final_answer)
        context["session"].messages.append(
            {"role": "assistant", "content": final_answer}
        )
        return

    _run_agent_loop(
        context=context,
        user_input=user_input,
        start_step=confirmed_step + 1,
        observations=[f"{tool_name}({tool_arguments}) -> {tool_result_text}"],
        should_save_user_input=False,
        fallback_to_chat=False,
    )


def handle_agent_message(context: AppContext, user_input: str) -> None:
    """处理普通用户输入，并由 Agent 执行最多 N 步的 plan-act-observe 循环。

    handle_agent_message() 整体流程：
    1. 先准备 session、tools、observations，并用 has_saved_user_input 标记用户输入是否已入历史。
    2. 每一轮都调用 decide_agent_step()，让模型基于“用户问题 + 已有 observation”决定下一步。
    3. 如果 planner 本身出错，就记录 planner 错误、按需保存用户输入，然后结束。
    4. 如果 action 是 final，先检查 answer 是否可用；若第一步就 final，则回到普通聊天流程。
    5. 如果 action 是 tool，就依次检查工具名、工具是否存在、参数是否为 dict、工具是否需要确认。
    6. 所有检查通过后，先把用户输入保存进 session.messages，再真正执行工具。
    7. 工具结果会写入 observations 和 trace；成功则进入下一轮，失败则直接给用户错误回答。
    8. 如果达到 MAX_AGENT_STEPS 仍没有 final，就停止循环，避免 Agent 无限调用工具。
    """

    _run_agent_loop(
        context=context,
        user_input=user_input,
        start_step=1,
        observations=[],
        should_save_user_input=True,
        fallback_to_chat=True,
    )


def _run_agent_loop(
    context: AppContext,
    user_input: str,
    start_step: int,
    observations: list[str],
    should_save_user_input: bool,
    fallback_to_chat: bool,
) -> None:
    """执行通用 Agent Loop，可从普通输入或确认后的工具结果继续运行。"""
    session = context["session"]
    tools = context["tools"]
    state = AgentLoopState(
        user_input=user_input,
        observations=observations,
        has_saved_user_input=not should_save_user_input,
        fallback_to_chat=fallback_to_chat,
    )

    for step in range(start_step, MAX_AGENT_STEPS + 1):
        # 3. 让 planner 根据用户输入和已有 observation，决定本步是调用工具还是最终回答。
        plan = decide_agent_step(
            state.user_input,
            tools,
            state.observations,
            context["memory_store"].to_messages_text(),
        )
        plan_error = plan.get("error")

        # 4. 如果 planner 自己失败，例如没有返回合法 JSON，就记录错误并结束本轮。
        if isinstance(plan_error, dict):
            _record_plan_error(
                context,
                state.user_input,
                plan,
                plan_error,
                step,
                # 如果还没保存过用户输入，就让错误记录函数顺手保存。
                record_user_message=not state.has_saved_user_input,
            )
            return

        action = plan.get("action")

        # 5. 如果 planner 认为信息已经足够，就进入最终回答分支。
        if action == "final":
            _handle_final_action(context, plan, step, state)
            return

        # 6. 除了 final，当前只接受 tool。其它 action 都属于 planner 格式错误。
        if action != "tool":
            _record_agent_error(
                context,
                user_input=state.user_input,
                step=step,
                tool_name="<planner>",
                arguments={},
                error=ToolError(
                    kind=ERROR_INVALID_AGENT_ACTION,
                    message=f"Agent 步骤里的 action 必须是 tool 或 final：{plan}",
                    retryable=True,
                    details={"plan": plan},
                ),
                record_user_message=not state.has_saved_user_input,
            )
            return

        should_continue = _handle_tool_action(context, plan, step, state)
        if not should_continue:
            return

    # 16. 如果循环用完所有步数还没有 final，就触发 max_steps 安全停止。
    final_answer = f"已达到最大 Agent 步数（{MAX_AGENT_STEPS}），本轮停止。"
    print(f"AI: {final_answer}")
    _attach_final_answer_to_latest_trace(context, final_answer)
    session.messages.append({"role": "assistant", "content": final_answer})


def _handle_final_action(
    context: AppContext,
    plan: dict,
    step: int,
    state: AgentLoopState,
) -> None:
    """处理 planner 返回 final 的分支。"""
    session = context["session"]
    final_answer = plan.get("answer")

    if not isinstance(final_answer, str) or not final_answer:
        _record_agent_error(
            context,
            user_input=state.user_input,
            step=step,
            tool_name="<planner>",
            arguments={},
            error=ToolError(
                kind=ERROR_INVALID_FINAL_ANSWER,
                message=f"最终回答必须是非空字符串：{plan}",
                retryable=True,
                details={"plan": plan},
            ),
            record_user_message=not state.has_saved_user_input,
        )
        return

    if (
        state.fallback_to_chat
        and not state.has_saved_user_input
        and not state.observations
    ):
        handle_chat_message(session, context["memory_store"], state.user_input)
        return

    _ensure_user_input_saved(context, state)
    print(f"AI: {final_answer}")
    _attach_final_answer_to_latest_trace(context, final_answer)
    session.messages.append({"role": "assistant", "content": final_answer})


def _handle_tool_action(
    context: AppContext,
    plan: dict,
    step: int,
    state: AgentLoopState,
) -> bool:
    """处理 planner 返回 tool 的分支；返回是否继续下一轮 loop。"""
    session = context["session"]
    tools = context["tools"]

    tool_name = plan.get("tool")
    if not isinstance(tool_name, str):
        _record_agent_error(
            context,
            user_input=state.user_input,
            step=step,
            tool_name="<planner>",
            arguments={},
            error=ToolError(
                kind=ERROR_INVALID_TOOL_NAME,
                message=f"工具计划里的 tool 字段必须是字符串：{plan}",
                retryable=True,
                details={"plan": plan},
            ),
            record_user_message=not state.has_saved_user_input,
        )
        return False

    tool = tools.get(tool_name)
    if tool is None:
        _record_agent_error(
            context,
            user_input=state.user_input,
            step=step,
            tool_name=tool_name,
            arguments={},
            error=ToolError(
                kind=ERROR_UNKNOWN_TOOL,
                message=f"模型选择了未知工具：{tool_name}",
                retryable=True,
                details={"available_tools": list(tools.keys())},
            ),
            record_user_message=not state.has_saved_user_input,
        )
        return False

    tool_arguments = plan.get("arguments", {})
    if not isinstance(tool_arguments, dict):
        _record_agent_error(
            context,
            user_input=state.user_input,
            step=step,
            tool_name=tool_name,
            arguments={},
            error=ToolError(
                kind=ERROR_INVALID_TOOL_ARGUMENTS,
                message=f"工具参数必须是 dict：{plan}",
                retryable=True,
                details={"plan": plan},
            ),
            record_user_message=not state.has_saved_user_input,
        )
        return False

    if tool.requires_confirmation:
        _ensure_user_input_saved(context, state)
        session.set_pending_tool_call(
            {
                "user_input": state.user_input,
                "step": step,
                "tool_name": tool_name,
                "arguments": tool_arguments,
            }
        )
        final_answer = (
            f"{tool_name} 工具需要用户确认。"
            "输入 /confirm 执行，或输入 /cancel 取消。"
        )
        print(f"AI: {final_answer}")
        _record_agent_step_trace(
            context,
            user_input=state.user_input,
            step=step,
            tool_name=tool_name,
            arguments=tool_arguments,
            ok=False,
            content=final_answer,
            error=ToolError(
                kind=ERROR_TOOL_REQUIRES_CONFIRMATION,
                message=f"{tool_name} 工具需要用户确认。",
                retryable=False,
                details={"tool_name": tool_name},
            ).to_dict(),
            final_answer=final_answer,
        )
        session.messages.append({"role": "assistant", "content": final_answer})
        return False

    _ensure_user_input_saved(context, state)
    result = tool.run(tool_arguments)
    tool_result_text = result.to_text()
    print(f"Tool[{step}:{tool_name}]: {tool_result_text}")
    state.observations.append(f"{tool_name}({tool_arguments}) -> {tool_result_text}")

    if not result.ok:
        final_answer = tool_result_text
        print(f"AI: {final_answer}")
        _record_agent_step_trace(
            context,
            user_input=state.user_input,
            step=step,
            tool_name=tool_name,
            arguments=tool_arguments,
            ok=result.ok,
            content=result.content,
            error=result.error.to_dict() if result.error else None,
            final_answer=final_answer,
        )
        session.messages.append({"role": "assistant", "content": final_answer})
        return False

    _record_agent_step_trace(
        context,
        user_input=state.user_input,
        step=step,
        tool_name=tool_name,
        arguments=tool_arguments,
        ok=result.ok,
        content=result.content,
        error=result.error.to_dict() if result.error else None,
        final_answer="",
    )
    return True


def _ensure_user_input_saved(context: AppContext, state: AgentLoopState) -> None:
    """确保本轮原始用户输入只写入历史一次。"""
    if state.has_saved_user_input:
        return

    session = context["session"]
    session.messages.append({"role": "user", "content": state.user_input})
    session.trim(MAX_HISTORY_ROUNDS)
    state.has_saved_user_input = True


def _record_agent_error(
    context: AppContext,
    user_input: str,
    step: int,
    tool_name: str,
    arguments: dict,
    error: ToolError,
    record_user_message: bool = True,
) -> None:
    """记录 Agent 在工具执行前遇到的错误。并给用户明确的回复"""
    session = context["session"]
    final_answer = error.to_text()

    print(f"AI: {final_answer}")
    if record_user_message:
        session.messages.append({"role": "user", "content": user_input})
        session.trim(MAX_HISTORY_ROUNDS)
    session.add_agent_step_trace(
        {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "user_input": user_input,
            "step": step,
            "tool_name": tool_name,
            "arguments": arguments,
            "ok": False,
            "content": error.message,
            "error": error.to_dict(),
            "final_answer": final_answer,
        }
    )
    session.messages.append({"role": "assistant", "content": final_answer})


def _record_plan_error(
    context: AppContext,
    user_input: str,
    plan: dict,
    plan_error: dict,
    step: int,
    record_user_message: bool = True,
) -> None:
    """把规划器返回的结构化错误记录进 trace。"""
    message = str(plan_error.get("message") or "工具规划失败。")
    details = plan_error.get("details")
    if not isinstance(details, dict):
        details = {"plan": plan}

    _record_agent_error(
        context,
        user_input=user_input,
        step=step,
        tool_name="<planner>",
        arguments={},
        error=ToolError(
            kind=str(plan_error.get("kind") or ERROR_PLANNER),
            message=message,
            retryable=True,
            details=details,
        ),
        record_user_message=record_user_message,
    )


def _record_agent_step_trace(
    context: AppContext,
    user_input: str,
    step: int,
    tool_name: str,
    arguments: dict,
    ok: bool,
    content: str,
    error: dict | None,
    final_answer: str,
) -> None:
    """记录一次 Agent Loop 步骤。"""
    context["session"].add_agent_step_trace(
        {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "user_input": user_input,
            "step": step,
            "tool_name": tool_name,
            "arguments": arguments,
            "ok": ok,
            "content": content,
            "error": error,
            "final_answer": final_answer,
        }
    )


def _attach_final_answer_to_latest_trace(
    context: AppContext,
    final_answer: str,
) -> None:
    """把最终回答补到最近一条 Agent step trace 上，方便 /trace 复盘。"""
    traces = context["session"].traces
    if not traces:
        return

    traces[-1]["final_answer"] = final_answer
