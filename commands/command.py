"""命令系统的抽象基类。"""

from abc import ABC, abstractmethod

from app_context import AppContext


class Command(ABC):
    """所有命令都需要遵守的统一接口。"""

    name: str = ""
    description: str = ""

    @abstractmethod
    def execute(self, context: AppContext, args: list[str]) -> bool:
        """执行命令，返回程序是否继续运行。"""
        raise NotImplementedError
