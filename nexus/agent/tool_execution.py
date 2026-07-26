"""不包含 Session、终端输出和 Trace 的工具执行边界。"""

from dataclasses import dataclass
from time import perf_counter

from nexus.agent.policy import ToolRequest
from nexus.tools import ToolResult


@dataclass(frozen=True)
class ToolExecution:
    """一次工具执行产生的请求、结构化结果和耗时。
    把执行的请求，结果，耗时统一打包封装成执行实例
    
    """

    request: ToolRequest
    result: ToolResult
    duration_ms: float

    @property
    def result_text(self) -> str:
        """返回适合终端展示或交给 Planner 的工具结果文本。"""
        return self.result.to_text()

    @property
    def observation(self) -> str:
        """把工具名、参数和结果组合成下一轮 Planner 可读取的 observation。"""
        return (
            f"{self.request.name}({self.request.arguments}) -> {self.result_text}"
        )


def execute_tool(request: ToolRequest) -> ToolExecution:
    """执行一个已通过 Policy 校验的工具请求，并测量完整执行耗时。"""
    started_at = perf_counter()
    result = request.tool.run(request.arguments)
    duration_ms = (perf_counter() - started_at) * 1000
    return ToolExecution(request=request, result=result, duration_ms=duration_ms)
