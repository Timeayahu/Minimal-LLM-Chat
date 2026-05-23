"""应用中的核心数据结构。

这些模型目前使用 TypedDict：
- 运行时仍然是普通 dict。
- 类型标注负责说明每个 dict 应该有哪些字段。
- 不要像普通 class 那样用 Message(...) 创建对象。
"""

from typing import Literal, TypedDict


class Message(TypedDict):
    """一条对话消息。"""

    role: Literal["system", "user", "assistant"]
    content: str
