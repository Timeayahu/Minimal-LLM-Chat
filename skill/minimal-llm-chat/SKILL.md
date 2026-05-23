---
name: nexus-agent-kernel
description: >-
  阶段式教学项目：从零构建 Nexus Agent Kernel，一个教学型通用 Agent 底座。
  项目从最小 LLM 命令行聊天助手起步，逐步建立命令系统、Session、Tool Use、
  Agent Loop、Memory、RAG、运行 trace、安全边界和可扩展架构，用于扎实学习智能体工程。
metadata:
  current_stage: 4
  completed_stage: 3
  current_lesson: 20
  completed_lessons: 19
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

## 当前状态

- 当前项目名：Nexus Agent Kernel
- 当前阶段：第四阶段，Tool Use 与 Agent Loop
- 已完成课程：第 1-19 课
- 下一课：第 20 课，多步 Agent Loop 与工具安全边界
- 当前重点：从单步工具调用升级为可控的多步 Agent Loop

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

### 第四阶段：Tool Use 与 Agent Loop（当前阶段，第 16-20 课）

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

### 第五阶段：Memory 进阶

目标：让 Agent 不只是记住当前窗口，而是能沉淀长期信息。

计划方向：

- 区分短期 Session 记忆和长期 Memory。
- 引入会话摘要，降低上下文长度压力。
- 建立最小用户画像，记录稳定偏好和学习状态。
- 建立重要事件记忆。
- 训练 Agent 判断什么值得记住，什么只是当前上下文。

### 第六阶段：RAG 框架技术评审与集成实战

目标：不再从零手写最小 RAG，而是基于成熟 AI Agent / RAG 框架做技术评审、选型和实战集成。

计划方向：

- 先做 RAG / Agent 框架技术评审，比较候选框架的定位、抽象层级、生态成熟度、学习成本和可控性。
- 候选方向包括但不限于 LlamaIndex、LangChain / LangGraph、Haystack、AutoGen 相关方案等；正式选型时必须基于当时最新文档和项目状态重新确认。
- 最终选出一个主框架作为第六阶段实战对象。
- 使用该框架完成资料导入、切分、索引、检索、引用来源和基于资料回答。
- 重点学习框架里的 RAG 数据流，而不是重复实现基础检索逻辑。
- 分析框架抽象如何映射到当前项目里的 `agent/`、`tools/`、`memory/` 和未来 `rag/` 边界。
- 保留一个轻量适配层，避免业务代码被某个框架完全锁死。
- 区分 Memory 和 RAG：Memory 记录用户与经历，RAG 检索外部知识。

学习重点：

- 如何做框架技术评审：评估功能、文档、维护活跃度、扩展点、调试体验、部署复杂度和迁移风险。
- 如何阅读成熟框架的 RAG 抽象：Document、Node / Chunk、Embedding、Vector Store、Retriever、Reranker、Response Synthesizer。
- 如何判断“用框架”与“自己写适配层”的边界。
- 如何把外部框架接进自己的 Agent Kernel，而不是把项目完全改造成框架 demo。

### 第七阶段：Agent Kernel 重构

目标：把项目整理成真正可扩展的 Agent Kernel。

目标结构：

```text
Nexus Agent Kernel/
├── agent/       # Agent Loop、planner、runtime、trace
├── tools/       # ToolSpec、registry、schemas、results、权限边界
├── memory/      # session、summary、profile、storage
├── rag/         # loader、chunker、retriever、index
├── commands/    # 用户直接控制程序的命令
├── llm_client.py
├── app_context.py
└── main.py
```

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
├── main.py
├── app_context.py
├── config.py
├── llm_client.py
├── chat.py
├── commands/
├── tools/
├── memory/
├── models.py
├── prompts.py
├── requirements.txt
├── PROGRESS.md
├── README.md
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
