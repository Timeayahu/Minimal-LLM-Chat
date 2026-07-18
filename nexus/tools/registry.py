from nexus.tools.builtins import echo_text, get_current_time
from nexus.tools.core import ToolParameters, ToolSpec


def get_tools() -> dict[str, ToolSpec]:
    """返回当前支持的工具注册表。"""
    tool_list = [
        ToolSpec(
            name="time",
            description="获取当前本地时间，不需要参数。",
            func=get_current_time,
            parameters=ToolParameters(
                properties={},
                required=[],
            ),
        ),
        ToolSpec(
            name="echo",
            description="原样返回输入文本，参数是要返回的文本。",
            func=echo_text,
            parameters=ToolParameters(
                properties={
                    "text": {
                        "type": "string",
                        "description": "要原样返回的文本。",
                    },
                },
                required=["text"],
            ),
        ),
        ToolSpec(
            name="confirm_echo",
            description="需要用户确认后，才会原样返回输入文本。",
            func=echo_text,
            parameters=ToolParameters(
                properties={
                    "text": {
                        "type": "string",
                        "description": "要在确认后原样返回的文本。",
                    },
                },
                required=["text"],
            ),
            requires_confirmation=True,
        ),
    ]

    return {tool.name: tool for tool in tool_list}
