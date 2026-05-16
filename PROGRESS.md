# 项目进度

## 总体状态

- 项目：最小 LLM 命令行聊天助手
- 开始日期：2026-05-03
- 当前阶段：第三阶段 — 工程化重构
- 当前课程：第 14 课（下一课：继续整理状态模型，评估是否引入 dataclass）
- 已完成：第 1-14 课主体内容
- 课程路线：阶段式持续迭代

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
  - 使用 `create_session()` 和 `create_app_context()` 收拢初始化逻辑，让 `main.py` 更专注于主循环。
- 设计判断：
  - 当前暂不引入 `dataclass`，因为 `Session` 目前主要还是结构化数据。
  - 当前暂不引入 Pydantic，因为数据来源主要由程序内部控制，还不需要运行时强校验。
- Debug 记录：
  - 重点区分 `session = create_session(new_session)` 与 `context["session"] = create_session(new_session)`。
  - 前者只是重新绑定局部变量；后者才是真正替换应用上下文里的当前会话。
- 下次计划：
  - 继续观察哪些行为应该归属于 `Session`。
  - 如 `reset`、`count_user_messages`、`history` 等行为开始聚集，再评估是否从 `TypedDict` 升级为 `dataclass` 或普通 class。
