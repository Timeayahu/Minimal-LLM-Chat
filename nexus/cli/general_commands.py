from nexus.agent.observability import new_run_id
from nexus.agent.run_recorder import RunRecorder
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
        """取消可能挂起的 Run，再重置消息和待确认状态，不删除已有 Trace。"""
        session = context["session"]
        pending_tool_call = session.pending_tool_call
        if pending_tool_call is not None:
            run_id = pending_tool_call.get("run_id") or new_run_id()
            RunRecorder(context, run_id).emit(
                "run_cancelled",
                status="cancelled",
                step=pending_tool_call["step"],
                data={
                    "tool_name": pending_tool_call["tool_name"],
                    "reason": "session_reset",
                },
            )

        session.reset()
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
