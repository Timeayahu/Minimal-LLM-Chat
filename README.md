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
- 支持 `/remember` 保存长期记忆，支持 `/memories`、`/memory`、`/forget` 管理长期记忆
- 普通聊天和 Agent 规划会读取长期记忆作为上下文参考
- 支持 `/tool` 手动调用本地工具
- 支持独立 JSONL TraceStore，运行时实时记录 planner、tool、confirmation 和 final 事件
- 支持 `/trace [run_id]` 查看当前会话或指定 Agent Run 的运行事件
- 支持 `/confirm` 和 `/cancel` 控制需要确认的工具调用
- 普通自然语言输入时，Agent 可自主判断是否需要调用工具
- 通过 `.env` 配置模型、API 地址和生成参数



## 文件结构

```text
Nexus Agent Kernel/
├── main.py           # 极薄的 CLI 启动入口
├── nexus/            # 所有可运行的应用源码
│   ├── app.py        # AppContext 与依赖组装
│   ├── settings.py   # .env 配置读取
│   ├── cli/          # 命令解析、命令实现与交互主循环
│   ├── agent/        # Planner、Agent Loop、错误与 JSONL 观测
│   ├── context/      # Session、会话快照与长期 Memory
│   ├── tools/        # 工具模型、内置工具与注册表
│   └── llm/          # Prompt 与 OpenAI-compatible 模型调用
├── tests/            # 自动化回归测试
├── docs/             # 项目规划与执行日志
├── skill/            # 本项目的教学课程 Skill
├── logs/             # 本地 Session 快照，不提交 Git
├── traces/           # 本地 JSONL 运行事件，不提交 Git
└── memory_data/      # 本地长期记忆，不提交 Git
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
/remember [类型] 内容 保存一条长期记忆，类型可选 fact/preference/learning
/memories 查看最近长期记忆
/memory 记忆ID 查看一条长期记忆详情
/forget 记忆ID 删除一条长期记忆
/model  查看当前模型
/tool   手动查看或调用本地工具
/trace [run_id] 查看当前会话或指定 Run 的运行事件
/confirm 确认执行待确认工具
/cancel 取消待确认工具
/exit   保存并退出
```



## 学习重点

这个项目练习的是 AI 应用最基础的数据流：

```text
.env -> nexus/settings.py -> nexus/llm/ -> nexus/agent/
                                      -> nexus/context/ + JSONL TraceStore
```

其中最重要的概念是 `messages`。它是一个列表，保存了 system、user、assistant 三类消息。模型本身不会自动记住上一轮对话，我们每次调用 API 时把完整 `messages` 发过去，它才表现得像有记忆。

## 项目状态

Nexus Agent Kernel 当前定位为 **Agent 架构学习与研究项目**。首轮 MVP 将形成一个
可运行、可观察、可对照实验的 `Agent Architecture Workbench`，用于理解和验证
通用 Agent、Loop、Workflow、Graph、Context、Harness、Tool 与 Eval 等设计理念。

项目状态不在 README 中重复维护：

- [项目计划](docs/PROJECT_PLAN.md)：愿景、MVP、十周路线、当前里程碑、完成标准与决策。
- [执行日志](docs/PROGRESS.md)：每次实际完成的变更、问题、验证与遗留风险。

