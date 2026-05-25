from datetime import datetime

from agent.chat import continue_agent_loop_after_confirmed_tool
from app_context import AppContext
from commands.command import Command
from memory import Session, list_session_names, load_session_data


class SaveCommand(Command):
    name = "/save"
    description = "保存对话记录"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        session = context["session"]
        session.save()
        print(f"System: 当前对话已保存到会话 '{session.name}'。")
        return True


class HistoryCommand(Command):
    name = "/history"
    description = "查看最近10条对话记录"

    def execute(self, context: AppContext, args: list[str]) -> bool:
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


class TraceCommand(Command):
    name = "/trace"
    description = "查看最近 Agent 步骤记录"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        traces = context["session"].get_recent_traces()

        if not traces:
            print("暂无 Agent 步骤记录。")
            return True

        print("--- 最近 Agent 步骤 ---")
        for trace in traces[-10:]:
            print(f"Time: {trace['created_at']}")
            if trace.get("step") is not None:
                print(f"Step: {trace['step']}")
            print(f"User: {trace['user_input']}")
            print(f"Tool: {trace['tool_name']}")
            print(f"Arguments: {trace['arguments']}")
            print(f"OK: {trace['ok']}")
            error = trace.get("error")
            if error:
                print(f"Error: {error['kind']}")
                print(f"Error message: {error['message']}")
                print(f"Retryable: {error['retryable']}")
            elif trace.get("error_type"):
                print(f"Error: {trace['error_type']}")
            print(f"Content: {trace['content']}")
            print(f"Final: {trace['final_answer']}")
            print()

        return True


class ConfirmCommand(Command):
    name = "/confirm"
    description = "确认执行待确认工具"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        session = context["session"]
        pending_tool_call = session.pending_tool_call

        if pending_tool_call is None:
            print("当前没有等待确认的工具调用。")
            return True

        tools = context["tools"]
        tool_name = pending_tool_call["tool_name"]
        tool = tools.get(tool_name)
        if tool is None:
            print(f"待确认工具不存在：{tool_name}")
            session.clear_pending_tool_call()
            return True

        result = tool.run(pending_tool_call["arguments"])
        tool_result_text = result.to_text()

        print(f"Tool[confirm:{tool_name}]: {tool_result_text}")

        session.add_agent_step_trace(
            {
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "user_input": pending_tool_call["user_input"],
                "step": pending_tool_call["step"],
                "tool_name": tool_name,
                "arguments": pending_tool_call["arguments"],
                "ok": result.ok,
                "content": result.content,
                "error": result.error.to_dict() if result.error else None,
                "final_answer": "",
            }
        )
        session.clear_pending_tool_call()
        continue_agent_loop_after_confirmed_tool(
            context=context,
            user_input=pending_tool_call["user_input"],
            confirmed_step=pending_tool_call["step"],
            tool_name=tool_name,
            tool_arguments=pending_tool_call["arguments"],
            tool_result_text=tool_result_text,
            tool_ok=result.ok,
        )
        return True


class CancelCommand(Command):
    name = "/cancel"
    description = "取消待确认工具"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        session = context["session"]
        pending_tool_call = session.pending_tool_call

        if pending_tool_call is None:
            print("当前没有等待取消的工具调用。")
            return True

        final_answer = f"已取消 {pending_tool_call['tool_name']} 工具调用。"
        print(f"AI: {final_answer}")

        session.add_agent_step_trace(
            {
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "user_input": pending_tool_call["user_input"],
                "step": pending_tool_call["step"],
                "tool_name": pending_tool_call["tool_name"],
                "arguments": pending_tool_call["arguments"],
                "ok": False,
                "content": final_answer,
                "error": None,
                "final_answer": final_answer,
            }
        )
        session.messages.append({"role": "assistant", "content": final_answer})
        session.clear_pending_tool_call()
        return True


class NewCommand(Command):
    name = "/new"
    description = "新建会话"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        session = context["session"]
        session.save()

        context["session"] = Session()

        print(f"System: 已创建新会话 '{context['session'].name}'。")
        return True


class LoadCommand(Command):
    name = "/load"
    description = "加载已保存会话"

    def execute(self, context: AppContext, args: list[str]) -> bool:
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
            f"包含 {len(loaded_session.messages)} 条消息和 "
            f"{len(loaded_session.traces)} 条 Agent 步骤记录。"
        )
        return True


class ExitCommand(Command):
    name = "/exit"
    description = "保存并退出程序"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        session = context["session"]
        session.save()
        print("Goodbye!")
        return False
