# 项目进度

## 总体状态

- 项目：Nexus Agent Kernel（教学型通用 Agent 底座）
- 开始日期：2026-05-03
- 当前阶段：第四阶段 — Tool Use 与 Agent Loop
- 当前课程：第 20 课已完成（多步 Agent Loop 与工具安全边界）
- 已完成：第 1-20 课主体内容
- 课程路线：阶段式持续迭代
- 长期目标：构建一个小而扎实、可扩展、可研究的通用 Agent Kernel，
  后续可扩展为 Hermes-style、Claude Code-style、Codex-style 等实验分支。
- 最新架构判断：已将 `Agent_Kernel_架构分层与设计模式说明.docx` 的核心思想纳入课程 Skill。
  当前不做一次性大重构，先以“架构北极星 + 渐进式重构触发条件”的方式指导后续课程。

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
- [x] 第四阶段 第 19 课：ToolError 与更正式的运行 trace
- [x] 第四阶段 第 20 课：多步 Agent Loop 与工具安全边界

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

#### 完成：第二阶段第 8 课 — 增加流式输出。

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

#### 完成：第二阶段第 9 课 — 增加 `/config` 命令。

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

#### 开始：第三阶段第 15 课 — 判断哪些行为应该属于 Session。

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

#### 开始：第四阶段第 16 课 — 最小 Tool Use 入门。

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

#### 开始：第四阶段第 17 课 — 将 Tool Use 融入普通聊天。

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

#### 开始：第四阶段第 18 课 — ToolSpec 标准化。

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

#### 继续：第四阶段第 18 课 — ToolResult 入门。

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

#### 继续：第四阶段第 18 课 — Agent 使用 ToolResult。

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

#### 继续：第四阶段第 18 课 — 最小工具调用 trace。

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

#### 继续：第四阶段第 18 课 — 查看工具调用 trace。

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

#### 继续：第四阶段第 18 课 — trace 结构增强。

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

#### 继续：第四阶段第 18 课 — Session 持久化升级。

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

#### 完成：第四阶段第 18 课 — 收尾：从 Session 快照恢复完整会话。

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

#### 课程路线调整：第六阶段从“最小 RAG 从零实现”改为“RAG 框架技术评审与集成实战”。

- 调整原因：
  - 学生已经熟悉 RAG 基础概念，不需要再把时间花在手写最小 loader / chunker / retriever。
  - 第六阶段更适合训练真实工程里的框架选型、文档阅读、抽象理解和项目集成能力。
- 新方向：
  - 先评审 LlamaIndex、LangChain / LangGraph、Haystack、AutoGen 相关方案等候选框架。
  - 正式进入第六阶段时，基于当时最新文档和项目状态选定一个主框架。
  - 使用选定框架完成资料导入、切分、索引、检索、引用来源和基于资料回答。
  - 保留轻量适配层，避免 Nexus Agent Kernel 被某个框架完全锁死。

### 2026-05-23

#### 开始：第四阶段第 19 课 — ToolError 与更正式的运行 trace。

- 今日学习：
  - 识别当前痛点：`ToolResult` 只有 `content` 和 `error_type`，不足以表达错误是否可重试、是否适合展示给用户、是否有额外细节。
  - 新增 `ToolError`，包含 `kind`、`message`、`retryable`、`user_visible`、`details`。
  - 将 `ToolResult.failure()` 改为创建结构化 `ToolError`，同时保留 `error_type` 属性兼容旧读取方式。
  - 将工具 trace 中的 `error_type` 升级为 `error` 结构。
  - 更新 `/trace` 展示，让它能显示 `Error`、`Error message` 和 `Retryable`，并兼容旧 trace。
- 设计判断：
  - `ToolResult` 表示“工具执行的结果”，`ToolError` 表示“失败的性质和处理提示”，两者职责开始分开。
  - `invalid_arguments` 标记为 `retryable=True`，因为后续多步 Agent Loop 可以尝试让模型修正参数后重试。
  - 暂时不引入异常类层级，先用数据结构表达 Agent 可理解、可保存、可展示的错误状态。
- 验证记录：
  - `python -m py_compile tools/spec.py tools/basic.py models.py agent/chat.py commands/session.py` 通过。
  - 手动验证 `echo.run({})` 返回 `ok=False`，并生成结构化 `ToolError`。
  - 手动验证 `/trace` 可以展示新结构的 `error` 字段。
- 下次计划：
  - 将 Agent 层的未知工具、计划格式错误、参数格式错误也统一写入 trace。

#### 继续：第四阶段第 19 课 — trace 类型归属整理。

- 今日学习：
  - 识别当前痛点：`models.py` 同时放了通用 `Message` 和工具调用 trace 类型，职责开始混杂。
  - 新增 `agent/trace.py`，用于放 Agent 运行过程中的 trace 数据结构。
  - 将 `ToolErrorData` 和 `ToolTrace` 从 `models.py` 迁移到 `agent/trace.py`。
  - `models.py` 现在只保留跨模块通用的 `Message`。
  - `memory/session.py` 改为从 `agent.trace` 引入 `ToolTrace`。
- 设计判断：
  - `ToolTrace` 虽然记录工具调用，但它不是工具定义本身，而是 Agent 对一次运行过程的观察记录。
  - 因此它放在 `agent/trace.py` 比放在 `tools/` 更贴近当前职责。
- 验证记录：
  - `python -m py_compile models.py agent/trace.py memory/session.py memory/storage.py agent/chat.py commands/session.py` 通过。
- 下次计划：
  - 将 Agent 层的未知工具、计划格式错误、参数格式错误也统一写入 trace。

#### 继续：第四阶段第 19 课 — Agent 决策阶段错误写入 trace。

- 今日学习：
  - 识别当前痛点：之前 trace 只记录工具函数真正执行后的结果；如果模型计划格式错误、选择未知工具、参数形状错误，这些失败只会打印在屏幕上，无法复盘。
  - 在 `tools/planner.py` 中为“模型没有返回合法 JSON”增加结构化 `error` 字段。
  - 在 `agent/chat.py` 中新增 `_record_agent_error()`，统一记录工具执行前的 Agent 错误。
  - 将 `planner_invalid_json`、`invalid_tool_name`、`unknown_tool`、`invalid_tool_arguments` 写入 trace。
  - 这些错误都暂时标记为 `retryable=True`，为后续多步 Agent Loop 中“让模型修正后重试”做准备。
- 设计判断：
  - 工具执行失败和 Agent 决策失败都属于一次 Agent 运行过程的一部分，都应该进入 trace。
  - 当前仍然使用 `ToolTrace` 这个名字，但语义已经开始靠近“Agent 运行记录”；后续进入多步 loop 时可继续升级命名。
- 验证记录：
  - `python -m py_compile agent/chat.py tools/planner.py tools/spec.py agent/trace.py commands/session.py` 通过。
  - 手动调用 `_record_agent_error()`，确认 unknown tool 错误可以写入 `session.traces` 并通过 `/trace` 展示。
- 下次计划：
  - 评估是否将 `ToolTrace` 命名升级为更通用的 `AgentTrace` / `AgentStepTrace`，或先进入多步 Agent Loop 前的收尾整理。

#### 完成：第四阶段第 19 课 — ToolError 与更正式的运行 trace。

- 第 19 课收尾结论：
  - 已完成 `ToolError` 结构化，工具失败不再只靠字符串或 `error_type` 表达。
  - 已完成 `ToolResult.failure()` 到 `ToolError` 的转换，保留 `error_type` 属性兼容旧代码。
  - 已完成 trace 从 `error_type` 到 `error` 结构的升级。
  - 已完成 `/trace` 对结构化错误的展示，并兼容旧 trace。
  - 已将 trace 类型从 `models.py` 迁移到 `agent/trace.py`，让 `models.py` 回到通用数据模型职责。
  - 已将 Agent 决策阶段错误写入 trace，包括 `planner_invalid_json`、`invalid_tool_name`、`unknown_tool`、`invalid_tool_arguments`。
- 设计判断：
  - 第 19 课完成了从“工具能失败”到“Agent 能理解、保存、展示失败”的升级。
  - 当前仍保留 `ToolTrace` 命名，后续第 20 课进入多步 Agent Loop 时，再根据真实结构评估是否升级为 `AgentTrace` / `AgentStepTrace`。
- 下次计划：
  - 进入第 20 课：多步 Agent Loop 与工具安全边界，引入 `max_steps`，让 Agent 支持 plan -> act -> observe -> continue / final。

#### 开始：第四阶段第 20 课 — 多步 Agent Loop 与工具安全边界。

- 今日学习：
  - 识别当前痛点：原来的 Agent 只能执行“规划一次 -> 调用一个工具 -> 总结一次”，无法表达 `plan -> act -> observe -> continue / final` 这种多步循环。
  - 新增 `MAX_AGENT_STEPS = 3`，让 Agent Loop 有明确上限，避免模型反复要求调用工具导致无限循环。
  - 新增 `decide_agent_step()`，让模型每一步输出 `{"action": "tool", ...}` 或 `{"action": "final", ...}`。
  - 在 `handle_agent_message()` 中引入 `observations`，每次工具结果都会成为下一步规划的观察信息。
  - 将工具执行展示从 `Tool[tool]` 升级为 `Tool[step:tool]`，方便观察多步执行顺序。
  - 为 trace 增加 `step` 字段，并在 `/trace` 中展示步骤编号。
  - 为 `ToolSpec` 增加最小安全边界字段：`is_readonly`、`requires_confirmation`、`timeout_seconds`。
  - 在 Agent Loop 中加入确认边界：如果工具标记为 `requires_confirmation=True`，当前自动循环不会静默执行它，而是记录结构化错误并停止。
- 设计判断：
  - 本课先保留教学版 JSON planner，不急着接正式 OpenAI tool calling，因为当前重点是理解 Agent Loop 的控制流。
  - `max_steps` 是 Agent 的安全边界之一：它不解决所有问题，但先解决“无限循环”这个最直接的风险。
  - 当前工具都是只读工具，因此安全字段先作为结构和边界检查存在；后续加入文件、命令、网络等危险工具时再继续扩展确认流程。
  - 成功工具步骤会先写入 trace，最终回答生成后再补到最近一条 trace，便于 `/trace` 复盘本轮闭环。
- 验证记录：
  - `python -m py_compile agent/chat.py tools/planner.py tools/spec.py agent/trace.py commands/session.py tools/__init__.py tools/basic.py main.py` 通过。
  - smoke test 通过：模拟 planner 第 1 步调用 `time`，第 2 步返回 `final`，trace 能记录 `step=1` 和最终回答。
  - smoke test 通过：模拟 planner 选择未知工具，Agent 能写入 `unknown_tool` 错误 trace。
- 下次计划：
  - 继续第 20 课：评估是否把 `ToolTrace` 升级为 `AgentStepTrace`，并加入更细的工具参数校验或确认交互。

#### 继续：第四阶段第 20 课 — 将 ToolTrace 升级为 AgentStepTrace。

- 今日学习：
  - 识别当前痛点：进入多步 Agent Loop 后，trace 记录的不再只是工具调用，还包括 planner 错误、未知工具、步骤编号和最终回答。
  - 将 `ToolTrace` 改名为 `AgentStepTrace`，让类型名称贴合“一次 Agent Loop 步骤记录”。
  - 将 `ToolErrorData` 改名为 `AgentStepErrorData`，让错误数据归属于 Agent 步骤，而不是只归属于工具。
  - 将 `Session.add_tool_trace()` 改名为 `Session.add_agent_step_trace()`。
  - `/trace` 的展示文案从“工具调用记录”改为“Agent 步骤记录”。
  - 保留 `Session.traces` 和保存文件中的 `traces` 字段不变，避免破坏旧会话文件兼容性。
  - 修复一个循环导入问题：`agent/__init__.py` 改为按需导出 `handle_agent_message`，避免导入 `agent.trace` 时提前加载 `agent.chat`。
- 设计判断：
  - 本次只改命名和职责边界，不改变 trace 的 JSON 存储字段，降低对历史数据的影响。
  - `AgentStepTrace` 比 `ToolTrace` 更适合后续扩展，例如记录 planner step、tool step、final step 或 confirmation step。
  - 包的 `__init__.py` 不应该太重，否则很容易因为类型模块互相引用触发循环导入。
- 验证记录：
  - `python -m py_compile agent/__init__.py agent/trace.py memory/session.py agent/chat.py commands/session.py main.py` 通过。
  - `from memory import Session` 后调用 `add_agent_step_trace()` 验证通过。
  - `from agent import handle_agent_message` 入口导出验证通过。
  - smoke test 通过：模拟 planner 第 1 步调用 `time`，第 2 步返回 `final`，trace 能记录 `step=1` 和最终回答。
- 下次计划：
  - 继续第 20 课：加入更细的工具参数校验，或开始设计需要确认的危险工具执行流程。

#### 继续：第四阶段第 20 课 — 工具参数校验。

- 今日学习：
  - 识别当前痛点：虽然 `ToolSpec` 已经有 JSON Schema 形式的 `parameters`，但执行工具前只检查了 `arguments` 是否为 dict，还没有真正按 schema 校验。
  - 为 `ToolSpec.run()` 增加统一参数校验入口，确保 Agent 调用和 `/tool` 手动调用都会经过同一层边界。
  - 新增 `ToolSpec.validate_arguments()`，支持当前项目已经用到的最小 JSON Schema 子集：`type: object`、`properties`、`required`、`additionalProperties: False` 和基础字段类型。
  - 新增 `_matches_json_schema_type()`，把 JSON Schema 的 `string`、`integer`、`number`、`boolean`、`object`、`array`、`null` 映射到 Python 类型检查。
  - 当参数缺失、多余或类型错误时，统一返回 `ToolResult.failure(..., error_type="invalid_arguments", retryable=True)`。
- 设计判断：
  - 本课暂不引入完整 JSON Schema 依赖，先实现项目当前工具实际需要的最小校验能力。
  - 参数校验放在 `ToolSpec.run()`，而不是分散在 Agent 或 CLI 层，因为工具边界应该由工具定义自己守住。
  - 工具函数内部仍可以保留业务层检查；schema 校验负责结构和类型，工具函数负责更具体的业务规则。
- 验证记录：
  - `python -m py_compile tools/spec.py tools/basic.py tools/__init__.py agent/chat.py` 通过。
  - 验证 `time.run({})` 成功，`time.run({"extra": "x"})` 返回 `invalid_arguments`。
  - 验证 `echo.run({})` 缺少必填参数，`echo.run({"text": 123})` 类型错误，`echo.run({"text": "hello"})` 成功。
  - smoke test 通过：模拟 Agent 调用 `echo` 且传入错误类型参数，trace 能记录 `invalid_arguments` 且 `retryable=True`。
- 下次计划：
  - 继续第 20 课：设计 `requires_confirmation=True` 工具的确认流程。

#### 继续：第四阶段第 20 课 — ToolParameters 与错误码常量化。

- 今日学习：
  - 识别当前痛点：`ToolSpec.parameters` 只是裸 `dict`，只有读到 `parameters.get("required")` 时才知道它内部约定了 `required` 字段。
  - 新增 `ToolParameters`，显式表达工具参数 schema 中的 `properties`、`required`、`additional_properties` 和 `schema_type`。
  - `ToolSpec.parameters` 从 `dict[str, Any]` 升级为 `ToolParameters`。
  - `ToolParameters.to_dict()` 负责导出 OpenAI-compatible JSON Schema dict，保证本地建模和外部协议之间有清楚转换点。
  - 新增 `tools/error_codes.py`，集中保存 `invalid_arguments`、`tool_exception`、`planner_invalid_json` 等错误码常量。
  - 将工具层、planner 层和 Agent 层的主要错误类型从裸字符串替换为统一常量。
- 设计判断：
  - `ToolParameters` 不是替代 JSON Schema，而是给本地代码加一层明确结构；对外仍通过 `to_dict()` 输出标准 schema。
  - 错误码常量化可以减少拼写漂移，例如避免 `invalid_argument` 和 `invalid_arguments` 这种隐蔽不一致。
  - 当前仍保留 `ToolArguments = dict[str, Any]`，因为运行时参数来自模型输出，内容本身仍然是动态 JSON。
- 验证记录：
  - `python -m py_compile tools/error_codes.py tools/spec.py tools/basic.py tools/__init__.py tools/planner.py agent/chat.py` 通过。

#### 继续：第四阶段第 20 课 — 待确认工具调用流程。

- 今日学习：
  - 识别当前痛点：`requires_confirmation=True` 之前只能阻止自动执行，还没有让用户确认后继续执行的入口。
  - 新增 `PendingToolCall`，用于记录等待确认的工具调用，包括用户输入、步骤编号、工具名和参数。
  - 为 `Session` 增加 `pending_tool_call`，并提供 `set_pending_tool_call()` / `clear_pending_tool_call()`。
  - Agent 选到需要确认的工具时，不再直接当作普通失败结束，而是保存 pending 调用，并提示用户输入 `/confirm` 或 `/cancel`。
  - 新增 `/confirm` 命令：执行等待确认的工具，打印工具结果，写入新的 Agent step trace，并清空 pending 状态。
  - 新增 `/cancel` 命令：取消等待确认的工具调用，写入取消 trace，并清空 pending 状态。
  - 新增 `confirm_echo` 演示工具，用于观察需要确认的工具执行流程。
- 设计判断：
  - 待确认调用属于当前会话状态，因此先放在 `Session`，而不是放进全局 `AppContext`。
  - `/confirm` 暂时只执行挂起工具，不继续进入完整多步 planner，总体更适合教学阶段观察权限边界。
  - `traces` 字段继续保存 Agent 步骤记录；`pending_tool_call` 单独保存当前还没执行的动作，两者语义不同。
- 验证记录：
  - `python -m py_compile agent/trace.py memory/session.py agent/chat.py commands/session.py commands/__init__.py tools/__init__.py` 通过。
  - smoke test 通过：模拟 planner 选择 `confirm_echo` 后，Session 能保存 pending 调用。
  - smoke test 通过：执行 `/confirm` 后工具正常运行，pending 状态清空，并追加成功 trace。
  - smoke test 通过：执行 `/cancel` 后 pending 状态清空，并追加取消 trace。

#### 继续：第四阶段第 20 课 — 确认后继续 Agent Loop。

- 今日学习：
  - 识别当前痛点：`/confirm` 虽然能执行工具，但只会输出“已确认并执行……”，没有把工具结果交回 planner 形成真正的最终回答。
  - 新增 `continue_agent_loop_after_confirmed_tool()`，让确认后的工具结果作为 observation 继续进入 Agent Loop。
  - `/confirm` 执行工具后不再直接拼接最终回答，而是记录工具 step trace，再把工具观察结果交回 planner。
  - 如果确认后的工具执行失败，Agent 会直接把失败信息作为最终回答，并把最终回答补到最新 trace。
  - 如果确认后的工具执行成功，planner 会基于 observation 继续选择 `final` 或下一次工具调用。
- 设计判断：
  - 这一步让 `requires_confirmation` 更接近真实 Agent 的权限暂停点：工具执行前暂停，确认后回到原任务上下文继续完成目标。
  - 当前 `continue_agent_loop_after_confirmed_tool()` 和 `handle_agent_message()` 有一些重复控制流，先接受这个教学阶段的重复；下一步可以抽出统一的 Agent Loop 执行器。
  - `/confirm` 不应该重新保存用户输入，因为用户原始输入已经在第一次触发 pending 工具时进入了 session messages。
- 验证记录：
  - `python -m py_compile main.py app_context.py chat.py llm_client.py models.py commands/*.py memory/*.py tools/*.py agent/*.py` 通过。
  - smoke test 通过：`/confirm` 后 planner 能看到 `confirm_echo({'text': 'hello'}) -> hello` 这样的 observation，并生成最终回答。
  - smoke test 通过：确认后的工具参数错误时，pending 状态会清空，trace 会记录失败最终回答。

#### 继续：第四阶段第 20 课 — 抽出统一 Agent Loop 执行器。

- 今日学习：
  - 识别当前痛点：`handle_agent_message()` 和 `continue_agent_loop_after_confirmed_tool()` 都在重复处理 planner JSON、工具名校验、参数校验、确认暂停、工具执行、trace 和 max steps。
  - 新增 `_run_agent_loop()`，作为统一的 Agent Loop 执行器。
  - `handle_agent_message()` 现在只负责以 `start_step=1`、空 observations、需要保存用户输入的方式启动 loop。
  - `continue_agent_loop_after_confirmed_tool()` 现在只负责把已确认工具的结果转换为 observation，再从下一步继续 loop。
  - 保留 `fallback_to_chat` 参数，让普通用户输入第一步 final 时仍然回到原聊天流程，而确认后的 loop 不会误触发普通聊天 fallback。
- 设计判断：
  - 这是一次“真实重复出现后的抽象”：先让普通 loop 和确认后 loop 行为都跑通，再抽公共控制流。
  - `_run_agent_loop()` 仍放在 `agent/chat.py` 内部，因为它目前还没有稳定到值得拆成独立模块。
  - `should_save_user_input` 明确区分两种入口：普通输入需要首次写入历史，确认后的继续执行不应重复保存同一条用户消息。
- 验证记录：
  - `python -m py_compile main.py app_context.py chat.py llm_client.py models.py commands/*.py memory/*.py tools/*.py agent/*.py` 通过。
  - smoke test 通过：普通工具调用后，第二步 planner 能看到 observation 并生成 final。
  - smoke test 通过：`/confirm` 后继续 loop，pending 状态清空，最终回答写回最近工具 trace。
  - smoke test 通过：普通工具后的第二步如果又遇到确认工具，会重新保存 pending 调用。
  - smoke test 通过：普通聊天 fallback 仍然不会生成 Agent trace。

#### 继续：第四阶段第 20 课 — 拆分 Agent Loop action 处理函数。

- 今日学习：
  - 识别当前痛点：`_run_agent_loop()` 已经统一了入口，但内部仍然同时承担 final 分支、tool 分支、保存用户输入和 trace 写入等细节。
  - 新增 `AgentLoopState`，集中保存一次 loop 运行中的可变状态：`user_input`、`observations`、`has_saved_user_input` 和 `fallback_to_chat`。
  - 新增 `_handle_final_action()`，专门处理 planner 返回 `action == "final"` 的分支。
  - 新增 `_handle_tool_action()`，专门处理 planner 返回 `action == "tool"` 的分支，并用返回值表示是否继续下一轮 loop。
  - 新增 `_ensure_user_input_saved()`，统一保证同一轮用户输入只写入历史一次。
  - `_run_agent_loop()` 现在更接近调度器：负责调用 planner、处理 planner 错误、分发 action、执行 max steps 兜底。
- 设计判断：
  - 这次不是为了追求文件变短，而是为了让每个函数拥有更清楚的职责边界。
  - `AgentLoopState` 目前先留在 `agent/chat.py` 内部，因为它仍然是当前实现细节，不急着进入公开数据模型。
  - `_handle_tool_action()` 返回 `bool` 是一个轻量控制信号：`True` 表示工具成功且可以继续规划，`False` 表示本轮已经结束或暂停。
- 验证记录：
  - `python -m py_compile main.py app_context.py chat.py llm_client.py models.py commands/*.py memory/*.py tools/*.py agent/*.py` 通过。
  - smoke test 通过：普通工具调用后继续 final。
  - smoke test 通过：确认工具 `/confirm` 后继续 final。
  - smoke test 通过：普通工具后的第二步遇到确认工具时仍会挂起 pending。
  - smoke test 通过：普通聊天 fallback 仍然不写 Agent trace。
  - smoke test 通过：空 final 会写入 `invalid_final_answer` trace。
  - smoke test 通过：工具 schema 参数错误会写入 `invalid_arguments` trace。
  - 验证 `echo.parameters.required == ["text"]`，`to_openai_tool()` 能导出包含 `type`、`required` 的标准 parameters dict。
  - 验证 `echo.run({"text": 123})` 返回统一错误码 `ERROR_INVALID_ARGUMENTS`。

#### 完成：第四阶段第 20 课 — 多步 Agent Loop 与工具安全边界。

- 第 20 课收尾结论：
  - 已完成多步 Agent Loop：Agent 可以在 `plan -> act -> observe -> continue/final` 之间循环，而不是只能调用一次工具。
  - 已完成 `MAX_AGENT_STEPS = 3` 安全上限，避免模型反复调用工具导致无限循环。
  - 已完成 `decide_agent_step()`，让 planner 每一步明确输出 `tool` 或 `final`。
  - 已完成 observations 机制，工具结果会进入下一轮 planner 上下文。
  - 已完成 `AgentStepTrace`，trace 记录从“工具调用记录”升级为“Agent 步骤记录”。
  - 已完成 `ToolParameters` 和 `ToolSpec.validate_arguments()`，工具参数会在统一工具边界处被校验。
  - 已完成错误码常量化，减少工具层、planner 层和 Agent 层的错误类型拼写漂移。
  - 已完成最小工具安全边界字段：`is_readonly`、`requires_confirmation`、`timeout_seconds`。
  - 已完成待确认工具流程：`pending_tool_call`、`/confirm`、`/cancel`。
  - 已完成确认后继续 Agent Loop：用户确认工具执行后，工具结果会作为 observation 回到原任务上下文。
  - 已完成轻量结构整理：`_run_agent_loop()`、`AgentLoopState`、`_handle_final_action()`、`_handle_tool_action()`、`_ensure_user_input_saved()`。
- 设计判断：
  - 第 20 课停止在“轻量内核整理”边界，不继续拆成完整 `AgentRuntime` / `AgentService`，避免在教学阶段过早架构化。
  - 当前 `agent/chat.py` 仍然偏长，但已经形成清楚职责：入口、loop 调度、final 处理、tool 处理、trace 记录。
  - `requires_confirmation` 当前只做最小确认流程；未来加入文件写入、命令执行、网络访问等危险工具时，再扩展更正式的 Policy / Permission 体系。
  - 当前仍使用教学版 JSON planner；正式 OpenAI tool calling 可以留到后续阶段接入。
- 完整验证清单：
  - 普通聊天 fallback 通过：第一步 final 且无 observation 时回到普通聊天，不写 Agent trace。
  - 普通工具调用后 final 通过：工具结果进入 observation，下一步 planner 能生成最终回答。
  - 工具参数错误通过：`echo({"text": 123})` 返回 `invalid_arguments` 并写入 trace。
  - 需要确认工具 pending 通过：`confirm_echo` 会保存 `pending_tool_call` 并提示 `/confirm` 或 `/cancel`。
  - `/confirm` 后继续 final 通过：确认后的工具结果会进入 observation，最终回答写回最近 trace。
  - `/cancel` 通过：pending 状态清空，并写入取消 trace。
  - max steps 通过：连续 3 次工具调用后触发“已达到最大 Agent 步数”兜底。
  - 全量编译通过：`python -m py_compile main.py app_context.py chat.py llm_client.py models.py commands/*.py memory/*.py tools/*.py agent/*.py`。
- 下一步计划：
  - 暂停进入新课，先复盘 Tool Use 全链路。
  - 建议按 `ToolSpec -> ToolParameters -> ToolResult/ToolError -> tools registry -> planner -> Agent Loop -> observation -> trace -> confirmation` 的顺序整理。
  - 第 21 课再进入下一阶段前的复盘或轻量架构边界整理。

#### 完成：将 Agent Kernel 架构分层与设计模式说明纳入课程 Skill。

- 本次架构输入：
  - 外部入口通过 Adapter 统一转成标准请求。
  - Application Layer 通过 `AgentService` 提供稳定门面。
  - Runtime Layer 通过 `AgentRuntime` 编排一次 Agent run。
  - LLM、Tools、Memory、Prompt、Policy、Trace 都应通过抽象接口注入 Runtime。
  - Tool 使用 Registry，Memory / Planner / Policy 使用 Strategy，LLM 使用 Provider，数据读写使用 Repository。
- 当前项目判断：
  - 现在已经有 `ToolSpec`、`ToolResult`、`ToolError`、最小 trace 和多步 Agent Loop，说明架构文档方向是对的。
  - 但项目仍处于第四阶段教学期，不适合立刻整体重构为完整分层架构。
  - 当前优先完成第 20 课，把多步 loop、安全边界、trace 命名和参数校验打扎实。
- 已更新：
  - `skill/minimal-llm-chat/SKILL.md` 新增“架构北极星”“当前重构判断”和更具体的第七阶段重构路线。
  - `skill/minimal-llm-chat/_meta.json` 从旧的最小聊天助手元信息升级为 Nexus Agent Kernel 元信息。
- 后续计划：
  - 第四阶段末尾：只做轻量边界整理，不改变 CLI 行为。
  - 第五阶段：引入 `MemoryStore` 抽象，区分短期 Session 和长期 Memory。
  - 第六阶段：RAG 框架接入时保留适配层，避免内核绑定具体框架。
  - 第七阶段：集中拆出 `AgentRequest`、`AgentResponse`、`AgentService`、`AgentRuntime`、`ToolRegistry`、`PromptBuilder`、`Policy`、`TraceLogger`、`LLMProvider`。

#### 阶段收尾总结：第四阶段 Tool Use 与 Agent Loop。

- 本阶段完成的核心跃迁：
  - 从“命令行手动工具调用”升级到“普通自然语言输入也能触发 Agent 工具决策”。
  - 从“一次性工具调用”升级到“多步 Agent Loop”，让工具结果能作为 observation 回到下一步规划。
  - 从“字符串式失败”升级到 `ToolError`、统一错误码和可复盘 trace。
  - 从“工具参数靠函数内部兜底”升级到 `ToolParameters` 和 `ToolSpec.validate_arguments()` 的统一边界。
  - 从“自动执行所有工具”升级到 `requires_confirmation`、`pending_tool_call`、`/confirm`、`/cancel` 的最小权限暂停点。
- 当前收口判断：
  - 第四阶段已经具备 Agent Kernel 的最小闭环：planner、tool registry、tool execution、observation、trace、confirmation 和 session memory 都已连通。
  - 暂时不继续做大规模架构拆分；下一步优先复盘整条 Tool Use 链路，确认概念稳定后再进入下一阶段。
  - `agent/chat.py` 仍然是后续最值得重构的文件，但现在已经有足够清楚的函数边界，可以作为未来拆出 `AgentRuntime` 的依据。
- 下次开始前建议复盘顺序：
  - `ToolSpec -> ToolParameters -> ToolResult/ToolError -> tools registry -> planner -> _run_agent_loop -> observation -> AgentStepTrace -> confirmation`。
