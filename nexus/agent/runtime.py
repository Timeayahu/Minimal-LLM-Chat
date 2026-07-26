"""Agent Run 生命周期与 plan-act-observe-final 循环编排。"""

from dataclasses import dataclass
from time import perf_counter

from nexus.agent.actions import (
    ACTION_FINAL,
    AgentActionParseError,
    FinalAction,
    ToolAction,
    parse_agent_action,
)
from nexus.agent.chat import handle_chat_message
from nexus.agent.observability import new_run_id
from nexus.agent.planner import decide_agent_step
from nexus.agent.policy import ToolRequest, resolve_tool_request
from nexus.agent.run_recorder import RunRecorder
from nexus.agent.tool_execution import execute_tool
from nexus.app import AppContext
from nexus.settings import MAX_HISTORY_ROUNDS
from nexus.tools import ToolError


MAX_AGENT_STEPS = 3


@dataclass
class AgentLoopState:
    """一次 Agent Loop 运行中的可变状态。"""

    user_input: str
    observations: list[str]
    has_saved_user_input: bool
    fallback_to_chat: bool


class AgentRuntime:
    """负责一次 Agent Run 的启动、恢复、循环编排和最终回答。"""

    def __init__(self, context: AppContext) -> None:
        """绑定本次运行使用的 Session、Memory、Tools 和 TraceLogger。"""
        self.context = context

    def run(self, user_input: str) -> None:
        """创建新 run_id，并从第一步处理一条普通用户输入。"""
        run_id = new_run_id()
        recorder = RunRecorder(self.context, run_id)
        recorder.emit(
            "run_started",
            status="running",
            data={
                "input_preview": user_input[:200],
                "input_length": len(user_input),
            },
        )
        try:
            self._run_loop(
                user_input=user_input,
                start_step=1,
                observations=[],
                should_save_user_input=True,
                fallback_to_chat=True,
                recorder=recorder,
            )
        except Exception as error:
            # 意外异常必须先留下终态事件，再继续抛出以保留真实错误现场。
            recorder.emit(
                "run_failed",
                status="error",
                data={"reason": "unhandled_exception"},
                error={
                    "kind": "unhandled_exception",
                    "message": str(error),
                    "details": {"exception_type": type(error).__name__},
                },
            )
            raise

    def continue_after_confirmed_tool(
        self,
        *,
        user_input: str,
        confirmed_step: int,
        tool_name: str,
        tool_arguments: dict,
        tool_result_text: str,
        tool_ok: bool,
        run_id: str,
    ) -> None:
        """接收已确认工具的结果，并用原 run_id 从下一步恢复 Agent Loop。"""
        recorder = RunRecorder(self.context, run_id)
        if not tool_ok:
            final_answer = tool_result_text
            print(f"AI: {final_answer}")
            self.context["session"].messages.append(
                {"role": "assistant", "content": final_answer}
            )
            recorder.emit(
                "run_failed",
                status="error",
                step=confirmed_step,
                data={"final_answer": final_answer},
            )
            return

        self._run_loop(
            user_input=user_input,
            start_step=confirmed_step + 1,
            observations=[
                f"{tool_name}({tool_arguments}) -> {tool_result_text}"
            ],
            should_save_user_input=False,
            fallback_to_chat=False,
            recorder=recorder,
        )

    def _run_loop(
        self,
        *,
        user_input: str,
        start_step: int,
        observations: list[str],
        should_save_user_input: bool,
        fallback_to_chat: bool,
        recorder: RunRecorder,
    ) -> None:
        """循环调用 Planner，并把 final/tool action 分派给对应处理方法。"""
        state = AgentLoopState(
            user_input=user_input,
            observations=observations,
            has_saved_user_input=not should_save_user_input,
            fallback_to_chat=fallback_to_chat,
        )

        for step in range(start_step, MAX_AGENT_STEPS + 1):
            recorder.emit(
                "planner_started",
                status="running",
                step=step,
                data={"observation_count": len(state.observations)},
            )
            planner_started_at = perf_counter()
            planner_result = decide_agent_step(
                state.user_input,
                self.context["tools"],
                state.observations,
                self.context["memory_store"].to_messages_text(),
            )
            planner_duration_ms = (perf_counter() - planner_started_at) * 1000
            parsed_action = (
                planner_result
                if isinstance(planner_result, AgentActionParseError)
                else parse_agent_action(planner_result)
            )

            if isinstance(parsed_action, AgentActionParseError):
                raw_plan = (
                    planner_result
                    if isinstance(planner_result, dict)
                    else {"planner_result": str(planner_result)}
                )
                recorder.record_plan_error(
                    user_input=state.user_input,
                    plan=raw_plan,
                    plan_error=parsed_action.to_dict(),
                    step=step,
                    record_user_message=not state.has_saved_user_input,
                    duration_ms=planner_duration_ms,
                )
                return

            plan = parsed_action
            recorder.emit(
                "planner_completed",
                status="success",
                step=step,
                duration_ms=planner_duration_ms,
                data={"action": plan.get("action"), "tool": plan.get("tool")},
            )
            action = plan.get("action")

            if action == ACTION_FINAL:
                self._handle_final_action(plan, step, state, recorder)
                return

            if not self._handle_tool_action(plan, step, state, recorder):
                return

        final_answer = f"已达到最大 Agent 步数（{MAX_AGENT_STEPS}），本轮停止。"
        print(f"AI: {final_answer}")
        self.context["session"].messages.append(
            {"role": "assistant", "content": final_answer}
        )
        recorder.emit(
            "run_failed",
            status="error",
            step=MAX_AGENT_STEPS,
            data={"reason": "max_steps", "final_answer": final_answer},
        )

    def _handle_final_action(
        self,
        plan: FinalAction,
        step: int,
        state: AgentLoopState,
        recorder: RunRecorder,
    ) -> None:
        """校验并保存最终回答，必要时回退到普通聊天流程。"""
        session = self.context["session"]
        final_answer = plan.get("answer")

        if (
            state.fallback_to_chat
            and not state.has_saved_user_input
            and not state.observations
        ):
            chat_started_at = perf_counter()
            final_answer = handle_chat_message(
                session, self.context["memory_store"], state.user_input
            )
            recorder.emit(
                "final_answer",
                status="success",
                step=step,
                duration_ms=(perf_counter() - chat_started_at) * 1000,
                data={
                    "source": "chat_fallback",
                    "answer_length": len(final_answer),
                    "answer_preview": final_answer[:500],
                },
            )
            recorder.emit("run_completed", status="success", step=step)
            return

        self._ensure_user_input_saved(state)
        print(f"AI: {final_answer}")
        session.messages.append({"role": "assistant", "content": final_answer})
        recorder.emit(
            "final_answer",
            status="success",
            step=step,
            data={
                "source": "planner",
                "answer_length": len(final_answer),
                "answer_preview": final_answer[:500],
            },
        )
        recorder.emit("run_completed", status="success", step=step)

    def _handle_tool_action(
        self,
        plan: ToolAction,
        step: int,
        state: AgentLoopState,
        recorder: RunRecorder,
    ) -> bool:
        """按 Policy 解析工具请求，处理确认或执行，并返回是否继续循环。"""
        resolved = resolve_tool_request(plan, self.context["tools"])
        if isinstance(resolved, ToolError):
            recorder.record_agent_error(
                user_input=state.user_input,
                step=step,
                tool_name=str(plan.get("tool") or "<planner>"),
                arguments={},
                error=resolved,
                record_user_message=not state.has_saved_user_input,
            )
            return False

        request: ToolRequest = resolved
        recorder.emit(
            "tool_requested",
            status="pending",
            step=step,
            data={"tool_name": request.name, "arguments": request.arguments},
        )

        if request.requires_confirmation:
            self._pause_for_confirmation(request, step, state, recorder)
            return False

        self._ensure_user_input_saved(state)
        recorder.emit(
            "tool_started",
            status="running",
            step=step,
            data={"tool_name": request.name, "arguments": request.arguments},
        )
        execution = execute_tool(request)
        print(f"Tool[{step}:{request.name}]: {execution.result_text}")
        state.observations.append(execution.observation)
        recorder.emit(
            "tool_completed" if execution.result.ok else "tool_failed",
            status="success" if execution.result.ok else "error",
            step=step,
            duration_ms=execution.duration_ms,
            data={
                "tool_name": request.name,
                "arguments": request.arguments,
                "result_preview": execution.result.content[:500],
            },
            error=(
                execution.result.error.to_dict()
                if execution.result.error
                else None
            ),
        )

        if execution.result.ok:
            return True

        final_answer = execution.result_text
        print(f"AI: {final_answer}")
        self.context["session"].messages.append(
            {"role": "assistant", "content": final_answer}
        )
        recorder.emit(
            "run_failed",
            status="error",
            step=step,
            data={"reason": "tool_failed", "final_answer": final_answer},
            error=(
                execution.result.error.to_dict()
                if execution.result.error
                else None
            ),
        )
        return False

    def _pause_for_confirmation(
        self,
        request: ToolRequest,
        step: int,
        state: AgentLoopState,
        recorder: RunRecorder,
    ) -> None:
        """保存待确认工具请求、暂停 Run，并向用户展示确认提示。"""
        self._ensure_user_input_saved(state)
        session = self.context["session"]
        session.set_pending_tool_call(
            {
                "user_input": state.user_input,
                "step": step,
                "tool_name": request.name,
                "arguments": request.arguments,
                "run_id": recorder.run_id,
            }
        )
        final_answer = (
            f"{request.name} 工具需要用户确认。"
            "输入 /confirm 执行，或输入 /cancel 取消。"
        )
        print(f"AI: {final_answer}")
        session.messages.append({"role": "assistant", "content": final_answer})
        recorder.emit(
            "confirmation_requested",
            status="paused",
            step=step,
            data={"tool_name": request.name, "arguments": request.arguments},
        )

    def _ensure_user_input_saved(self, state: AgentLoopState) -> None:
        """确保本轮原始用户输入只写入 Session 一次，并裁剪历史长度。"""
        if state.has_saved_user_input:
            return

        session = self.context["session"]
        session.messages.append({"role": "user", "content": state.user_input})
        session.trim(MAX_HISTORY_ROUNDS)
        state.has_saved_user_input = True
