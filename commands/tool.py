from app_context import AppContext
from commands.command import Command


class ToolCommand(Command):
    name = "/tool"
    description = "手动调用本地工具"

    def execute(self, context: AppContext, args: list[str]) -> bool:
        tools = context["tools"]

        if not args:
            print("可用工具：")
            for tool in tools.values(): #tools.values -> toolspec
                print(f"  {tool.name}: {tool.description}")
            return True

        tool_name = args[0]
        tool_args = args[1:]
        tool = tools.get(tool_name)

        if tool is None:
            print(f"未知工具：{tool_name}")
            print("输入 /tool 查看可用工具。")
            return True

        result = tool.run_cli(tool_args)
        print(f"Tool[{tool_name}]: {result.to_text()}")
        return True
