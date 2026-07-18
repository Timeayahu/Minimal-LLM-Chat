---
name: nexus-agent-kernel
description: >-
  阶段式教学项目：从零构建 Nexus Agent Kernel，一个教学型通用 Agent 底座。
  项目从最小 LLM 命令行聊天助手起步，逐步建立命令系统、Session、Tool Use、
  Agent Loop、Memory、RAG、运行 trace、安全边界和可扩展架构，用于扎实学习智能体工程。
metadata:
  current_stage: 5
  completed_stage: 4
  current_lesson: 22
  completed_lessons: 21
  difficulty: beginner-to-intermediate
  prerequisites:
    - Python 基础语法（变量、函数、循环、列表、字典）
    - 能在命令行运行 Python
    - 了解最基础的 Git add / commit / push 流程
  tech_stack:
    - Python 3.11+
    - OpenAI-compatible API
    - python-dotenv
    - JSON
    - Git / GitHub
  tags:
    - python
    - llm
    - agent
    - tool-use
    - memory
    - rag
    - cli
    - tutorial
---

# Nexus Agent Kernel — 课程 Skill

## 项目定位

本项目原名 `AI Learning Chat` / `Minimal LLM Chat`，现在正式定位为 **Nexus Agent Kernel**。

它不是为了立刻做成某个具体产品，而是一个教学型通用 Agent 底座。它的价值在于：学生从最小 LLM 调用开始，一步一步亲手建立对话、命令、会话、工具、记忆、RAG、Agent Loop 和工程边界。后续再基于这个最熟悉的底座，学习 Hermes-style、Claude Code-style、Codex-style 等顶级 Agent 的架构亮点。

一句话目标：

```text
做出一个小而扎实、可扩展、可研究的通用 Agent Kernel。
```

## 架构北极星

这个项目的目标不是写一个什么都会的 Agent，而是沉淀一个边界清晰、依赖可替换、能力可插拔、运行过程可观测的 Agent Kernel。

后续每次新增能力或重构，都按这个标准判断：

```text
外部入口
-> Adapter
-> AgentRequest
-> AgentService
-> AgentRuntime
-> LLM / Tools / Memory / Prompt / Policy / Trace
-> AgentResponse
-> Adapter 转成外部平台响应
```

核心边界：

1. Interface Layer 使用 Adapter Pattern。CLI、HTTP、飞书、企业微信、Webhook 等入口只负责把外部事件转成标准 `AgentRequest`，再把 `AgentResponse` 转回平台消息。Adapter 不写推理逻辑、工具逻辑、业务判断或 Prompt 拼接。
2. Application Layer 使用 Facade / Use Case 思想。对外提供稳定的 `AgentService`，负责接收标准请求、选择 Runtime 或 Agent Profile、处理应用级异常、返回标准响应。
3. Runtime Layer 使用 Orchestrator Pattern。`AgentRuntime` 只编排一次 run：加载上下文、构造 messages、调用模型、处理 tool call、执行工具、整合观察结果、输出答案、记录 trace。
4. Runtime 必须坚持 Dependency Injection。它依赖 `LLMClient`、`ToolRegistry`、`MemoryStore`、`PromptBuilder`、`Policy`、`TraceLogger` 等抽象接口，不自己读取环境变量、初始化 SDK、创建数据库连接或硬编码工具。
5. Capability Layer 使用 Strategy / Plugin / Registry 思想。工具、记忆、规划、策略、安全护栏、输出格式化等能力都可以先简单实现，但接口要保留替换空间。
6. Infrastructure Layer 使用 Provider / Repository / Adapter 思想。模型、数据库、文件系统、向量库、外部 API、日志系统等基础设施细节不能污染 Runtime。

一句话压缩原则：

```text
入口可替换，模型可替换，工具可插拔，Memory 可替换，策略可扩展，Runtime 保持稳定。
```

## 当前重构判断

现在暂不做一次性大重构。当前项目还处在第四阶段，核心学习目标是把 Tool Use、Agent Loop、ToolResult、ToolError、trace 和安全边界吃透。直接切到完整分层会增加太多抽象，容易让学习重心从“理解数据流”变成“搬目录和套接口”。

更合适的策略是渐进式重构：

1. 第四阶段末尾先做轻量边界整理，不改变用户行为。
2. 第五阶段引入 Memory 抽象时，再把 `Session` 和未来长期记忆拆成不同 `MemoryStore` 策略。
3. 第六阶段接入 RAG 框架时，用适配层保护内核，避免项目变成某个框架的 demo。
4. 第七阶段集中完成 Agent Kernel 分层重构，补齐 `AgentRequest`、`AgentResponse`、`AgentService`、`AgentRuntime`、`PromptBuilder`、`Policy`、`TraceLogger` 等稳定接口。

重构触发条件：

- 同一个流程开始被 CLI、HTTP、IM Adapter 等多个入口复用。
- `agent/chat.py` 中继续堆叠 planner、runtime、policy、trace、输出展示等多种职责。
- LLM 调用、Prompt 拼接或 Memory 访问开始散落在多个模块。
- 新增工具或能力需要频繁修改主循环。
- trace 从简单列表升级为可查询、可持久化、可复盘的运行记录。

## 当前状态

- 当前项目名：Nexus Agent Kernel
- 当前阶段：第五阶段，Memory 进阶
- 已完成课程：第 1-24 课
- 当前课程：第 24 课已完成，Agent 运行可观测性与 Trace 持久化
- 当前重点：会话快照、长期 Memory 和 Runtime Trace 已分开，下一步继续完善 Memory 召回和生命周期

## 教学节奏要求

学生当前最需要补强的是“为什么要改”的中间环节。继续课程或做任何重构前，必须先补上问题意识，而不是直接给优化后的结构。

每次改动前都要按这个顺序讲清楚：

1. 当前朴素实现是什么样。
2. 它在什么场景下会开始变难用、难维护或容易出错。
3. 如果不改，后面会遇到什么具体困难。
4. 本次改动正好解决哪一个困难。
5. 这次改动的代价是什么，为什么现在值得付出。

教学时优先使用“先遇到痛点，再引入抽象”的方式。不要只说“这样更规范”“这样更扩展”“这样状态更好”，必须说明是哪种真实复杂度逼出了这个设计。

## 终点定义

Nexus Agent Kernel v0.1 应具备：

1. 用户自然输入时，Agent 能自主判断是否需要调用工具。
2. 有统一的 `ToolSpec`、工具注册表、工具参数 schema、工具结果和工具错误。
3. 有多步 Agent Loop，支持 plan、tool call、observation、final answer 和 `max_steps`。
4. 有短期 Session 记忆、会话摘要和最小长期用户画像。
5. 有基于成熟框架集成的 RAG 能力，能导入资料、检索片段，并基于资料回答。
6. 有运行 trace，能看到每次工具调用的计划、参数、结果和最终回答。
7. 有工具安全边界，包括参数校验、只读标记、危险工具确认、错误处理。
8. 架构分层清楚，未来可以扩展不同 Agent 风格。

理想数据流：

```text
用户输入
-> Agent 判断问题类型：普通聊天 / 工具任务 / 记忆问题 / RAG 问题 / 文件或代码任务
-> Agent 根据需要调用工具、检索资料、读取记忆
-> Agent 整合观察结果
-> Agent 输出最终回答
-> 程序记录必要 trace 和记忆
```

## 八阶段路线

### 第一阶段：最小 LLM Chat（第 1-6 课，已完成）

目标：从零做出一个能运行的命令行 LLM 聊天助手。

已完成内容：

- 第 1 课：跑通最小模型调用。
- 第 2 课：加入命令行循环。
- 第 3 课：加入多轮对话历史。
- 第 4 课：保存和读取历史。
- 第 5 课：配置化模型参数。
- 第 6 课：整理 README 与 Git 提交。

学生应掌握：

- `.env -> config.py -> llm_client.py -> main.py` 的基础数据流。
- `messages` 中 system / user / assistant 的结构。
- 模型本身没有记忆，记忆来自程序每次发送完整上下文。
- 配置和代码分离，敏感信息不提交 Git。

### 第二阶段：聊天体验增强（第 7-12 课，已完成）

目标：让聊天助手更像真实 AI 应用，体验更稳定。

已完成内容：

- 第 7 课：限制对话历史长度。
- 第 8 课：增加流式输出。
- 第 9 课：增加 `/config` 命令。
- 第 10 课：增加 `/history` 命令。
- 第 11 课：支持多个聊天历史文件。
- 第 12 课：阶段复盘与 Git 标签。

学生应掌握：

- 上下文窗口和历史裁剪。
- streaming 与普通响应的区别。
- 配置可观察性。
- 多会话文件和路径管理。
- 用 Git 记录阶段成果。

### 第三阶段：工程化重构（第 13-15 课，已完成）

目标：把能跑的脚本逐步整理成可维护项目。

已完成内容：

- 第 13 课：命令系统重构。
  - 建立 `Command` 抽象。
  - 建立命令注册表。
  - 拆分 `commands/` 包。
  - 理解命令由用户直接触发。

- 第 14 课：数据建模与应用上下文。
  - 建立 `Message`、`Session`、`AppContext`。
  - 将散落状态收拢到上下文。
  - 理解字典、TypedDict、对象建模的取舍。

- 第 15 课：Session 行为归属与包化重构。
  - 将 `memory.py` 升级为 `memory/` 包。
  - 将 `Session` 升级为 dataclass。
  - 将 reset、count、history、save、trim 等行为迁入 `Session`。
  - 理解 class 定义阶段、`__init__`、`field(default_factory=...)` 的区别。

学生应掌握：

- `Command` 做成 class 是为了统一接口和多态。
- `Session` 做成 class 是因为状态和行为开始聚集。
- `AppContext` 是运行时上下文，不是业务模型本身。
- 工程化不是盲目拆文件，而是让职责边界更清楚。

### 第四阶段：Tool Use 与 Agent Loop（第 16-21 课，已完成）

目标：让 Agent 从“只会聊天”变成“能判断并调用工具”。

#### 第 16 课：最小 Tool Use 入门（已完成）

本课真实内容：

- 新建 `tools/` 包。
- 写出 `time`、`echo` 两个本地工具。
- 建立工具注册表，并放入 `AppContext`。
- 新增 `/tool` 命令，用于手动查看和调用工具。
- 新增 `/ask-tool` 命令，用教学版 JSON 工具计划器演示最小 Agent Loop。
- 将工具从裸 `Callable[[list[str]], str]` 升级为 `ToolSpec`。
- 讲清楚 `Callable`、`__call__`、`__init__`、函数工具和对象工具的区别。
- 初步阅读 OpenAI-compatible Tool Calling 文档。
- 理解工具 JSON Schema 中的 `parameters`、`type: object`、`properties`、字段级 `type`、`required`、`additionalProperties`、`strict`。

第 16 课关键结论：

```text
模型不真正执行工具。
模型只提出工具调用请求。
Python 程序负责执行工具、处理错误、记录结果、守住权限边界。
```

当前教学版 JSON 工具计划器的问题：

- 模型可能不返回合法 JSON。
- 参数是 `list[str]`，语义弱，不知道每个参数叫什么。
- 没有 JSON Schema 约束，模型容易乱传字段或参数值。
- 没有标准 `tool_calls`、`tool_call_id`、`function.arguments` 协议。
- 工具失败和工具成功都只是字符串，错误处理不结构化。

OpenAI-compatible 正式 Tool Calling 的思路：

```text
Python 把 tools 定义发给模型
-> 模型返回标准 tool_calls
-> Python 根据 tool_calls 执行本地工具
-> Python 把工具结果作为 tool message 发回模型
-> 模型基于工具结果生成最终回答
```

当前 `ToolSpec` 后续还缺：

- `parameters`: OpenAI-compatible JSON Schema。
- `strict`: 是否要求模型严格遵守 schema。
- `ToolResult`: 工具成功结果。
- `ToolError`: 工具失败结果。
- `is_readonly`: 工具是否只读。
- `requires_confirmation`: 是否需要用户确认。
- `timeout_seconds`: 工具超时限制。
- `to_openai_tool()`: 转换为 OpenAI-compatible tool JSON。

为什么 `/ask-tool` 只是临时训练命令：

- 它把 Agent 内部工具决策流程显式暴露出来，适合学习。
- 真实 Agent 不应要求用户输入特殊命令。
- 最终普通聊天入口应自动判断是否调用工具。
- `/tool` 可以保留为调试命令，`/ask-tool` 最终应被 `agent_chat()` 吸收。

#### 第 17 课：将 Tool Use 融入普通聊天（已完成）

目标：用户自然输入时，Agent 自主判断是否调用工具。

计划：

- 新建 `agent/` 包或 `agent_chat()` 入口。
- 将教学版工具调用流程迁移到普通聊天路径。
- 普通输入先进入 Agent 层，而不是直接进入 `stream_llm()`。
- Agent 判断：不需要工具则普通回答，需要工具则执行工具再回答。
- 暂时保留 `/tool` 作为工具调试命令。
- 移除教学调试命令，用户只需要自然语言输入。

#### 第 18 课：ToolSpec 标准化

目标：让本地工具定义开始靠近 OpenAI-compatible tool schema。

计划：

- 将工具参数从 `list[str]` 逐步升级为 `dict[str, Any]`。
- 为 `ToolSpec` 增加 `parameters` 和 `strict`。
- 增加 `to_openai_tool()`。
- 用当前 `time`、`echo` 工具练习 JSON Schema。
- 继续保持教学版流程，不一次性替换全部模型调用。

#### 第 19 课：ToolResult、ToolError 与运行 trace

目标：让工具执行结果结构化、可判断、可记录。

计划：

- 工具返回值从裸字符串升级为 `ToolResult`。
- 区分成功、参数错误、执行异常、未知工具。
- 增加 `ToolError`。
- 记录每次工具调用的 plan、arguments、result、error、final answer。
- 这些记录叫运行 trace，不是旧课程里那种泛泛的日志系统。

#### 第 20 课：多步 Agent Loop 与工具安全边界

目标：从单步工具调用升级为可控的多步 Agent Loop。

计划：

- 引入 `max_steps`，避免无限循环。
- 支持 plan -> act -> observe -> continue / final。
- 增加只读工具和危险工具的区别。
- 对写文件、执行命令等危险工具增加用户确认。
- 为未来 Claude Code-style / Codex-style 能力做准备。

#### 第 21 课：Tool Use 全链路复盘与轻量架构边界整理

目标：在进入 Memory 进阶前，把第 16-20 课形成的 Tool Use 链路复盘清楚。

计划：

- 复盘 `user input -> planner -> tool -> observation -> trace -> final answer` 的完整数据流。
- 明确 `ToolSpec`、`ToolParameters`、`ToolResult`、`ToolError`、`AgentStepTrace` 和 `PendingToolCall` 的职责。
- 新增轻量文档 `docs/TOOL_USE_FLOW.md`，作为后续重构前的地图。
- 暂时不大拆 `AgentRuntime` / `Policy` / `TraceLogger`，等 Memory、RAG、危险工具等复杂度继续出现后再拆。
- 为第五阶段 Memory 进阶做准备：接下来要区分“当前会话上下文”和“长期可沉淀记忆”。

### 第五阶段：Memory 进阶

目标：让 Agent 不只是记住当前窗口，而是能沉淀长期信息。

计划方向：

- 区分短期 Session 记忆和长期 Memory。
- 引入会话摘要，降低上下文长度压力。
- 建立最小用户画像，记录稳定偏好和学习状态。
- 建立重要事件记忆。
- 训练 Agent 判断什么值得记住，什么只是当前上下文。

#### 第 22 课：区分短期 Session 与长期 Memory（已完成）

目标：先把当前会话上下文和跨会话长期记忆分成两个明确概念。

计划：

- 新增 `MemoryStore`，用本地 JSON 保存长期记忆。
- 在 `AppContext` 中同时放 `session` 和 `memory_store`。
- 新增 `/remember`，手动保存一条长期记忆。
- 新增 `/memories`，查看最近长期记忆。
- 普通聊天和 Agent planner 在调用模型前临时注入长期记忆，不污染 `Session.messages`。

#### 第 23 课：长期记忆的类型与生命周期管理（已完成）

- 支持 `fact`、`preference`、`learning` 三类记忆。
- 支持按 ID 创建、列出、查看和删除。
- 删除后不复用旧 ID。

#### 第 24 课：Agent 运行可观测性与 Trace 持久化（已完成）

- 区分 Conversation、Runtime Trace、Operational Log 和 Metrics。
- 新增独立 JSONL TraceStore，运行事件不再等待 Session 保存。
- 通过 `session_id` / `run_id` / `event_id` 还原一次 Agent Loop。
- 记录 planner、tool、confirmation、final 和终态事件及耗时。
- 新增最小敏感字段脱敏与自动化测试。

### 第六阶段：RAG 框架技术评审与集成实战

目标：不再从零手写最小 RAG，而是基于成熟 AI Agent / RAG 框架做技术评审、选型和实战集成。

计划方向：

- 先做 RAG / Agent 框架技术评审，比较候选框架的定位、抽象层级、生态成熟度、学习成本和可控性。
- 候选方向包括但不限于 LlamaIndex、LangChain / LangGraph、Haystack、AutoGen 相关方案等；正式选型时必须基于当时最新文档和项目状态重新确认。
- 最终选出一个主框架作为第六阶段实战对象。
- 使用该框架完成资料导入、切分、索引、检索、引用来源和基于资料回答。
- 重点学习框架里的 RAG 数据流，而不是重复实现基础检索逻辑。
- 分析框架抽象如何映射到当前项目里的 `nexus/agent/`、`nexus/tools/`、`nexus/context/` 和未来 `nexus/knowledge/` 边界。
- 保留一个轻量适配层，避免业务代码被某个框架完全锁死。
- 区分 Memory 和 RAG：Memory 记录用户与经历，RAG 检索外部知识。

学习重点：

- 如何做框架技术评审：评估功能、文档、维护活跃度、扩展点、调试体验、部署复杂度和迁移风险。
- 如何阅读成熟框架的 RAG 抽象：Document、Node / Chunk、Embedding、Vector Store、Retriever、Reranker、Response Synthesizer。
- 如何判断“用框架”与“自己写适配层”的边界。
- 如何把外部框架接进自己的 Agent Kernel，而不是把项目完全改造成框架 demo。

### 第七阶段：Agent Kernel 重构

目标：把项目整理成真正可扩展的 Agent Kernel。这个阶段不是为了“看起来更工程化”，而是因为前面已经有了工具、Memory、RAG、trace、安全策略和多个入口的真实复杂度，需要把稳定内核和可替换能力分开。

重构原则：

- 先定义标准请求和响应：`AgentRequest`、`AgentResponse`。
- 再建立对外门面：`AgentService`。
- 再拆出核心编排器：`AgentRuntime`。
- 再把能力组件通过依赖注入接入 Runtime。
- 每一步都保持 CLI 当前行为可运行，避免一次性改坏主路径。

演进目标（在现有 `nexus/` 包内按真实复杂度逐步增加，而不是再次平铺根目录）：

```text
Nexus Agent Kernel/
├── main.py                    # 稳定启动入口
└── nexus/
    ├── app.py                 # 依赖组装
    ├── cli/                   # 当前 CLI；未来可增加 HTTP / IM adapter
    ├── agent/
    │   ├── contracts.py       # 未来 AgentRequest / AgentResponse
    │   ├── runtime.py         # 当前 AgentRuntime / Orchestrator
    │   ├── planner.py
    │   ├── prompt_builder.py
    │   ├── policy.py
    │   └── observability.py
    ├── tools/                 # ToolSpec、ToolRegistry 与具体工具
    ├── context/               # Session、Memory 与存储实现
    ├── knowledge/             # 未来 RAG 框架适配层
    └── llm/                   # 可注入的 LLM Provider
```

推荐拆分顺序：

1. 在 `nexus/agent/contracts.py` 增加 `AgentRequest` / `AgentResponse`，先统一类型和数据流，不改行为。
2. 让 `nexus/cli/main.py` 的普通输入分支通过 `AgentService` 调用。
3. 已从 `nexus/agent/loop.py` 拆出 `AgentRuntime`，保留当前多步 loop 和函数式兼容入口。
4. 把 `nexus/tools/` 的 `dict[str, ToolSpec]` 升级为 `ToolRegistry`。
5. 把 `nexus/llm/client.py` 从模块级函数升级为可注入 `LLMClient` / `LLMProvider`。
6. 把 Prompt 组装从 planner 和 chat 里拆到 `PromptBuilder`。
7. 已建立最小工具请求 Policy；等危险工具类型增加后，再补允许、拒绝、降级等完整权限策略。
8. 将当前 JSONL `TraceLogger` 保持为独立依赖，需要复杂查询时再增加 SQLite 或外部观测实现。
9. 增加 HTTP / IM Adapter 时，只接入 `AgentService`，不修改 Runtime。

### 第八阶段：顶级 Agent 亮点实验

目标：基于主干 Kernel 学习顶级 Agent 的关键架构能力。

方向：

- Hermes-style：长期记忆、用户画像、人格一致性、陪伴感、主动上下文召回。
- Claude Code-style：代码库理解、文件搜索、补丁编辑、运行测试、任务计划、交互式确认。
- Codex-style：工程化执行、沙箱权限、持续验证、变更边界、并行子任务、最终交付总结。

原则：

- 不要太早 fork 很多份。
- 先把主干 Kernel 做扎实。
- 等核心接口稳定后，再通过分支或变体实验不同 Agent 风格。

## 当前项目结构

```text
Nexus Agent Kernel/
├── main.py                    # 极薄启动入口
├── nexus/
│   ├── app.py                # AppContext 与依赖组装
│   ├── settings.py           # 配置
│   ├── cli/                  # CLI 主循环和命令
│   ├── agent/                # Planner、Loop 与观测
│   ├── context/              # Session 与 Memory
│   ├── tools/                # 工具模型、实现和注册表
│   └── llm/                  # Prompt 与模型调用
├── tests/
├── docs/
├── requirements.txt
└── skill/minimal-llm-chat/
```

## 教学原则

参考 `AI_TUTOR_RULES.md`，实际教学时遵守：

1. 先解释为什么做这一步。
2. 提前说明修改范围。
3. 每次尽量小步修改，优先 1-3 个文件。
4. 关键代码必须解释输入、输出和数据流。
5. 不跳过基础概念。
6. 报错先教怎么看，再给修复方案。
7. 每课结束要更新 `PROGRESS.md`。
8. 关键认知突破或课程收尾时更新 `LEARNER_PROFILE.md`。

## 训练方式

从第二阶段之后，课程不再默认由老师直接给完整答案，而是更接近真实开发训练：

1. 老师先讲清需求、数据流和关键限制。
2. 老师给实现线索，不急着贴完整答案。
3. 学生先说思路或尝试实现。
4. 老师根据学生反馈逐步提示。
5. 必要时老师再给出正确写法。
6. 每次新抽象都要解释它解决了什么变化点，是否有过度工程化风险。

## Debug 训练规则

优先使用日常开发中最常见的方法：

- `print()` 查看变量值和数据结构。
- `len()` 检查列表长度。
- `type()` 检查变量类型。
- `python -m py_compile ...` 做语法检查。
- 根据 traceback 找到报错文件、行号、错误类型。
- 在 Cursor / VS Code 中使用断点、单步执行、变量面板。

## Git 训练规则

每课结束前至少做一次：

```bash
git status --short
git diff
```

课程功能完成后，学生自己完成提交：

```bash
git add <本课相关文件>
git commit -m "简短说明本课完成了什么"
git push
```

老师负责解释 Git 输出，不替学生盲目提交。

## 学习画像记录规则

维护 `LEARNER_PROFILE.md` 作为学生长期学习档案。它不是功能日志，而是老师视角的阶段性评估。

需要更新的情况：

1. 完成一课或一个清晰课程节点。
2. 学生围绕某个概念连续追问并出现明显认知突破。
3. 阶段结束、复盘或用户明确要求总结评估。

记录重点：

- 当前处于软件开发、AI 应用开发、Agent 工程化学习的哪个位置。
- 已掌握的知识和掌握程度。
- 学生主动提出的问题、反馈和思考特点。
- 当前短板、容易混淆的概念、下一步训练建议。
- 老师评语要保留具体观察和判断。

## 概念速查表

| 概念 | 当前理解 | 所属阶段 |
|---|---|---|
| `messages` | 模型输入的对话历史，由 system/user/assistant 消息组成 | 第一阶段 |
| Session | 当前会话状态和相关行为的聚合 | 第三阶段 |
| AppContext | 程序运行时上下文，连接 session、commands、tools | 第三阶段 |
| Command | 用户直接触发的程序命令 | 第三阶段 |
| Tool | 模型可选择、程序负责执行的能力 | 第四阶段 |
| ToolSpec | 工具定义，包含名称、描述、执行函数，后续扩展 schema 和权限 | 第四阶段 |
| Tool Calling | 模型提出工具调用，程序执行工具，再把结果交回模型 | 第四阶段 |
| JSON Schema | 描述工具参数结构的标准格式 | 第四阶段 |
| ToolResult | 工具成功执行后的结构化结果 | 第四阶段后续 |
| ToolError | 工具失败后的结构化错误 | 第四阶段后续 |
| Agent Loop | plan -> act -> observe -> final 的循环 | 第四阶段后续 |
| Memory | Agent 对用户、会话、重要事件的可召回记录 | 第五阶段 |
| RAG | 基于外部资料检索片段并回答 | 第六阶段 |
| Adapter | 把 CLI、HTTP、IM 等外部协议转成统一 AgentRequest / AgentResponse | 第七阶段 |
| AgentService | 对外稳定门面，隐藏 Runtime 内部依赖 | 第七阶段 |
| AgentRuntime | 只负责编排一次 Agent run 的核心运行时 | 第七阶段 |
| Dependency Injection | Runtime 依赖抽象组件，由外部注入具体实现 | 第七阶段 |
| ToolRegistry | 注册、发现和调用工具的统一入口 | 第七阶段 |
| PromptBuilder | 集中构造 system/user/tool 等 messages，避免 Prompt 拼接散落 | 第七阶段 |
| Policy | 判断工具调用是否允许、是否确认、是否拒绝或降级 | 第七阶段 |
| LLMProvider | 屏蔽 OpenAI-compatible、Claude、本地模型等模型服务差异 | 第七阶段 |
| Repository | 屏蔽会话、记忆、trace 等底层存储差异 | 第七阶段 |
| TraceLogger | 记录一次 Agent run 的模型调用、工具调用、错误、耗时和输出 | 第七阶段 |
