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
    description = "查看最近工具调用记录"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        traces = context["session"].get_recent_traces()

        if not traces:
            print("暂无工具调用记录。")
            return True

        print("--- 最近工具调用 ---")
        for trace in traces[-10:]:
            print(f"Time: {trace['created_at']}")
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
            f"{len(loaded_session.traces)} 条工具调用记录。"
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
