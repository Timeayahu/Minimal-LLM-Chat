from nexus.agent import handle_agent_message
from nexus.app import create_app_context
from nexus.cli.parser import parse_command

try:
    from prompt_toolkit import prompt
except ImportError:
    prompt = None


def read_user_input() -> str:
    """读取用户输入。

    prompt_toolkit 对中文这类双宽字符的删除和光标移动支持更好。
    如果环境里没有安装 prompt_toolkit，就退回 Python 内置 input。
    """
    if prompt is None:
        return input("You: ").strip()

    return prompt("You: ").strip()


def main():
    """创建应用上下文并运行 CLI 主循环，将输入分发给 Command 或 Agent。"""
    print("欢迎来我的频道，今天想聊点什么？")

    context = create_app_context()
    commands = context["commands"]

    while True:
        user_input = read_user_input()
        if not user_input:
            continue

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

        handle_agent_message(context, user_input)


if __name__ == "__main__":
    main()
