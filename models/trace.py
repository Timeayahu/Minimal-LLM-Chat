"""Agent 运行过程中的 trace 数据结构。"""

from typing import Any, TypedDict


class AgentStepErrorData(TypedDict):
    """一次 Agent 步骤错误的可保存数据。

    AgentStepErrorData 是 AgentStepTrace.error 字段里的结构化错误对象。
    它的设计目的不是简单保存一段错误字符串，而是让工程师在复盘时能回答：
    “这一步为什么失败？失败属于哪一类？能不能重试？适不适合展示给用户？”

    - kind: 错误类型，例如：ERROR_INVALID_ARGUMENTS、ERROR_UNKNOWN_TOOL、ERROR_PLANNER_INVALID_JSON。

    - message: 人能读懂的错误说明。它描述这次失败具体发生了什么，比如“模型选择了
      未知工具：xxx”或“echo 工具缺少必填参数：text”。message 适合用于
      trace 展示，也可以在 user_visible=True 时转成用户可见提示。

    - retryable: 这个错误是否理论上可以重试。比如参数缺失、planner 输出格式不合法，
      往往可以通过让模型重新规划来修复；但用户取消、权限拒绝、需要确认
      这类状态通常不是自动重试能解决的。

    - user_visible: 这个错误是否适合直接展示给用户。比如“工具参数缺失”可以比较安全地
      展示；但如果 details 里包含内部异常、文件路径、敏感信息，就不应该
      直接暴露给普通用户。

    - details: 面向工程排查的补充信息。它可以保存更细的上下文，例如原始 plan、
      缺失的参数名、实际参数类型、异常类型、可用工具列表等。details 的
      价值是让工程师不用复现也能判断失败发生在哪一层。

    示例：planner 选择了一个不存在的工具时，错误对象可能长这样：

    {
        "kind": "unknown_tool",
        "message": "模型选择了未知工具：weather",
        "retryable": True,
        "user_visible": True,
        "details": {
            "available_tools": ["time", "echo", "confirm_echo"],
        },
    }
    """

    kind: str
    message: str
    retryable: bool
    user_visible: bool
    details: dict[str, Any]


class AgentStepTrace(TypedDict, total=False):
    """一次 Agent Loop 步骤记录。

    - created_at: 这一步是什么时候发生的。用于按时间顺序还原 Agent 行为，也方便排查

    - user_input: 触发这次 Agent Loop 的原始用户输入。注意它不是工具参数，而是用户最初
      说的话。这样即使工具调用已经进入第 2 步、第 3 步，也能知道这一串行为
      是为了回答哪个问题。

    - step: 当前是本轮 Agent Loop 的第几步

    - tool_name: 本步骤选择的工具名

    - arguments: 传给工具的结构化参数。它回答“模型到底生成了什么参数”。很多 Agent
      问题不是工具坏了，而是模型给工具的参数不对，所以 arguments 是复盘
      工具调用时最关键的字段之一。

    - ok:本步骤是否成功。True 表示工具执行成功；False 表示工具失败、planner
      输出不合法、需要用户确认、用户取消等非成功状态。

    - content: 本步骤产生的核心内容。成功时通常是工具返回内容；失败时通常是错误说明；
      需要确认时可以是“该工具需要用户确认”的提示。

    - error: 结构化错误信息。成功时通常是 None；失败时保存 kind、message、retryable、
      user_visible、details，方便后续判断错误类型、是否可重试、是否适合展示给用户。

    - final_answer: 这一轮最终给用户看的回答。如果当前工具步骤只是中间步骤，通常先留空；
      等 Agent 后续生成最终回答时，再补到最近一条 trace 上。这样 /trace 能
      同时看到“工具做了什么”和“用户最终看到了什么”。

    示例：一次 echo 工具调用成功的单步记录可能长这样：

    {
        "created_at": "2026-05-24T20:15:30",
        "user_input": "帮我 echo 一下 hello",
        "step": 1,
        "tool_name": "echo",
        "arguments": {"text": "hello"},
        "ok": True,
        "content": "hello",
        "error": None,
        "final_answer": "echo 工具返回：hello",
    }
    """

    created_at: str
    user_input: str
    step: int
    tool_name: str
    arguments: dict[str, Any]
    ok: bool
    content: str
    error: AgentStepErrorData | None
    final_answer: str


class PendingToolCall(TypedDict):
    """等待用户确认的一次工具调用。"""

    user_input: str
    step: int
    tool_name: str
    arguments: dict[str, Any]
