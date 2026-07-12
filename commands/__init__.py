from commands.basic import (
    ConfigCommand,
    CountCommand,
    HelpCommand,
    ModelCommand,
    ResetCommand,
)
from commands.command import Command
from commands.session import (
    CancelCommand,
    ConfirmCommand,
    ExitCommand,
    ForgetCommand,
    HistoryCommand,
    LoadCommand,
    MemoryCommand,
    MemoriesCommand,
    RememberCommand,
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
        RememberCommand(),
        MemoriesCommand(),
        MemoryCommand(),
        ForgetCommand(),
        TraceCommand(),
        ConfirmCommand(),
        CancelCommand(),
        NewCommand(),
        LoadCommand(),
        ToolCommand(),
        ExitCommand(),
    ]

    return {command.name: command for command in command_list}
