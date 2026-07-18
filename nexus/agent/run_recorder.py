"""Agent Run 的 Trace 写入和失败终态处理。"""

from typing import Any

from nexus.agent.errors import ERROR_PLANNER
from nexus.agent.observability import create_trace_event
from nexus.app import AppContext
from nexus.settings import MAX_HISTORY_ROUNDS
from nexus.tools import ToolError


class RunRecorder:
    """绑定一个 AppContext 和 run_id，统一记录本次 Run 的事件与错误。"""

    def __init__(self, context: AppContext, run_id: str) -> None:
        """保存运行上下文和关联 ID，供后续事件自动复用。"""
        self.context = context
        self.run_id = run_id

    def emit(
        self,
        event_type: str,
        *,
        status: str = "info",
        step: int | None = None,
        duration_ms: float | None = None,
        data: dict[str, Any] | None = None,
        error: dict[str, Any] | None = None,
    ) -> None:
        """补齐当前 Session 和 Run 信息，并立即写入一条 TraceEvent。"""
        self.context["trace_logger"].record(
            create_trace_event(
                event_type=event_type,
                session_id=self.context["session"].name,
                run_id=self.run_id,
                status=status,
                step=step,
                duration_ms=duration_ms,
                data=data,
                error=error,
            )
        )

    def record_agent_error(
        self,
        *,
        user_input: str,
        step: int,
        tool_name: str,
        arguments: dict,
        error: ToolError,
        record_user_message: bool = True,
    ) -> None:
        """向用户展示 Agent 错误，保存会话消息，并以 run_failed 结束 Run。"""
        session = self.context["session"]
        final_answer = error.to_text()

        print(f"AI: {final_answer}")
        if record_user_message:
            session.messages.append({"role": "user", "content": user_input})
            session.trim(MAX_HISTORY_ROUNDS)
        session.messages.append({"role": "assistant", "content": final_answer})
        self.emit(
            "run_failed",
            status="error",
            step=step,
            data={
                "tool_name": tool_name,
                "arguments": arguments,
                "final_answer": final_answer,
            },
            error=error.to_dict(),
        )

    def record_plan_error(
        self,
        *,
        user_input: str,
        plan: dict,
        plan_error: dict,
        step: int,
        record_user_message: bool = True,
        duration_ms: float | None = None,
    ) -> None:
        """记录 planner_failed，并将结构化 Planner 错误转成 Run 失败终态。"""
        message = str(plan_error.get("message") or "工具规划失败。")
        details = plan_error.get("details")
        if not isinstance(details, dict):
            details = {"plan": plan}

        error_kind = str(plan_error.get("kind") or ERROR_PLANNER)
        self.emit(
            "planner_failed",
            status="error",
            step=step,
            duration_ms=duration_ms,
            data={"plan": plan},
            error={
                "kind": error_kind,
                "message": message,
                "details": details,
            },
        )
        self.record_agent_error(
            user_input=user_input,
            step=step,
            tool_name="<planner>",
            arguments={},
            error=ToolError(
                kind=error_kind,
                message=message,
                retryable=True,
                details=details,
            ),
            record_user_message=record_user_message,
        )
