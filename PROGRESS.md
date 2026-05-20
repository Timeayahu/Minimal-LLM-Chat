# 项目进度

## 总体状态

- 项目：Nexus Agent Kernel（教学型通用 Agent 底座）
- 开始日期：2026-05-03
- 当前阶段：第四阶段 — Tool Use 与 Agent Loop
- 当前课程：第 19 课准备中（ToolError 与更正式的运行 trace）
- 已完成：第 1-18 课主体内容
- 课程路线：阶段式持续迭代
- 长期目标：构建一个小而扎实、可扩展、可研究的通用 Agent Kernel，
  后续可扩展为 Hermes-style、Claude Code-style、Codex-style 等实验分支。

## 课程完成状态

- [x] 第一阶段 第 1 课：跑通最小模型调用
- [x] 第一阶段 第 2 课：加入命令行循环
- [x] 第一阶段 第 3 课：加入多轮对话历史
- [x] 第一阶段 第 4 课：保存和读取历史
- [x] 第一阶段 第 5 课：配置化模型参数
- [x] 第一阶段 第 6 课：整理 README + Git 提交
- [x] 第二阶段 第 7 课：限制对话历史长度
- [x] 第二阶段 第 8 课：增加流式输出
- [x] 第二阶段 第 9 课：增加 `/config` 命令
- [x] 第二阶段 第 10 课：增加 `/history` 命令
- [x] 第二阶段 第 11 课：支持多个聊天历史文件
- [x] 第二阶段 第 12 课：阶段复盘与 Git 标签
- [x] 第三阶段 第 13 课：命令系统重构
- [x] 第三阶段 第 14 课：数据建模与应用上下文
- [x] 第三阶段 第 15 课：Session 行为归属与包化重构
- [x] 第四阶段 第 16 课：最小 Tool Use 入门
- [x] 第四阶段 第 17 课：将 Tool Use 融入普通聊天
- [x] 第四阶段 第 18 课：ToolSpec 标准化、ToolResult 与最小 trace

## 每日日志

### 2026-05-03

- 完成：AI_TUTOR_RULES.md（教学规则文档）
- 完成：课程设计 Skill（skill/minimal-llm-chat/）
- 完成：PROGRESS.md（本文件）
- 完成：requirements.txt + .gitignore（项目骨架）
- 完成：更新 CLAUDE.md（添加项目条目）
- 今日学习：
  - 确定了第一个训练项目：最小 LLM 命令行聊天助手
  - 拆分为 6 节课渐进式学习
  - 固定了技术栈：Python + OpenAI-compatible API + JSON + 命令行
- 明日计划：开始第 1 课 — 跑通最小模型调用

### 2026-05-04

- 完成：第一阶段第 1-6 课，项目已经可以命令行连续聊天、保存历史、读取配置，并推送到 GitHub。
- 完成：重构 `skill/minimal-llm-chat/SKILL.md`，改为阶段式学习路线。
- 完成：在课程 Skill 中加入 Debug 训练和 Git 训练规则。
- 完成：第二阶段第 7 课 — 限制最多保留最近 N 轮对话。
- 今日学习：
  - 理解 `messages` 中 system、user、assistant 的结构。
  - 理解“一轮对话”通常等于一条 user + 一条 assistant。
  - 使用 `while` 和 `del current_memory[1:3]` 删除最早一轮历史，同时保留 system prompt。
  - 通过 `print()` 和卡住位置判断，定位并修复 `while` 条件变量不更新导致的死循环。
  - 使用 `/count` 命令观察当前记忆轮数。
  - 完成 Git 提交并推送到 GitHub。
- Debug 记录：
  - 现象：输入普通问题后程序卡住。
  - 原因：`while` 循环中使用了不会更新的 `user_chat_turns` 变量。
  - 修复：把条件改为每轮重新计算 `check_current_chat_nums(current_memory)`。
- Git 记录：
  - 最新提交：`845b49b`。
  - 当前本地 `main` 已和 `origin/main` 同步。
- 下次计划：第二阶段第 8 课 — 增加流式输出。

### 2026-05-14

- 完成：第二阶段第 8 课 — 增加流式输出。
- 今日学习：
  - 理解普通响应和 stream 响应的区别。
  - 理解 `yield` 会分批把内容交给外层 `for` 循环。
  - 使用 `print(..., end="", flush=True)` 让回答实时显示且不自动换行。
  - 用 `part_of_ans` 收集每个 chunk，最后通过 `"".join(...)` 拼成完整回答。
  - 修复把 generator 直接保存进 `messages` 导致 JSON 历史文件损坏的问题。
- Debug 记录：
  - 现象：程序启动时报 `json.decoder.JSONDecodeError`。
  - 原因：之前把 generator 对象当作 assistant content 保存，导致 `logs/history.json` 写到一半中断。
  - 修复：流式输出时一边打印 chunk，一边收集 chunk，最后只把完整字符串保存进历史。
- 下次计划：第二阶段第 9 课 — 增加 `/config` 命令。

### 2026-05-14

- 完成：第二阶段第 9 课 — 增加 `/config` 命令。
- 今日学习：
  - 理解“配置可观察性”：程序应该能告诉我们当前读到了哪些配置。
  - 使用 `mask_api_key()` 隐藏敏感 API Key，只展示前几位。
  - 使用 `get_config_summary()` 返回字典，集中整理配置摘要。
  - 使用 `for key, value in config_summary.items()` 遍历并打印字典内容。
  - 在 `/help` 中同步补充新命令说明。
- Debug 记录：
  - `/config` 一开始只调用了 `get_config_summary()`，但没有打印返回值。
  - 修复方式：先把返回值保存到 `config_summary`，再遍历打印。
- 下次计划：第二阶段第 10 课 — 增加 `/history` 命令。

### 2026-05-16

- 完成：第三阶段第 13 课 — 命令系统重构。
- 完成：第三阶段第 14 课主体 — 数据建模与应用上下文。
- 今日学习：
  - 使用 `TypedDict` 给字典结构增加类型约束，理解它运行时仍然是普通 dict。
  - 建立 `Message`、`Session`、`AppContext` 三层数据模型。
  - 理解 `Session` 表示当前会话状态，`AppContext` 表示命令执行时可访问的应用上下文。
  - 把旧的 `context["messages"]`、`context["current_session"]` 改为 `context["session"]`。
  - 理解“修改同一个可变对象”和“替换字典中的引用”的区别。
  - 使用 `Session()` 和 `create_app_context()` 收拢初始化逻辑，让 `main.py` 更专注于主循环。
- 设计判断：
  - 当前暂不引入 `dataclass`，因为 `Session` 目前主要还是结构化数据。
  - 当前暂不引入 Pydantic，因为数据来源主要由程序内部控制，还不需要运行时强校验。
- Debug 记录：
  - 重点区分重新绑定局部变量与替换 `context["session"]` 中当前会话的区别。
  - 前者只是重新绑定局部变量；后者才是真正替换应用上下文里的当前会话。
- 下次计划：
  - 继续观察哪些行为应该归属于 `Session`。
  - 如 `reset`、`count_user_messages`、`history` 等行为开始聚集，再评估是否从 `TypedDict` 升级为 `dataclass` 或普通 class。

### 2026-05-17

- 开始：第三阶段第 15 课 — 判断哪些行为应该属于 Session。
- 今日学习：
  - 理解“行为归属”：如果一段逻辑总是在操作 `Session` 内部数据，就应该考虑把它收拢到更靠近 `Session` 的模块。
  - 把 `/reset` 的内部实现从命令层迁移为 `reset_session(session)`。
  - 把 `/count` 的统计逻辑迁移为 `count_session_user_messages(session)`。
  - 把 `/history` 的历史筛选逻辑迁移为 `get_recent_session_messages(session)`，命令层只负责展示。
  - 把保存逻辑迁移为 `save_session(session)`，减少命令层对 `session["messages"]` 和 `session["name"]` 的直接依赖。
  - 将普通聊天入口改为 `handle_chat_message(session, user_input)`，让 `main.py` 不再直接拆出 `session["messages"]`。
  - 将原来的 `memory.py` 升级为 `memory/` 包，拆出 `memory/storage.py` 和 `memory/session.py`。
  - 将 `Session` 从 `TypedDict` 升级为 `dataclass`，访问方式从 `session["name"]` 变为 `session.name`。
  - 将 `reset`、`count_user_messages`、`get_recent_messages`、`save`、`trim` 迁入 `Session` 类，命令层直接调用 `session.xxx()`。
  - 使用 `field(default_factory=...)` 让 `Session()` 每次创建时自动生成新的会话名和新的 messages 列表。
  - 区分 class 定义阶段、`__init__` 实例初始化阶段、`field(default_factory=...)` 默认值生成阶段。
  - 将 `AppContext` 从 `models.py` 拆到 `app_context.py`，避免类型标注依赖和运行时依赖混在一起。
- 设计判断：
  - `Message` 和 `AppContext` 继续保留 `TypedDict`，因为它们目前主要表达结构。
  - `Session` 已升级为 `dataclass`，因为它开始承载会话状态，并且相关行为正在聚集。
  - `Command` 做成 class 的主要原因是统一接口和多态；`Session` 做成 class 的主要原因是状态和行为开始聚集。
- 下次计划：
  - 进入最小 Tool Use：先手写一个本地工具函数，再把工具接入命令或模型调用流程。

### 2026-05-17

- 开始：第四阶段第 16 课 — 最小 Tool Use 入门。
- 今日学习：
  - 理解工具和命令的相似点：都可以通过注册表从名字找到可执行对象。
  - 理解工具和命令的关键区别：命令由用户直接触发，工具未来主要由模型选择后由程序执行。
  - 新增 `tools/` 包，创建 `time` 和 `echo` 两个本地工具函数。
  - 新增工具注册表 `get_tools()`，并将工具注册表放入 `AppContext`。
  - 新增 `/tool` 命令，支持手动查看和调用工具。
  - 新增 `/ask-tool` 命令，让模型先输出工具调用计划，再由 Python 执行工具。
  - 将工具执行结果交回模型，让模型基于工具结果组织最终回答，形成最小 Agent Loop。
  - 理解 `Callable[[list[str]], str]` 表示“满足输入输出形状的可调用对象”。
  - 理解 `__call__` 可以让实例像函数一样被调用，`__init__` 负责初始化对象属性。
  - 将工具从裸函数注册表升级为 `ToolSpec`，让工具拥有 `name`、`description`、`func` 和 `run()`。
- 验证记录：
  - `/tool` 可以列出 `time` 和 `echo`。
  - `/tool time` 可以返回当前时间。
  - `/ask-tool 现在几点` 可以由模型选择 `time` 工具，并基于工具结果回答。
  - `ToolSpec` 重构后，`/tool` 和 `/ask-tool` 均验证通过。
- 第 16 课收尾结论：
  - 当前教学版 JSON 工具计划器适合学习，但存在非法 JSON、弱参数、无 schema、无标准 tool call id、错误处理不结构化等问题。
  - OpenAI-compatible 正式 Tool Calling 的核心流程仍然是：模型返回标准 `tool_calls`，Python 执行工具，再把工具结果发回模型。
  - 当前 `ToolSpec` 还缺 `parameters`、`strict`、`ToolResult`、`ToolError`、权限字段、超时字段和 `to_openai_tool()`。
  - `ToolResult` / `ToolError` 后续需要出现，因为工具执行结果必须从“一段字符串”升级为“可判断、可记录、可恢复的结构化结果”。
  - `/ask-tool` 只是临时训练命令，最终应被普通聊天入口吸收。
- 下次计划：
  - 第 17 课：将 Tool Use 融入普通聊天，让用户自然输入时 Agent 自主判断是否调用工具。
  - 第 18 课：ToolSpec 标准化，加入 parameters / strict / to_openai_tool()。
  - 第 19 课：引入 ToolResult、ToolError 与 trace 日志。
  - 第 20 课：进入多步 Agent Loop 与工具安全边界。


### 2026-05-19

- 开始：第四阶段第 17 课 — 将 Tool Use 融入普通聊天。
- 完成：第四阶段第 17 课 — 将 Tool Use 融入普通聊天。
- 今日学习：
  - 理解 `/ask-tool` 是教学入口，真实 Agent 应该让普通用户输入也进入工具决策流程。
  - 新增 `agent/` 包，建立 `handle_agent_message(context, user_input)` 作为普通输入的 Agent 层入口。
  - 将 `main.py` 的普通聊天分支从 `handle_chat_message(context["session"], user_input)` 改为 `handle_agent_message(context, user_input)`。
  - 当模型计划不需要工具时，Agent 回退到原来的普通聊天流程。
  - 当模型选择工具时，Agent 执行工具、打印工具结果，再让模型基于工具结果生成最终回答。
  - 把工具计划执行逻辑收拢到 `agent/chat.py` 的 `run_planned_tool()`。
  - 新增 `handle_tool_debug_message()`，让 `/ask-tool` 继续作为调试入口，但不再重复 Agent 执行逻辑。
  - 理解“命令层”和“Agent 层”的边界：命令负责解析入口，Agent 负责决策、工具执行和最终回答。
  - 移除 `/ask-tool` 教学调试命令，工具调用只通过自然语言输入由 Agent 自主判断。
- 验证记录：
  - `/tool` 仍可正常列出工具。
  - 直接输入 `现在几点`，不使用 `/ask-tool`，Agent 可以自主选择 `time` 工具并回答。
  - 直接输入 `你好`，Agent 判断不需要工具后，可以正常走普通聊天回答。
  - `python -m py_compile main.py chat.py agent/chat.py commands/tool.py tools/planner.py` 通过。
- 下次计划：
  - 第 18 课：ToolSpec 标准化，加入 parameters / strict / to_openai_tool()。
  - `/tool` 暂时保留为手动调试工具入口。

### 2026-05-19

- 开始：第四阶段第 18 课 — ToolSpec 标准化。
- 今日学习：
  - 为 `ToolSpec` 增加 `parameters`，用 JSON Schema 描述工具参数。
  - 为 `ToolSpec` 增加 `strict`，表达是否要求模型严格遵守参数 schema。
  - 为 `ToolSpec` 增加 `to_openai_tool()`，把本地工具定义转换为 OpenAI-compatible tools 结构。
  - 为 `time` 工具补充“无参数”的 schema。
  - 为 `echo` 工具补充 `text` 字符串参数的 schema。
  - 让教学版 planner 在提示词中展示每个工具的参数 schema。
  - 基于“先痛点，后抽象”的教学节奏，将 `run_planned_tool()` 合回 `handle_agent_message()`。
  - 将工具计划中的 `args: list` 升级为 `arguments: dict`，让模型输出的参数形状和 JSON Schema 保持一致。
  - 将工具函数的输入从 `list[str]` 升级为 `dict[str, Any]`。
  - 为 `ToolSpec` 增加 `run_cli()`，让 `/tool` 命令行调试入口继续接收字符串列表，再转换为结构化参数。
- 设计判断：
  - 本课从“工具定义标准化”推进到“工具执行参数结构化”，解决 schema 和实际参数形状不一致的问题。
  - `to_openai_tool()` 目前先作为结构转换能力存在，后续再接入正式 tool calling API 流程。
  - `/ask-tool` 移除后，工具执行逻辑暂时只有一个调用入口，因此先保持线性代码更利于理解。
  - 等后续加入 `ToolResult`、`ToolError`、trace 或多步循环后，如果 `handle_agent_message()` 明显变长，再重新抽出工具执行函数。
  - 自然语言 Agent 和命令行调试入口的参数来源不同：Agent 使用结构化 `arguments`，`/tool` 使用 CLI 字符串，因此在 `ToolSpec` 里保留一个小适配层。
- 验证记录：
  - `python -m py_compile main.py agent/chat.py commands/tool.py tools/spec.py tools/__init__.py tools/planner.py` 通过。
  - `time` 和 `echo` 均可成功导出 OpenAI-compatible tool JSON。
  - `python -m py_compile agent/chat.py main.py` 通过。
  - `python -m py_compile agent/chat.py commands/tool.py tools/spec.py tools/basic.py tools/planner.py` 通过。
  - `time.run({})`、`echo.run({"text": "..."})`、`echo.run_cli([...])` 均验证通过。
- 下次计划：
  - 引入 `ToolResult` / `ToolError`，让工具成功和失败不再只是一段字符串。

### 2026-05-20

- 继续：第四阶段第 18 课 — ToolResult 入门。
- 今日学习：
  - 识别当前痛点：工具成功结果和工具错误都只是字符串，程序无法可靠区分。
  - 新增 `ToolResult`，用 `ok` 表示成功或失败，用 `content` 保存结果文本，用 `error_type` 保存错误类型。
  - 为 `ToolResult` 增加 `success()`、`failure()` 和 `to_text()`。
  - 将工具函数返回值从 `str` 升级为 `ToolResult`。
  - `ToolSpec.run()` 捕获工具内部异常，并转换为失败的 `ToolResult`。
  - `agent/chat.py` 和 `/tool` 命令通过 `result.to_text()` 展示和回传工具结果。
- 设计判断：
  - 本次先只引入 `ToolResult`，暂不单独创建 `ToolError` 类，避免抽象过早。
  - 现在最重要的是让程序内部先能判断 `result.ok`，后续 trace 和错误处理会基于它继续展开。
- 验证记录：
  - `python -m py_compile agent/chat.py commands/tool.py tools/spec.py tools/basic.py tools/__init__.py` 通过。
  - 验证了 `time.run({})`、`time.run({"extra": "x"})`、`echo.run({"text": "hello"})`、`echo.run({})`、`echo.run_cli([...])` 的成功和失败路径。
- 下次计划：
  - 在 Agent 层根据 `result.ok` 做不同处理。
  - 开始记录最小工具调用 trace。

### 2026-05-20

- 继续：第四阶段第 18 课 — Agent 使用 ToolResult。
- 今日学习：
  - 识别当前痛点：虽然工具已经返回 `ToolResult.ok`，但 Agent 还没有使用这个成功/失败信号。
  - 在 `agent/chat.py` 中增加失败分支：当 `result.ok` 为 `False` 时，直接向用户展示工具失败信息，并结束本轮处理。
  - 保持成功分支不变：当 `result.ok` 为 `True` 时，继续把工具结果交给模型组织最终回答。
- 设计判断：
  - 工具失败时暂时不再调用模型二次总结，避免把错误结果伪装成正常工具观察。
  - 这一步让 `ToolResult` 从“只是数据结构”变成了真正参与 Agent 控制流的信号。
- 验证记录：
  - `python -m py_compile agent/chat.py` 通过。
  - `echo.run({})` 返回 `ok=False`，并能通过 `to_text()` 转成明确失败文本。
- 下次计划：
  - 开始记录最小工具调用 trace。

### 2026-05-20

- 继续：第四阶段第 18 课 — 最小工具调用 trace。
- 今日学习：
  - 识别当前痛点：工具调用过程只打印在屏幕上，程序内部没有保存，后续难以复盘模型选了什么工具、传了什么参数、工具是否成功。
  - 新增 `ToolTrace`，描述一次工具调用记录的结构。
  - 为 `Session` 增加 `traces` 列表，用来保存当前会话内的工具调用记录。
  - 为 `Session` 增加 `add_tool_trace()`，让记录 trace 的行为归属于会话对象。
  - 在 `agent/chat.py` 工具执行后写入 trace，记录 `tool_name`、`arguments`、`ok`、`content`、`error_type`。
- 设计判断：
  - 本次只做内存 trace，不写文件，也不急着做 `/trace` 命令。
  - 先把“记录 trace”和“展示 trace”分开，避免一次引入太多变化。
- 验证记录：
  - `python -m py_compile models.py memory/session.py agent/chat.py` 通过。
  - 手动创建 `Session()` 并调用 `add_tool_trace()`，确认 `session.traces` 可以保存工具调用记录。
- 下次计划：
  - 增加查看 trace 的命令行入口。

### 2026-05-20

- 继续：第四阶段第 18 课 — 查看工具调用 trace。
- 今日学习：
  - 识别当前痛点：trace 已经记录到 `Session.traces`，但还没有命令行入口可以查看。
  - 新增 `/trace` 命令，用于查看最近 10 条工具调用记录。
  - `/trace` 展示工具名、参数、成功状态、错误类型和结果内容。
  - 将 `/trace` 注册进命令注册表，并更新 README 常用命令说明。
- 设计判断：
  - `/history` 查看聊天消息，`/trace` 查看工具调用过程，两者都属于当前 Session 的观察入口。
  - 本次只做展示，不做 trace 持久化，避免把“查看当前运行过程”和“长期日志存储”混在一起。
- 验证记录：
  - `python -m py_compile commands/session.py commands/__init__.py` 通过。
  - 手动创建一条 trace 后执行 `/trace`，可以正常打印工具调用记录。
  - 命令注册表中已包含 `/trace`。
- 下次计划：
  - 评估第 18 课是否收尾。
  - 后续进入第 19 课：更正式的 trace 结构、错误处理和 Agent Loop 边界。

### 2026-05-20

- 继续：第四阶段第 18 课 — trace 结构增强。
- 今日学习：
  - 识别当前痛点：最小 trace 只能看到工具本身，不能完整复盘“用户输入 -> 工具调用 -> 最终回答”。
  - 为 `ToolTrace` 增加 `created_at`、`user_input` 和 `final_answer` 字段。
  - 为 `Session` 增加 `get_recent_traces()`，让读取最近 trace 的行为归属于会话对象。
  - 将 `agent/chat.py` 的 trace 写入时机调整到最终回答生成之后，保证每条 trace 是完整闭环。
  - 更新 `/trace` 展示内容，补充时间、用户输入和最终回答。
- 设计判断：
  - 成功分支和失败分支目前都有一段相似的 trace 写入代码，暂时不抽函数。
  - 等后续 trace 字段继续增加或写入逻辑变复杂，再考虑抽出统一记录函数。
- 验证记录：
  - `python -m py_compile models.py memory/session.py agent/chat.py commands/session.py` 通过。
  - 手动创建完整 trace 后执行 `/trace`，可以正常展示 `Time`、`User`、`Tool`、`Arguments`、`OK`、`Content`、`Final`。
- 下次计划：
  - 评估第 18 课收尾，并整理进入第 19 课前的边界。

### 2026-05-20

- 继续：第四阶段第 18 课 — Session 持久化升级。
- 今日学习：
  - 识别当前痛点：`Session` 已经包含 `messages` 和 `traces`，但旧的 `save()` 只保存 `messages`，导致 trace 退出程序后丢失。
  - 理解不能直接把 Python 对象写进 JSON，需要先转换成 JSON 可序列化的数据结构。
  - 为 `Session` 增加 `to_dict()`，把会话对象转换成包含 `name`、`messages`、`traces` 的 dict。
  - 为 `Session` 增加 `from_dict()`，为后续从文件恢复完整 Session 做准备。
  - 新增 `save_session_data()` 和 `load_session_data()`，用于保存和读取完整会话快照。
  - 保留旧的 `save_history()` / `load_history()`，并让 `load_history()` 读取新格式时仍然只返回 `messages`，兼容旧接口。
- 设计判断：
  - 不保存整个 `AppContext`，因为其中包含 commands、tools、函数引用等不适合 JSON 持久化的运行时对象。
  - 保存的是 Session 的“数据快照”，不是 Python 对象本身。
  - 本次先升级保存格式，暂不做“选择旧 session 并恢复”的交互入口。
- 验证记录：
  - `python -m py_compile memory/storage.py memory/session.py memory/__init__.py commands/session.py` 通过。
  - 创建带 trace 的测试 `Session` 并调用 `save()`，`load_session_data()` 可以读回 `traces`。
  - `load_history()` 读取新格式文件时仍返回 `messages` 列表。
- 下次计划：
  - 增加从 session 快照恢复完整 Session 的入口，或先收尾第 18 课。

### 2026-05-20

- 完成：第四阶段第 18 课 — 收尾：从 Session 快照恢复完整会话。
- 今日学习：
  - 识别当前痛点：已经能保存完整 Session 快照，但程序还没有入口把它恢复成当前会话。
  - 新增 `list_session_names()`，用于列出 `logs/` 下已经保存过的会话文件。
  - 新增 `/load` 命令：不带参数时列出可加载会话，带会话名时读取完整快照。
  - `/load 会话名` 会先保存当前会话，再用 `Session.from_dict()` 替换 `context["session"]`。
  - 恢复后的会话同时包含 `messages` 和 `traces`，不再只恢复聊天历史。
- 设计判断：
  - `/new` 负责开启新会话，`/save` 负责保存当前会话，`/load` 负责恢复旧会话，三者组成最小 session 生命周期。
  - 当前只按会话名加载，不做交互选择界面，保持命令行入口简单直接。
  - 这一步让第 18 课形成闭环：工具定义标准化、工具结果结构化、trace 可查看且可持久化恢复。
- 验证记录：
  - `python -m py_compile memory/storage.py memory/session.py memory/__init__.py commands/session.py commands/__init__.py main.py` 通过。
  - 手动创建带 trace 的测试 Session，保存后通过 `LoadCommand` 加载，确认 `messages` 和 `traces` 都能恢复。
- 第 18 课收尾结论：
  - 已完成 `ToolSpec.parameters`、`strict`、`to_openai_tool()`。
  - 已完成结构化 `ToolResult`，Agent 能根据 `result.ok` 区分成功和失败。
  - 已完成最小工具调用 trace，并支持 `/trace` 查看、随 Session 保存和 `/load` 恢复。
- 下次计划：
  - 进入第 19 课：补 `ToolError` 边界、更正式的 trace 结构，以及 Agent Loop 前的错误处理整理。
