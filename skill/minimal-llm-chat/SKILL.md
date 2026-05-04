---
name: minimal-llm-chat
description: >-
  阶段式教学项目：从零构建并持续增强一个最小 LLM 命令行聊天助手。
  第一阶段完成基础可用版本；第二阶段增强聊天体验；后续阶段继续练习
  代码结构、Tool Use、最小 RAG 等 AI 应用开发核心能力。
metadata:
  current_stage: 2
  completed_stage: 1
  difficulty: beginner
  prerequisites:
    - Python 基础语法（变量、函数、循环）
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
    - cli
    - tutorial
    - ai-app
---

# Minimal LLM Chat — 阶段式课程 Skill

## 项目概览

这个项目不是一次性写完的脚本，而是一条持续演进的学习路线：

1. 第一阶段：从零做出一个能用的 LLM 命令行聊天助手。
2. 第二阶段：增强聊天体验，让它更接近真实 AI 应用。
3. 第三阶段：整理代码结构，让项目更容易维护。
4. 第四阶段：加入最小 Tool Use，让助手能调用工具。
5. 第五阶段：加入最小 RAG，让助手能基于本地资料回答。

每一课坚持小步前进：最多改 1-2 个文件，先讲为什么，再写代码，最后解释数据流和留下练习。

## 当前项目文件结构

```text
ai-learning-chat/
├── main.py          # 程序入口，命令行循环和命令解析
├── config.py        # 读取 API Key、模型名、base_url、生成参数
├── llm_client.py    # 封装模型调用
├── memory.py        # 保存和读取对话历史
├── requirements.txt # Python 依赖
├── .env.example     # 配置模板
├── .env             # API Key，不提交 Git
├── .gitignore       # 忽略敏感文件和缓存
├── logs/            # 对话历史 JSON 文件
└── README.md        # 项目说明
```

## 教学原则

参考 `AI_TUTOR_RULES.md`：

1. 先解释为什么做这一步。
2. 提前说明修改范围。
3. 每次最多改 1-2 个文件。
4. 关键代码必须解释输入、输出和数据流。
5. 每次留一个 5-15 分钟的小练习。
6. 报错先教怎么看，再给修复方案。
7. 不跳过基础概念。

## 第二阶段开始的训练方式

从第二阶段开始，课程不再默认由老师直接实现完整功能，而是切换成更接近真实开发的训练方式：

1. 老师先讲清楚需求、数据流和关键限制。
2. 老师给出 2-4 条实现线索，但不直接贴完整答案。
3. 学生先自己尝试实现，可以先说思路，也可以直接改代码。
4. 老师根据学生反馈逐步提示，必要时再给出正确写法。
5. 每课加入一个 Debug 小练习，练习读报错、打断点、打印变量、缩小问题范围。
6. 每课加入一个 Git 小练习，练习 `status`、`diff`、`add`、`commit`、`push` 等日常流程。
7. 老师可以故意留下很小的 bug 作为练习，但必须控制风险，不能破坏 API Key、Git 历史或重要文件。

### Debug 训练规则

Debug 练习优先使用日常开发里最常见的方法：

- `print()` 查看变量值和数据结构。
- `len()` 检查列表长度。
- `type()` 检查变量类型。
- `python -m py_compile ...` 做语法检查。
- 根据 traceback 找到报错文件、行号、错误类型。
- 在 Cursor / VS Code 里使用断点、单步执行、变量面板。

### Git 训练规则

每课结束前，至少做一次 Git 状态检查：

```bash
git status --short
git diff
```

当一课功能完成后，学生自己完成提交：

```bash
git add <本课相关文件>
git commit -m "简短说明本课完成了什么"
git push
```

老师负责解释 Git 输出，而不是替学生盲目提交。遇到冲突、未跟踪文件、tracking 问题时，优先教学生读懂信息。

---

## 第一阶段：从 0 到可用的最小 LLM Chat（已完成）

### 阶段目标

从空项目开始，完成一个可以在命令行里连续聊天、保存历史、读取配置、并提交到 GitHub 的最小 AI 应用。

### 第 1 课：跑通最小模型调用

**目标**：Python 调用一次大模型 API，打印回答。

**涉及文件**：
- `config.py`
- `llm_client.py`
- `main.py`
- `.env.example`

**我做了什么**：
- 创建配置读取模块。
- 创建 LLM 调用函数。
- 写一个最小 `main.py`，发送一次固定问题。

**你做了什么**：
- 创建并保存 `.env`。
- 填入真实 API Key、base_url、model。
- 学会用报错定位 `.env` 没保存或没读到的问题。

**你学到什么**：
- API Key 是鉴权凭证。
- `base_url` 是 API 服务地址。
- `messages` 是模型输入的核心结构。
- `.env` 用来把敏感配置和代码分离。

**数据流**：

```text
.env -> config.py -> llm_client.py -> API -> main.py 打印回答
```

---

### 第 2 课：加入命令行循环

**目标**：用户可以连续输入问题，模型连续回答。

**涉及文件**：
- `main.py`
- `llm_client.py`

**我做了什么**：
- 在 `main.py` 中加入 `while True`。
- 加入 `/exit` 命令。
- 清理 `llm_client.py` 中影响聊天体验的调试输出。

**你做了什么**：
- 增加 `/help` 命令。
- 学会用三引号字符串打印多行帮助文本。

**你学到什么**：
- `while True` 表示持续循环。
- `input()` 从终端读取用户输入。
- `if / elif / continue / break` 可以完成基础命令解析。

**数据流**：

```text
input() -> 判断命令 -> 普通问题调用 API -> 打印回答 -> 回到 input()
```

---

### 第 3 课：加入多轮对话历史

**目标**：模型能记住前面说过的话。

**涉及文件**：
- `main.py`

**我做了什么**：
- 把 `messages` 从循环内移动到循环外。
- 每轮追加 user 消息和 assistant 消息。

**你做了什么**：
- 增加 `/reset` 命令。
- 用 `del messages[1:]` 清空历史但保留 system prompt。

**你学到什么**：
- API 每次调用本身没有记忆。
- “记忆”来自我们每次都把完整 `messages` 发给模型。
- 对话历史过长会增加成本，也可能超过上下文窗口。

**数据流**：

```text
messages=[system] -> append user -> 调 API -> append assistant -> messages 变长
```

---

### 第 4 课：保存和读取历史

**目标**：程序退出后，下次启动还能读取历史。

**涉及文件**：
- `memory.py`
- `main.py`

**我做了什么**：
- 创建 `save_history()` 和 `load_history()`。
- 启动时读取 `logs/history.json`。
- 退出时自动保存。
- 增加 `/save` 命令。

**你做了什么**：
- 理解 `Path("logs/history.json").parent.mkdir(...)`。
- 学会区分“创建文件夹”和“创建文件”。

**你学到什么**：
- JSON 可以保存 Python 列表和字典。
- `with open(...)` 会自动关闭文件。
- `ensure_ascii=False` 可以让中文正常写入。
- `parents=True` 创建多层父目录。
- `exist_ok=True` 表示目录已存在时不报错。

**数据流**：

```text
启动 -> load_history() -> 恢复 messages
退出或 /save -> save_history(messages) -> 写入 logs/history.json
```

---

### 第 5 课：配置化模型参数

**目标**：模型名、API 地址、温度参数、最大输出长度都从配置读取。

**涉及文件**：
- `config.py`
- `llm_client.py`
- `.env.example`
- `main.py`

**我做了什么**：
- 在 `config.py` 中加入 `TEMPERATURE` 和 `MAX_TOKENS`。
- 在 `llm_client.py` 调用 API 时传入这些参数。

**你做了什么**：
- 增加 `/model` 命令。
- 更新 `.env.example`。

**你学到什么**：
- 配置和代码分离。
- `.env` 读出来的值都是字符串，需要 `float()` / `int()` 转换。
- `temperature` 控制回答稳定性和发散程度。
- `max_tokens` 控制模型最长回答。

**数据流**：

```text
.env -> config.py 类型转换 -> llm_client.py 调用参数 -> API
```

---

### 第 6 课：整理 README + GitHub 提交

**目标**：把项目整理成别人也能运行的学习作品。

**涉及文件**：
- `README.md`
- `.env.example`
- Git / GitHub

**我做了什么**：
- 新增 README。
- 初始化 Git。
- 完成第一次本地提交。
- 解释 remote、tracking、`push -u` 的关系。

**你做了什么**：
- 完成学习总结。
- 删除错误创建的 GitHub repo。
- 新建空 GitHub repo。
- 成功把本地项目推送到 GitHub。

**你学到什么**：
- 本地已有代码时，GitHub 应创建空 repo。
- `git remote add` 只是告诉本地远程地址。
- `git push -u` 会建立本地分支和远程分支的追踪关系。
- `.env` 和 `logs/` 不应该提交。

**标准流程**：

```text
git init -> git add -> git commit -> GitHub 空 repo -> git remote add origin -> git push -u origin main
```

---

## 第二阶段：增强聊天体验（当前阶段）

### 阶段目标

让这个命令行聊天助手更好用、更稳定，并开始接近真实 AI 应用的体验。第二阶段重点不是“大改架构”，而是在现有代码上练习小功能迭代。

### 第二阶段课程总览

| 课时 | 主题 | 主要文件 | 你会学到 |
|---|---|---|---|
| 第 7 课 | 限制对话历史长度 | `main.py` | 列表切片、上下文窗口、成本控制 |
| 第 8 课 | 增加流式输出 | `llm_client.py`, `main.py` | generator、流式响应、终端刷新 |
| 第 9 课 | 增加 `/config` 命令 | `config.py`, `main.py` | 配置展示、敏感信息隐藏、函数返回字典 |
| 第 10 课 | 增加 `/history` 命令 | `main.py` 或 `memory.py` | 遍历列表、格式化输出、角色区分 |
| 第 11 课 | 支持多个聊天历史文件 | `memory.py`, `main.py` | 文件命名、会话概念、路径管理 |
| 第 12 课 | 阶段复盘与 Git 标签 | `README.md`, Git | 写变更记录、打 tag、复盘学习成果 |

---

### 第 7 课：限制对话历史长度

**目标**：最多保留最近 10 轮对话，避免 `messages` 无限变长。

**涉及文件**：
- `main.py`

**我会做什么**：
- 解释为什么上下文不能无限增长。
- 带你观察 `messages` 的结构：第 0 条是 system，后面每轮两条。
- 先给你实现线索，不直接写完整答案。
- 根据你的思路或代码反馈，逐步提示并帮你修正。

**你要做什么**：
- 先自己设计裁剪逻辑：什么时候裁剪、保留哪几条消息。
- 自己尝试写一个 `trim_messages()` 或等价逻辑。
- 尝试打印 `len(messages)`，观察列表长度变化。
- 修改最大保留轮数，比如从 10 轮改成 3 轮，用更短的数字方便测试。

**这一课核心学到什么**：
- `messages` 的长度和轮数不是一回事。
- 一轮对话通常包含 2 条消息：user + assistant。
- Python 列表切片可以保留列表的一部分。
- AI 应用需要主动管理上下文成本。

**预期数据流**：

```text
append user -> 调 API -> append assistant -> 如果历史太长 -> 裁剪早期消息
```

**课后练习**：
- 增加 `/count` 命令，显示当前 `messages` 里有多少条消息。

**Debug 练习**：
- 故意把最大保留轮数设成 1 或 2，连续问 4 轮，观察 `len(messages)` 是否符合预期。
- 如果模型忘记得太快，先打印完整 `messages`，判断是不是裁剪过头。

**Git 练习**：
- 功能完成后先运行 `git diff main.py`，用自己的话说出这次改了哪里。
- 提交信息建议：`Limit chat history length`。

---

### 第 8 课：增加流式输出

**目标**：让 AI 回答边生成边显示，而不是等完整回答结束后一次性打印。

**涉及文件**：
- `llm_client.py`
- `main.py`

**我会做什么**：
- 解释普通响应和 stream 响应的区别。
- 把 `ask_llm()` 拆出一个 `stream_llm()`。
- 在终端逐块打印模型返回的内容。

**你要做什么**：
- 观察流式输出时终端显示方式的变化。
- 给流式输出补上换行，让下一次 `You:` 不贴在回答后面。
- 尝试保留完整 answer，并 append 到 `messages`。

**这一课核心学到什么**：
- generator 是“边产生边使用”的函数。
- 流式响应会返回很多小片段。
- 即使边打印，也要把完整回答存进历史。

**预期数据流**：

```text
messages -> stream API -> chunk 文本逐块打印 -> 拼成 answer -> append assistant
```

**课后练习**：
- 增加配置项 `OPENAI_STREAM=true/false`，控制是否使用流式输出。

**Debug 练习**：
- 老师可能故意留下“回答能显示但没有保存进历史”的小 bug。
- 你需要用第二轮追问测试：如果模型记不住上一轮，就检查 assistant 消息有没有 append。

**Git 练习**：
- 用 `git diff llm_client.py main.py` 检查流式输出改动。
- 提交信息建议：`Add streaming chat output`。

---

### 第 9 课：增加 `/config` 命令

**目标**：在程序里查看当前模型配置，但不能泄露 API Key。

**涉及文件**：
- `config.py`
- `main.py`

**我会做什么**：
- 在 `config.py` 中增加一个 `get_config_summary()` 函数。
- 在 `main.py` 中增加 `/config` 命令。
- 隐藏 API Key，只展示前几位。

**你要做什么**：
- 把 `/model` 合并进 `/config`。
- 修改 `.env` 中的 temperature，重新运行观察变化。
- 判断哪些配置可以显示，哪些不应该完整显示。

**这一课核心学到什么**：
- 函数可以返回字典作为结构化信息。
- 配置信息展示时要注意安全。
- 代码里可以给用户做“可观察性”：让当前状态看得见。

**预期数据流**：

```text
.env -> config.py -> get_config_summary() -> /config 打印
```

**课后练习**：
- 在 `/help` 中加入 `/config` 的说明。

**Debug 练习**：
- 故意把 `.env` 中的 `OPENAI_TEMPERATURE` 写成非数字，比如 `abc`，观察 `ValueError`。
- 学会从 traceback 找到 `float(...)` 出错的位置。

**Git 练习**：
- 检查 `.env` 是否没有出现在 `git status` 中。
- 提交信息建议：`Add config command`。

---

### 第 10 课：增加 `/history` 命令

**目标**：在命令行里查看最近几轮对话。

**涉及文件**：
- `main.py`
- 可选：`memory.py`

**我会做什么**：
- 解释如何遍历 `messages`。
- 过滤掉 system，只展示 user 和 assistant。
- 格式化最近 N 条消息。

**你要做什么**：
- 把展示数量从最近 6 条改成最近 10 条。
- 给不同角色加前缀，比如 `You:` 和 `AI:`。
- 观察 `/reset` 后 `/history` 的变化。

**这一课核心学到什么**：
- 列表遍历。
- 根据字典字段判断角色。
- 面向用户的输出需要格式化。

**预期数据流**：

```text
/history -> 读取 messages -> 过滤 system -> 格式化打印最近消息
```

**课后练习**：
- 增加 `/history all`，显示全部历史。

**Debug 练习**：
- 故意在没有任何对话时运行 `/history`，观察是否能友好提示“暂无历史”。
- 如果报错，检查列表为空时切片和循环会发生什么。

**Git 练习**：
- 用 `git diff` 检查是否只改了本课相关文件。
- 提交信息建议：`Add history command`。

---

### 第 11 课：支持多个聊天历史文件

**目标**：不再只有一个 `logs/history.json`，而是可以新建不同会话。

**涉及文件**：
- `memory.py`
- `main.py`

**我会做什么**：
- 解释“会话 session”的概念。
- 让 `save_history()` 和 `load_history()` 支持文件名参数。
- 增加 `/new` 命令，新建一个新的聊天历史。

**你要做什么**：
- 给新会话起自己的名字。
- 查看 `logs/` 下面是否生成多个 JSON 文件。
- 思考历史文件命名里哪些字符不适合作为文件名。

**这一课核心学到什么**：
- 函数参数让代码更灵活。
- 路径拼接要谨慎。
- 从单文件存储走向多会话管理。

**预期数据流**：

```text
/new -> 设置当前 session 名 -> messages 重置 -> 保存到 logs/<session>.json
```

**课后练习**：
- 增加 `/sessions` 命令，列出已有历史文件。

**Debug 练习**：
- 故意输入带空格或特殊字符的 session 名，观察文件保存是否异常。
- 学会把用户输入转换成更安全的文件名。

**Git 练习**：
- 检查 `logs/` 是否仍然被 `.gitignore` 忽略。
- 提交信息建议：`Support multiple chat sessions`。

---

### 第 12 课：阶段复盘与 Git 标签

**目标**：把第二阶段成果整理成一个清晰版本，并给 Git 打 tag。

**涉及文件**：
- `README.md`
- `PROGRESS.md`
- Git

**我会做什么**：
- 帮你整理第二阶段新增功能列表。
- 更新 README 的命令说明。
- 解释 Git tag 的作用。

**你要做什么**：
- 写第二阶段学习总结。
- 提交代码。
- 打一个标签，比如 `v0.2.0`。
- 推送 tag 到 GitHub。

**这一课核心学到什么**：
- 每个阶段结束都应该有可说明的版本。
- README 是项目对外表达，PROGRESS 是自己学习记录。
- Git tag 可以标记一个稳定学习节点。

**标准流程**：

```text
git status -> git add -> git commit -> git tag v0.2.0 -> git push -> git push --tags
```

**课后练习**：
- 在 GitHub Releases 页面写一段第二阶段 release note。

**Debug 练习**：
- 复盘第二阶段遇到的一个真实 bug，写清楚：现象、原因、定位方法、修复方式。

**Git 练习**：
- 使用 `git log --oneline --max-count=5` 查看最近提交。
- 使用 `git tag v0.2.0` 标记第二阶段完成点。
- 使用 `git push --tags` 推送标签。

---

## 第三阶段：代码结构升级（规划）

### 阶段目标

把目前集中在 `main.py` 的逻辑逐步拆开，让项目更容易读、改、测试。

### 计划课时

| 课时 | 主题 | 核心能力 |
|---|---|---|
| 第 13 课 | 把命令处理拆成函数 | 函数职责、输入输出 |
| 第 14 课 | 把 system prompt 配置化 | 配置管理、默认值 |
| 第 15 课 | 给 `memory.py` 加异常处理 | try/except、坏文件恢复 |
| 第 16 课 | 给 `llm_client.py` 加错误处理 | API 错误分类、友好提示 |
| 第 17 课 | 增加最小测试 | 单元测试、可验证代码 |
| 第 18 课 | 阶段复盘与重构总结 | 维护性、代码阅读能力 |

---

## 第四阶段：最小 Tool Use（规划）

### 阶段目标

让助手不仅会聊天，还能调用本地工具完成简单任务。

### 计划课时

| 课时 | 主题 | 核心能力 |
|---|---|---|
| 第 19 课 | 增加 `/time` 工具 | 调用标准库、格式化时间 |
| 第 20 课 | 增加 `/calc` 工具 | 输入解析、安全计算 |
| 第 21 课 | 让模型决定是否调用工具 | 模型输出解析、工具协议 |
| 第 22 课 | 工具结果写回 messages | tool result、上下文闭环 |
| 第 23 课 | 阶段复盘 | Tool Use 数据流 |

---

## 第五阶段：最小 RAG（规划）

### 阶段目标

让助手能读取本地资料，并基于资料回答问题。

### 计划课时

| 课时 | 主题 | 核心能力 |
|---|---|---|
| 第 24 课 | 新建 `docs/` 并读取 txt | 文件读取、文本数据 |
| 第 25 课 | 关键词搜索相关片段 | 最小检索、字符串匹配 |
| 第 26 课 | 把检索结果放进 prompt | 上下文拼接、引用资料 |
| 第 27 课 | 增加 `/askdoc` 命令 | 命令扩展、RAG 入口 |
| 第 28 课 | 阶段复盘 | RAG 数据流 |

---

## 概念速查表

| 概念 | 一句话解释 | 首次出现 |
|------|-----------|---------|
| API Key | 调用 API 的身份凭证，像密码一样不能泄漏 | 第 1 课 |
| base_url | API 服务器地址 | 第 1 课 |
| messages | 发给模型的对话消息列表 | 第 1 课 |
| system prompt | 给模型的角色设定指令 | 第 1 课 |
| while 循环 | 反复执行代码，直到遇到 break | 第 2 课 |
| input() | 从命令行读取用户输入 | 第 2 课 |
| continue | 跳过本轮后续代码，进入下一轮循环 | 第 2 课 |
| break | 结束当前循环 | 第 2 课 |
| context window | 模型一次能处理的最大上下文长度 | 第 3 课 |
| JSON | 一种轻量级数据交换格式 | 第 4 课 |
| with 语句 | 自动管理文件打开和关闭 | 第 4 课 |
| Path.parent | 获取路径的父目录 | 第 4 课 |
| 环境变量 | 存在系统或 `.env` 中的键值对配置 | 第 5 课 |
| 类型转换 | 把字符串转成数字等其他类型 | 第 5 课 |
| Git remote | 本地仓库记录的远程仓库地址 | 第 6 课 |
| tracking | 本地分支和远程分支的对应关系 | 第 6 课 |
| 列表切片 | 从列表中取出一部分元素 | 第 7 课 |
| generator | 边产生边返回数据的函数形式 | 第 8 课 |
| session | 一次独立聊天会话 | 第 11 课 |
| Git tag | 给某个提交打版本标签 | 第 12 课 |

---

## 异常处理指南

### 配置和 API 常见报错

**`ValueError: Missing OPENAI_API_KEY`**

说明 `.env` 没有被正确读取，优先检查：

```bash
pwd
ls -la .env
cat .env
```

**`openai.AuthenticationError`**

API Key 错误或无权限。检查 key 是否复制完整、平台是否匹配。

**`openai.APIConnectionError`**

无法连接服务器。检查网络、base_url、代理或平台服务状态。

**`ModuleNotFoundError`**

缺少依赖。运行：

```bash
pip install -r requirements.txt
```

### Python 语法常见报错

**`IndentationError`**

缩进错误。Python 用缩进表示代码块，循环和分支内部通常缩进 4 空格。

**`NameError`**

变量未定义。检查变量名是否拼写一致，是否在使用前赋值。

**`SyntaxError`**

语法错误。常见原因是括号没闭合、字符串没闭合、多行字符串写法不正确。

### JSON 和文件常见报错

**`FileNotFoundError`**

文件或目录不存在。保存文件前要确保父目录存在。

**`json.JSONDecodeError`**

JSON 文件格式坏了。常见原因是手动编辑时少了逗号、引号或括号。

### Git 常见报错

**`no tracking information for the current branch`**

本地分支还没有绑定远程分支。第一次推送使用：

```bash
git push -u origin main
```

**`Need to specify how to reconcile divergent branches`**

本地和远程都有各自提交，Git 不知道用 merge 还是 rebase。学习阶段优先使用：

```bash
git pull --no-rebase origin main
```

**`refusing to merge unrelated histories`**

本地和远程是两条独立历史。通常是 GitHub repo 创建时勾选了 README 或 LICENSE，而本地也已经 commit。更推荐重新建空 repo，或明确合并：

```bash
git pull --no-rebase origin main --allow-unrelated-histories
```
