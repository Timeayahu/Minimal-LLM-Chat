from commands.basic import (
    ConfigCommand,
    CountCommand,
    HelpCommand,
    ModelCommand,
    ResetCommand,
)
from commands.command import Command
from commands.session import (
    ExitCommand,
    HistoryCommand,
    LoadCommand,
    NewCommand,
    SaveCommand,
    TraceCommand,
)
from commands.tool import ToolCommand


def get_commands() -> dict[str, Command]:
    """返回当前支持的命令注册表。"""
    command_list = [
        HelpCommand(),
        ResetCommand(),
        ModelCommand(),
        CountCommand(),
        ConfigCommand(),
        SaveCommand(),
        HistoryCommand(),
        TraceCommand(),
        NewCommand(),
        LoadCommand(),
        ToolCommand(),
        ExitCommand(),
    ]

    return {command.name: command for command in command_list}
