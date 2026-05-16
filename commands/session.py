from commands.command import Command
from memory import create_session, generate_session_name, save_history
from models import AppContext


class SaveCommand(Command):
    name = "/save"
    description = "保存对话记录"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        session = context["session"]
        save_history(session["messages"], session["name"])
        print(f"System: 当前对话已保存到会话 '{session['name']}'。")
        return True


class HistoryCommand(Command):
    name = "/history"
    description = "查看最近10条对话记录"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        messages = context["session"]["messages"]
        chat_messages = [msg for msg in messages if msg["role"] != "system"]

        if not chat_messages:
            print("暂无历史对话。")
            return True

        recent_messages = chat_messages[-10:]

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


class NewCommand(Command):
    name = "/new"
    description = "新建或切换到指定会话"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        session = context["session"]
        new_session = " ".join(args).strip()

        if not new_session:
            new_session = generate_session_name()

        save_history(session["messages"], session["name"])

        context["session"] = create_session(new_session)

        print(f"System: 已创建新会话 '{new_session}'。")
        return True


class ExitCommand(Command):
    name = "/exit"
    description = "保存并退出程序"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        session = context["session"]
        save_history(session["messages"], session["name"])
        print("Goodbye!")
        return False
