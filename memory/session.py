from dataclasses import dataclass, field
from typing import Any

from agent.trace import ToolTrace
from models import Message

from memory.storage import generate_session_name, init_messages, save_session_data


# 重要：class 定义、__init__、default_factory 的执行时机不同。
#
# 1. 模块被运行或第一次 import 时，Python 会从上到下执行模块代码。
#    执行到 class Session 时，会执行 class 代码块，创建 Session 这个类对象。
#
# 2. 如果写成 name: str = generate_session_name()，这个函数会在 class 定义阶段
#    立刻执行一次；之后所有默认 Session 都会复用这一次算出来的默认值。
#
# 3. __init__ 只有在真正创建实例时才会执行，比如 Session()。
#    但如果字段默认值写成函数调用，比如 name: str = generate_session_name()，
#    这个“默认值表达式”会先在 class 定义阶段执行；dataclass 只是把执行结果
#    放进它生成的 __init__ 默认参数里，并不会在 import 时真正创建 Session 实例。
#
# 4. field(default_factory=generate_session_name) 传入的是函数本身，不是函数结果。
#    dataclass 会在每次执行 Session() 且没有手动传 name 时，再调用它生成默认值。
#    messages 也是同理：每个 Session 都应该拿到一份新的消息列表，不能共享同一个 list。
@dataclass
class Session:
    """
    一个聊天会话。

    dataclass 会根据下面的字段自动生成 __init__ 等基础方法，
    所以我们可以直接写 Session() 来创建一个全新的会话。
    name 和 messages 会分别通过 default_factory 自动生成。
    """

    name: str = field(default_factory=generate_session_name)
    messages: list[Message] = field(default_factory=init_messages)
    traces: list[ToolTrace] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Session":
        """从 JSON 可序列化的数据恢复 Session。"""
        return cls(
            name=data.get("name") or generate_session_name(),
            messages=data.get("messages") or init_messages(),
            traces=data.get("traces") or [],
        )

    def to_dict(self) -> dict[str, Any]:
        """把 Session 转换成 JSON 可序列化的数据。"""
        return {
            "name": self.name,
            "messages": self.messages,
            "traces": self.traces,
        }

    def reset(self) -> None:
        """清空会话消息，但保留 system prompt。"""
        del self.messages[1:]
        self.traces.clear()

    def count_user_messages(self) -> int:
        """统计当前会话中的用户消息数量。"""
        return sum(1 for msg in self.messages if msg["role"] == "user")

    def get_recent_messages(self, limit: int = 10) -> list[Message]:
        """获取当前会话最近的非 system 消息。"""
        chat_messages = [msg for msg in self.messages if msg["role"] != "system"]
        return chat_messages[-limit:]

    def save(self) -> None:
        """保存当前会话。"""
        save_session_data(self.to_dict(), self.name)

    def trim(self, chat_limits: int) -> None:
        """
        记忆压缩：最多保留最近 chat_limits 轮对话。

        保留第 0 条 system prompt，每次删除最早的一轮 user + assistant。
        """
        while self.count_user_messages() > chat_limits:
            del self.messages[1:3]

    def add_tool_trace(self, trace: ToolTrace) -> None:
        """记录一次工具调用过程。"""
        self.traces.append(trace)

    def get_recent_traces(self, limit: int = 10) -> list[ToolTrace]:
        """获取最近的工具调用记录。"""
        return self.traces[-limit:]
