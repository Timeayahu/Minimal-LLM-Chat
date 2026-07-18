# Tool Use Flow

这份文档用于复盘第四阶段已经完成的 Tool Use 全链路。

它回答一个核心问题：

```text
用户自然输入一句话后，Agent 到底怎样决定是否调用工具、怎样执行工具、怎样继续规划、怎样记录 trace？
```

## 一句话总览

当前 Tool Use 数据流是：

```text
user input
-> handle_agent_message()
-> _run_agent_loop()
-> decide_agent_step()
-> _handle_final_action() / _handle_tool_action()
-> ToolSpec.run()
-> ToolResult / ToolError
-> observations
-> TraceEvent / JsonlTraceLogger
-> final answer
```

## 入口

普通用户输入会进入 `handle_agent_message()`。

这一层不直接判断具体工具，也不直接拼 prompt。它只负责启动一次 Agent Loop：

```text
handle_agent_message()
-> _run_agent_loop(start_step=1, observations=[], fallback_to_chat=True)
```

这里的关键状态是：

- `user_input`: 用户原始输入
- `observations`: 已有工具观察结果
- `start_step`: 从第几步开始运行
- `fallback_to_chat`: 第一轮如果 planner 直接 final，是否回到普通聊天

## Planner

每一步都会调用 `decide_agent_step()`。

planner 只负责决定下一步动作，不负责执行工具。它必须返回两种 action 之一：

```json
{"action": "tool", "tool": "time", "arguments": {}}
```

或：

```json
{"action": "final", "answer": "最终回答"}
```

这一步的边界很重要：

- 模型只提出计划
- Python 程序负责校验计划
- Python 程序负责执行工具
- Python 程序负责记录 trace 和守住安全边界

## Final 分支

如果 planner 返回 `action == "final"`，Agent 进入 `_handle_final_action()`。

它会处理两种情况：

1. 第一轮没有 observation，并且允许 fallback：交给普通聊天流程。
2. 已经有 observation：把 final answer 输出给用户，并新增 `final_answer` 事件。

这样保留了普通聊天体验：不是每句话都强行变成工具任务。

## Tool 分支

如果 planner 返回 `action == "tool"`，Agent 进入 `_handle_tool_action()`。

执行工具前会依次检查：

- `tool` 字段必须是字符串
- 工具必须存在于工具注册表
- `arguments` 必须是 dict
- 工具如果 `requires_confirmation=True`，必须先暂停并等待用户确认

只有这些边界都通过，才会真正调用：

```text
ToolSpec.run(arguments)
```

## ToolSpec 边界

`ToolSpec.run()` 是工具执行前的统一边界。

它先调用 `validate_arguments()`，根据 `ToolParameters` 检查：

- 必填参数是否缺失
- 是否传入未知参数
- 参数类型是否符合最小 JSON Schema type
- 顶层 schema 是否是当前支持的 object

这意味着 Agent 自动调用和 `/tool` 手动调用会共享同一套参数校验规则。

## ToolResult 与 ToolError

工具不再返回裸字符串，而是返回 `ToolResult`。

成功时：

```text
ok=True
content=工具结果文本
error=None
```

失败时：

```text
ok=False
content=错误提示
error=ToolError(...)
```

`ToolError` 会保存：

- `kind`: 错误码
- `message`: 人能读懂的错误
- `retryable`: 是否理论上可重试
- `user_visible`: 是否适合展示给用户
- `details`: 工程排查信息

## Observation

工具成功后，结果会进入 observations：

```text
time({}) -> 当前时间是 ...
```

下一步 planner 会看到这些 observation，再决定继续调用工具还是生成 final answer。

这就是多步 Agent Loop 的核心：

```text
plan -> act -> observe -> continue/final
```

## Trace

每个 planner、工具、确认、最终回答或 Agent 错误会实时记录为 `TraceEvent`，并由 `JsonlTraceLogger` 追加落盘。

trace 记录的信息包括：

- 用户原始输入
- 第几步
- 工具名
- 工具参数
- 是否成功
- 工具结果或错误内容
- 结构化错误
- 最终回答

`/trace` 读取这些记录，帮助复盘 Agent 当时为什么这么做。

## Confirmation

如果工具设置了：

```text
requires_confirmation=True
```

Agent 不会自动执行它，而是保存为 `pending_tool_call`，并提示用户：

```text
/confirm 执行
/cancel 取消
```

用户确认后，工具结果会作为 observation 回到原任务上下文，继续 Agent Loop。

这一步是未来文件写入、命令执行、网络访问等危险工具的最小权限基础。

## 当前边界

当前实现仍然是教学版，不是最终架构：

- planner 仍使用 JSON prompt，不是正式 OpenAI tool calling
- `nexus/agent/loop.py` 已缩成函数式兼容入口，核心编排位于 `nexus/agent/runtime.py`
- `nexus/agent/policy.py` 负责把 Planner 输出校验为 `ToolRequest`
- 自动调用和 `/confirm` 通过 `nexus/agent/tool_execution.py` 共用同一执行边界
- `nexus/agent/run_recorder.py` 统一补齐 Run 关联字段并记录失败终态
- TraceLogger 已有独立接口，但还没有 metrics 聚合和外部观测后端
- ToolRegistry 仍然是 `dict[str, ToolSpec]`

这些暂时不是问题。第 20 课的目标是先打通最小闭环，第 21 课的目标是把这条链路复盘清楚。

当前已完成 `AgentRuntime`、Policy、工具执行器和 `RunRecorder` 的第一轮拆分。后续当工具数量、权限类型或入口增加后，再升级 `ToolRegistry`、`AgentService` 和更完整的权限策略。
