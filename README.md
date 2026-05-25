# Nexus Agent Kernel

一个从最小命令行聊天助手演进出来的教学型通用 Agent 底座。

这个项目原名 `AI Learning Chat` / `Minimal LLM Chat`。现在它的目标是作为
**Nexus Agent Kernel** 持续演进：先把普通 Agent 该有的能力打扎实，再作为学习
Hermes-style、Claude Code-style、Codex-style 等智能体架构亮点的实验底座。

它不是为了立刻做成某个具体产品，而是为了扎实学习 Agent 工程：对话、工具调用、
多步 Agent Loop、记忆、RAG、日志、权限边界和可扩展架构。

## 功能

- 调用 OpenAI-compatible Chat Completions API
- 支持连续命令行聊天
- 使用 `messages` 保存多轮上下文
- 退出时自动保存对话历史
- 启动时自动读取历史
- 支持 `/help`、`/reset`、`/save`、`/model`、`/exit` 命令
- 支持 `/new` 创建新会话，支持 `/load` 恢复已保存会话
- 支持 `/tool` 手动调用本地工具
- 支持 `/trace` 查看最近 Agent 步骤记录
- 支持 `/confirm` 和 `/cancel` 控制需要确认的工具调用
- 普通自然语言输入时，Agent 可自主判断是否需要调用工具
- 通过 `.env` 配置模型、API 地址和生成参数

## 文件结构

```text
ai-learning-chat/
├── main.py           # 程序入口，处理命令行交互
├── app_context.py    # 应用上下文，连接 session、commands、tools
├── config.py         # 读取 .env 配置
├── llm_client.py     # 封装模型调用
├── chat.py           # 普通聊天入口
├── commands/         # 命令系统
├── tools/            # 工具系统
├── memory/           # 会话模型、历史读取和保存
├── models.py         # 轻量类型定义
├── requirements.txt  # Python 依赖
├── .env.example      # 配置模板
├── .gitignore        # Git 忽略规则
└── logs/             # 对话历史目录，不提交 Git
```

## 安装

建议先进入你的 Python 虚拟环境，然后安装依赖：

```bash
pip install -r requirements.txt
```

## 配置

复制配置模板：

```bash
cp .env.example .env
```

然后打开 `.env`，填写你的真实 API Key：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000
```

如果使用 DeepSeek、智谱、硅基流动等 OpenAI-compatible 平台，把 `OPENAI_BASE_URL` 和 `OPENAI_MODEL` 改成对应平台提供的值。

## 运行

```bash
python main.py
```

常用命令：

```text
/help   查看帮助
/reset  清空上下文
/save   保存当前对话
/new    自动创建新会话
/load   查看或加载已保存会话
/model  查看当前模型
/tool   手动查看或调用本地工具
/trace  查看最近 Agent 步骤记录
/confirm 确认执行待确认工具
/cancel 取消待确认工具
/exit   保存并退出
```

## 学习重点

这个项目练习的是 AI 应用最基础的数据流：

```text
.env -> config.py -> llm_client.py -> main.py -> memory/
```

其中最重要的概念是 `messages`。它是一个列表，保存了 system、user、assistant 三类消息。模型本身不会自动记住上一轮对话，我们每次调用 API 时把完整 `messages` 发过去，它才表现得像有记忆。

## 当前进展

截至第四阶段第 20 课，项目已经从“能聊天、能手动调用工具”的命令行程序，演进为一个具备最小 Agent Kernel 形态的教学项目：

- Agent 支持多步 `plan -> act -> observe -> final` 循环，并通过 `MAX_AGENT_STEPS` 限制无限循环风险
- 工具系统包含 `ToolSpec`、`ToolParameters`、`ToolResult`、`ToolError` 和统一错误码
- 工具参数会在 `ToolSpec.run()` 边界统一校验，Agent 和 `/tool` 手动入口共享同一套规则
- 运行过程会保存为 `AgentStepTrace`，可以通过 `/trace` 复盘工具选择、参数、结果、错误和最终回答
- 需要确认的工具会进入 `pending_tool_call`，由 `/confirm` 或 `/cancel` 明确处理
- 架构方向已确定为渐进式演进：短期保留教学实现，后续再拆出 `AgentRuntime`、`AgentService`、Policy、MemoryStore 等更正式的边界

## 长期目标

本项目的目标是构建一个小而扎实、可扩展、可研究的通用 Agent Kernel。

v0.1 完成标准包括：

- 用户自然输入时，Agent 能自主决定是否调用工具
- 有统一的 `ToolSpec`、工具注册表、工具结果和错误处理
- 有多步 Agent Loop，支持计划、工具调用、观察结果和最终回答
- 有短期 Session 记忆、会话摘要和最小长期用户画像
- 有基于成熟框架集成的 RAG：能导入资料、检索片段、基于资料回答
- 有 trace 日志，能观察工具调用过程
- 架构分层清楚，方便未来扩展不同 Agent 风格

未来可以基于这个底座实验：

- Hermes-style Agent：长期记忆、用户画像、人格一致性
- Claude Code-style Agent：代码库理解、文件搜索、补丁编辑、测试运行
- Codex-style Agent：工程化执行、沙箱权限、持续验证、交付总结

## 我的学习总结

在这个很简单的命令行项目中，我通过与ai交互学习的方式，了解了以下内容：
- 一个标准的项目所具备的结构，包括：.env存放配置文件、主文件、requirements.md、README.md
- agent的简单记忆存储
- 配置与后段代码分离，尽量减少代码的修改，把代码的扩展性做好
- 文件的读写操作
