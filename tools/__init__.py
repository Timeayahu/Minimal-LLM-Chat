from tools.basic import echo_text, get_current_time
from tools.spec import ToolSpec


def get_tools() -> dict[str, ToolSpec]:
    """返回当前支持的工具注册表。"""
    tool_list = [
        ToolSpec(
            name="time",
            description="获取当前本地时间，不需要参数。",
            func=get_current_time,
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        ),
        ToolSpec(
            name="echo",
            description="原样返回输入文本，参数是要返回的文本。",
            func=echo_text,
            parameters={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "要原样返回的文本。",
                    },
                },
                "required": ["text"],
                "additionalProperties": False,
            },
        ),
    ]

    return {tool.name: tool for tool in tool_list}
