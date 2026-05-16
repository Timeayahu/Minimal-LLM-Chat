from chat import handle_chat_message
from commands import get_commands
from commands.parser import parse_command
from memory import create_session
from models import AppContext


def create_app_context() -> AppContext:
    """创建应用运行所需的上下文。"""
    commands = get_commands()
    context: AppContext = {
        "session": create_session(),
        "commands": commands,
    }

    return context


def main():
    print("欢迎来我的频道，今天想聊点什么？")

    context = create_app_context()
    commands = context["commands"]

    while True:
        user_input = input("You: ")
        command_name, args = parse_command(user_input)
        command = commands.get(command_name)

        if command:
            should_continue = command.execute(context, args)
            if should_continue:
                continue
            break

        if user_input.startswith("/"):
            print(f"未知命令：{command_name}")
            print("输入 /help 查看可用命令。")
            continue

        handle_chat_message(context["session"]["messages"], user_input) #统一用context来管理聊天记录


if __name__ == "__main__":
    main()
