from nexus.app import AppContext
from nexus.cli.command import Command
from nexus.settings import MODEL, get_config_summary


class HelpCommand(Command):
    name = "/help"
    description = "查看帮助"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """遍历应用中已注册的命令，输出每个命令的名称和说明。"""
        commands = context["commands"]

        print("可用命令：")
        for command in commands.values():
            print(f"  {command.name} {command.description}")
        return True


class ResetCommand(Command):
    name = "/reset"
    description = "清空上下文"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """重置当前 Session 的对话消息和待确认工具状态，不删除独立 JSONL Trace。"""
        context["session"].reset()
        print("上下文已清空")
        return True


class ModelCommand(Command):
    name = "/model"
    description = "查看当前模型"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """输出从当前环境配置读取到的模型名称。"""
        print("当前模型：", MODEL)
        return True


class CountCommand(Command):
    name = "/count"
    description = "查看当前对话记忆轮数"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """统计当前 Session 中的 user 消息数，作为已保留对话轮数。"""
        user_message_count = context["session"].count_user_messages()
        print("当前聊天记忆轮数为：", user_message_count)
        return True


class ConfigCommand(Command):
    name = "/config"
    description = "查看当前配置"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        """输出当前生效的模型配置摘要，API Key 只显示脱敏结果。"""
        config_summary = get_config_summary()
        print("当前配置：")
        for key, value in config_summary.items():
            print(f"  {key}: {value}")
        return True
