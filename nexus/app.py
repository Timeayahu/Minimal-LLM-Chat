from typing import TYPE_CHECKING, Any, TypedDict

from nexus.context import MemoryStore, Session
from nexus.tools import ToolSpec

if TYPE_CHECKING:
    from nexus.agent.observability import TraceLogger


class AppContext(TypedDict):
    """命令执行时能访问的应用上下文。"""

    session: Session
    memory_store: MemoryStore
    commands: dict[str, Any]
    tools: dict[str, ToolSpec]
    trace_logger: "TraceLogger"


def create_app_context() -> AppContext:
    """在应用启动时组装 Session、Memory、Commands、Tools 和 TraceLogger。"""
    # 局部导入避免 Command 抽象在导入阶段反向依赖 AppContext。
    from nexus.agent.observability import JsonlTraceLogger
    from nexus.cli import get_commands
    from nexus.tools import get_tools

    return {
        "session": Session(),
        "memory_store": MemoryStore.load(),
        "commands": get_commands(),
        "tools": get_tools(),
        "trace_logger": JsonlTraceLogger(),
    }
