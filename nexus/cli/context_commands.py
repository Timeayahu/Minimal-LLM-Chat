from nexus.agent import continue_agent_loop_after_confirmed_tool
from nexus.agent.observability import new_run_id
from nexus.agent.policy import ToolRequest
from nexus.agent.run_recorder import RunRecorder
from nexus.agent.tool_execution import execute_tool
from nexus.app import AppContext
from nexus.cli.command import Command
from nexus.context import (
    MEMORY_KINDS,
    MemoryKind,
    Session,
    list_session_names,
    load_session_data,
)


class SaveCommand(Command):
    name = "/save"
    description = "保存对话记录"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """把当前 Session 的 messages 和 pending 状态写成会话快照，不包含运行 Trace。"""
        session = context["session"]
        session.save()
        print(f"System: 当前对话已保存到会话 '{session.name}'。")
        return True


class HistoryCommand(Command):
    name = "/history"
    description = "查看最近10条对话记录"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """读取当前 Session 最近的非 system 消息，并按用户/助手格式展示。"""
        recent_messages = context["session"].get_recent_messages()

        if not recent_messages:
            print("暂无历史对话。")
            return True

        print("--- 最近历史 ---")
        for msg in recent_messages:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                print(f"You: {content}")
            elif role == "assistant":
                print(f"AI: {content}")
            print()

        return True


class RememberCommand(Command):
    name = "/remember"
    description = "保存长期记忆，可选类型 fact/preference/learning"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """解析可选记忆类型和内容，然后通过 MemoryStore 立即持久化新记忆。"""
        kind: MemoryKind = "fact"
        if args and args[0] in MEMORY_KINDS:
            kind = args[0]
            args = args[1:]

        content = " ".join(args).strip()
        if not content:
            print("用法：/remember [fact|preference|learning] 要长期记住的内容")
            return True

        memory = context["memory_store"].add(content, kind)
        print(f"System: 已保存长期记忆 {memory['id']} [{memory['kind']}]。")
        return True


class MemoriesCommand(Command):
    name = "/memories"
    description = "查看最近长期记忆"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """列出 MemoryStore 中最近的长期记忆及其 ID、类型和创建时间。"""
        memories = context["memory_store"].list_recent()

        if not memories:
            print("暂无长期记忆。")
            return True

        print("--- 最近长期记忆 ---")
        for memory in memories:
            print(
                f"{memory['id']} [{memory['kind']}] "
                f"{memory['created_at']} - {memory['content']}"
            )

        return True


class MemoryCommand(Command):
    name = "/memory"
    description = "按 ID 查看长期记忆详情"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """使用用户传入的记忆 ID 查找并展示一条完整长期记忆。"""
        if not args:
            print("用法：/memory 记忆ID")
            return True

        memory = context["memory_store"].get(args[0])
        if memory is None:
            print(f"找不到长期记忆：{args[0]}")
            return True

        print(f"ID: {memory['id']}")
        print(f"类型: {memory['kind']}")
        print(f"创建时间: {memory['created_at']}")
        print(f"内容: {memory['content']}")
        return True


class ForgetCommand(Command):
    name = "/forget"
    description = "按 ID 删除长期记忆"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """按记忆 ID 从 MemoryStore 删除记忆，并立即写回长期记忆文件。"""
        if not args:
            print("用法：/forget 记忆ID")
            return True

        memory_id = args[0]
        if not context["memory_store"].delete(memory_id):
            print(f"找不到长期记忆：{memory_id}")
            return True

        print(f"System: 已删除长期记忆 {memory_id}。")
        return True


class TraceCommand(Command):
    name = "/trace"
    description = "查看当前会话或指定 run_id 的运行事件"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """从独立 JSONL TraceStore 查询当前 Session 或用户指定的 Run。"""
        run_id = args[0] if args else None
        events = context["trace_logger"].read_recent(
            session_id=None if run_id else context["session"].name,
            run_id=run_id,
            limit=30,
        )

        if events:
            print("--- 最近 Agent 运行事件 ---")
            for event in events:
                step_text = f" step={event['step']}" if event.get("step") else ""
                duration = event.get("duration_ms")
                duration_text = (
                    f" duration={duration:.1f}ms" if isinstance(duration, (int, float)) else ""
                )
                print(
                    f"{event['created_at']} {event['event_type']} "
                    f"status={event['status']}{step_text}{duration_text}"
                )
                data = event.get("data") or {}
                if data.get("tool_name"):
                    print(f"  tool={data['tool_name']}")
                if data.get("action"):
                    print(f"  action={data['action']}")
                if data.get("result_preview"):
                    print(f"  result={data['result_preview']}")
                if data.get("answer_preview"):
                    print(f"  answer={data['answer_preview']}")
                if data.get("reason"):
                    print(f"  reason={data['reason']}")
                error = event.get("error")
                if error:
                    print(f"  error={error.get('kind')}: {error.get('message')}")
            print(f"Run: {events[-1]['run_id']}")
            return True

        print("暂无 Agent 运行事件。")
        return True


class ConfirmCommand(Command):
    name = "/confirm"
    description = "确认执行待确认工具"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """执行 Session 中挂起的工具，记录确认事件，并用原 run_id 继续 Agent Loop。"""
        session = context["session"]
        pending_tool_call = session.pending_tool_call

        if pending_tool_call is None:
            print("当前没有等待确认的工具调用。")
            return True

        tools = context["tools"]
        tool_name = pending_tool_call["tool_name"]
        tool = tools.get(tool_name)
        run_id = pending_tool_call.get("run_id") or new_run_id()
        if tool is None:
            print(f"待确认工具不存在：{tool_name}")
            _record_runtime_event(
                context,
                event_type="run_failed",
                run_id=run_id,
                status="error",
                step=pending_tool_call["step"],
                data={"tool_name": tool_name, "reason": "unknown_tool"},
            )
            session.clear_pending_tool_call()
            return True

        _record_runtime_event(
            context,
            event_type="confirmation_received",
            run_id=run_id,
            status="running",
            step=pending_tool_call["step"],
            data={"tool_name": tool_name},
        )
        _record_runtime_event(
            context,
            event_type="tool_started",
            run_id=run_id,
            status="running",
            step=pending_tool_call["step"],
            data={
                "tool_name": tool_name,
                "arguments": pending_tool_call["arguments"],
                "confirmed": True,
            },
        )
        execution = execute_tool(
            ToolRequest(
                name=tool_name,
                arguments=pending_tool_call["arguments"],
                tool=tool,
            )
        )
        result = execution.result
        tool_result_text = execution.result_text

        _record_runtime_event(
            context,
            event_type="tool_completed" if result.ok else "tool_failed",
            run_id=run_id,
            status="success" if result.ok else "error",
            step=pending_tool_call["step"],
            duration_ms=execution.duration_ms,
            data={
                "tool_name": tool_name,
                "result_preview": result.content[:500],
                "confirmed": True,
            },
            error=result.error.to_dict() if result.error else None,
        )

        print(f"Tool[confirm:{tool_name}]: {tool_result_text}")

        session.clear_pending_tool_call()
        continue_agent_loop_after_confirmed_tool(
            context=context,
            user_input=pending_tool_call["user_input"],
            confirmed_step=pending_tool_call["step"],
            tool_name=tool_name,
            tool_arguments=pending_tool_call["arguments"],
            tool_result_text=tool_result_text,
            tool_ok=result.ok,
            run_id=run_id,
        )
        return True


class CancelCommand(Command):
    name = "/cancel"
    description = "取消待确认工具"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """取消 Session 中挂起的工具，清理 pending 状态并以 run_cancelled 结束原 Run。"""
        session = context["session"]
        pending_tool_call = session.pending_tool_call

        if pending_tool_call is None:
            print("当前没有等待取消的工具调用。")
            return True

        final_answer = f"已取消 {pending_tool_call['tool_name']} 工具调用。"
        run_id = pending_tool_call.get("run_id") or new_run_id()
        print(f"AI: {final_answer}")

        _record_runtime_event(
            context,
            event_type="run_cancelled",
            run_id=run_id,
            status="cancelled",
            step=pending_tool_call["step"],
            data={
                "tool_name": pending_tool_call["tool_name"],
                "final_answer": final_answer,
            },
        )

        session.messages.append({"role": "assistant", "content": final_answer})
        session.clear_pending_tool_call()
        return True


class NewCommand(Command):
    name = "/new"
    description = "新建会话"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """先保存当前会话快照，再用新 Session 替换 AppContext 中的当前会话。"""
        session = context["session"]
        session.save()

        context["session"] = Session()

        print(f"System: 已创建新会话 '{context['session'].name}'。")
        return True


class LoadCommand(Command):
    name = "/load"
    description = "加载已保存会话"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """无参数时列出会话；有参数时保存当前会话并加载指定会话快照。"""
        if not args:
            session_names = list_session_names()
            if not session_names:
                print("暂无已保存会话。")
                return True

            print("已保存会话：")
            for session_name in session_names:
                print(f"  {session_name}")
            print("使用 /load 会话名 加载指定会话。")
            return True

        session_name = args[0]
        session_data = load_session_data(session_name)

        if session_data is None:
            print(f"找不到会话：{session_name}")
            print("输入 /load 查看已保存会话。")
            return True

        context["session"].save()
        context["session"] = Session.from_dict(session_data)
        loaded_session = context["session"]
        print(
            f"System: 已加载会话 '{loaded_session.name}'，"
            f"包含 {len(loaded_session.messages)} 条消息。"
        )
        return True


class ExitCommand(Command):
    name = "/exit"
    description = "保存并退出程序"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """保存当前 Session 快照并返回 False，通知 CLI 主循环结束。"""
        session = context["session"]
        session.save()
        print("Goodbye!")
        return False


def _record_runtime_event(
    context: AppContext,
    *,
    event_type: str,
    run_id: str,
    status: str,
    step: int | None = None,
    duration_ms: float | None = None,
    data: dict | None = None,
    error: dict | None = None,
) -> None:
    """
    把命令层产生的确认/取消事件转成 TraceEvent 并立即落盘。

    这个转换点自动填入当前 Session ID，调用方只需提供本次
    Run 和事件本身的字段。函数不修改 Session 状态。
    """
    RunRecorder(context, run_id).emit(
        event_type,
        status=status,
        step=step,
        duration_ms=duration_ms,
        data=data,
        error=error,
    )
