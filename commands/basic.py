from app_context import AppContext
from commands.command import Command
from config import MODEL, get_config_summary


class HelpCommand(Command):
    name = "/help"
    description = "查看帮助"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        commands = context["commands"]

        print("可用命令：")
        for command in commands.values():
            print(f"  {command.name} {command.description}")
        return True


class ResetCommand(Command):
    name = "/reset"
    description = "清空上下文"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        context["session"].reset()
        print("上下文已清空")
        return True


class ModelCommand(Command):
    name = "/model"
    description = "查看当前模型"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        print("当前模型：", MODEL)
        return True


class CountCommand(Command):
    name = "/count"
    description = "查看当前对话记忆轮数"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        user_message_count = context["session"].count_user_messages()
        print("当前聊天记忆轮数为：", user_message_count)
        return True


class ConfigCommand(Command):
    name = "/config"
    description = "查看当前配置"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        config_summary = get_config_summary()
        print("当前配置：")
        for key, value in config_summary.items():
            print(f"  {key}: {value}")
        return True
