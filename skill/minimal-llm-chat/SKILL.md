---
name: minimal-llm-chat
description: >-
  6 节课渐进式教学，从零构建一个最小 LLM 命令行聊天助手。
  覆盖 Python 文件结构、API 调用、多轮对话、JSON 持久化、
  配置管理、Git 提交等核心技能。
metadata:
  lessons: 6
  difficulty: beginner
  prerequisites:
    - Python 基础语法（变量、函数、循环）
    - 能在命令行运行 Python
  tech_stack:
    - Python 3.11+
    - OpenAI-compatible API
    - python-dotenv
    - JSON
  tags:
    - python
    - llm
    - cli
    - tutorial
---

# Minimal LLM Chat — 课程 Skill

## 项目概览

用 6 节课，从零构建一个命令行 LLM 聊天助手。每节课只改 1-2 个文件，
确保你理解每行代码在做什么。

### 最终效果

```
$ python main.py
System: 你是一个耐心的 AI 应用开发老师。（system prompt）
You: 什么是 LLM？
AI: LLM 是 Large Language Model...
You: /reset
System: 上下文已清空。
You: /exit
Goodbye!
```

### 项目文件结构

```
ai-learning-chat/
├── main.py          # 程序入口，命令行循环
├── config.py        # 读取 API Key、模型名、base_url
├── llm_client.py    # 封装模型调用
├── memory.py        # 保存和读取对话历史
├── requirements.txt # 依赖
├── .env             # API Key（不提交 Git）
├── .gitignore       # 忽略敏感文件
├── logs/            # 对话历史 JSON 文件
└── README.md        # 项目说明
```

### 教学原则

参考 `AI_TUTOR_RULES.md`：

1. 先解释"为什么做这一步"
2. 每次最多改 1-2 个文件
3. 关键代码必须解释数据流
4. 每次留一个 5-15 分钟的小练习
5. 报错先教怎么看，再给修复

## 课程详情

---

### 第 1 课：跑通最小模型调用

**目标**：Python 调用一次大模型 API，打印回答。

**涉及文件**：
- `main.py` — 程序入口
- `config.py` — 读取环境变量
- `llm_client.py` — 封装 API 调用
- `.env` — 存放 API Key

**核心概念**：
- `API Key` 是什么（鉴权凭证）
- `base_url` 是什么（API 地址）
- `model` 参数（选择哪个模型）
- `messages` 结构（system / user / assistant 三种角色）
- `python-dotenv` 读取 `.env` 文件

**数据流**：
```
.env → config.py（读取 API Key）→ llm_client.py（构造请求）→ API → 打印回答
```

**用户练习**：修改 system prompt 为自己风格的提示词。

---

### 第 2 课：加入命令行循环

**目标**：用户可以连续输入问题，模型连续回答。

**涉及文件**：
- `main.py` — 增加 `while True` 循环

**核心概念**：
- `while True` 无限循环
- `input()` 获取用户输入
- 命令解析（`/exit` 退出）
- `if/elif` 分支处理

**数据流**：
```
input() → 判断是否为命令 → 是：执行命令 / 否：调 API → 打印回答 → 回到 input()
```

**用户练习**：增加 `/help` 命令显示可用命令列表。

---

### 第 3 课：加入多轮对话历史

**目标**：模型能记住前面说过的话。

**涉及文件**：
- `llm_client.py` — 接收完整 messages 列表
- `main.py` — 维护 messages 列表，每轮 append
- `memory.py`（首次引入，但只做内存管理）

**核心概念**：
- 为什么单次调用没有记忆（API 每次调用都是独立的）
- `messages` 列表就是"记忆"
- 每轮对话 = append 两条：user 输入 + assistant 回答
- 上下文窗口限制（太长会报错或丢失早期内容）

**数据流**：
```
messages = [system] → 用户输入 → append user msg → 调 API → append assistant msg → messages 变长
```

**用户练习**：限制最多保留最近 10 轮对话（最早超出部分丢弃）。

---

### 第 4 课：保存和读取历史

**目标**：程序退出后，下次启动还能读取历史。

**涉及文件**：
- `memory.py` — 实现 `save_history()` 和 `load_history()`
- `main.py` — 启动时 load，退出时 save

**核心概念**：
- `json.dump()` / `json.load()` 读写 JSON
- `ensure_ascii=False`（中文不乱码）
- `indent=2`（文件可读）
- `open()` 的 `with` 语句
- 异常处理：文件不存在、写入权限

**数据流**：
```
启动 → load_history() → 从 JSON 文件恢复 messages
对话 → append messages
退出 → save_history() → messages 写入 JSON 文件
```

**用户练习**：增加 `/save` 命令手动保存当前对话。

---

### 第 5 课：配置化模型参数

**目标**：模型名、API 地址、温度参数从配置读取。

**涉及文件**：
- `config.py` — 增加模型名、temperature、max_tokens 等配置
- `llm_client.py` — 使用配置中的参数

**核心概念**：
- 配置和代码分离（不改代码就能切换模型）
- `.env` 不提交 Git（防止泄露）
- 多模型切换（deepseek / glm / openai）

**用户练习**：增加 `/model` 命令显示当前模型名。

---

### 第 6 课：整理 README + Git 提交

**目标**：把项目整理成别人也能跑的学习作品。

**涉及文件**：
- `README.md` — 项目说明
- 第一次 `git init` + `git commit`

**核心概念**：
- README 写什么（简介、安装、配置、运行、功能列表、下一步计划）
- `.gitignore` 保护敏感文件
- 第一次 Git 提交的意义
- 每完成一课提交一次的习惯

**用户练习**：写一段"我从这个项目学到了什么"，用自己的话总结。

---

## 概念速查表

| 概念 | 一句话解释 | 出现在第几课 |
|------|-----------|-------------|
| API Key | 调用 API 的身份凭证，像密码一样，不能泄漏 | 1 |
| base_url | API 服务器的地址 | 1 |
| messages | 发给模型的对话消息列表，每轮包含 user 和 assistant 两条 | 1 |
| system prompt | 给模型的角色设定指令 | 1 |
| while 循环 | 反复执行一段代码，直到遇到 break | 2 |
| input() | 从命令行读取用户输入 | 2 |
| context window | 模型一次能处理的最大 token 数量 | 3 |
| JSON | 一种轻量级数据交换格式，Python 用 json 模块处理 | 4 |
| with 语句 | 自动管理文件打开和关闭的语法 | 4 |
| ensure_ascii | JSON 输出时是否用 ASCII 转义非英文字符 | 4 |
| 环境变量 | 存在操作系统中的键值对，用于配置 | 5 |
| .env | 存放环境变量的文件，dotenv 库负责读取 | 5 |
| git init | 初始化 Git 仓库，开始版本管理 | 6 |
| .gitignore | 告诉 Git 哪些文件不要跟踪 | 6 |

## 异常处理指南

### 第 1 课常见报错

**`openai.AuthenticationError`**：API Key 错误
→ 检查 `.env` 文件格式：`API_KEY=sk-xxx`（不要引号，不要空格）

**`openai.APIConnectionError`**：无法连接服务器
→ 检查 `base_url` 是否正确，网络是否正常

**`ModuleNotFoundError`**：缺少依赖
→ `pip install -r requirements.txt`

### 第 2-3 课常见报错

**`IndentationError`**：缩进错误
→ Python 用缩进表示代码块，确保 `while` 循环内代码统一缩进 4 空格

**`NameError`**：变量未定义
→ 检查变量名是否拼写正确，是否在使用前已赋值

### 第 4 课常见报错

**`FileNotFoundError`**：文件不存在
→ 首次运行时还没有历史文件，需要处理这个异常

**`json.JSONDecodeError`**：JSON 格式损坏
→ 检查 JSON 文件是否被手动修改过

### 第 5 课常见报错

**`KeyError`**：字典中找不到某个键
→ 检查 `.env` 中是否定义了所有必需的配置项

---

## 学习方法建议

1. **不要复制粘贴代码** — 手动抄一遍更能理解
2. **每节课后做练习** — 练习比听课重要
3. **主动修改代码看效果** — 故意改错再修复，理解更深
4. **每课提交一次 Git** — 养成版本管理习惯
5. **用自己的话写总结** — 最好的检验方式是教别人

## 后续扩展方向

完成 6 课后，可以自然升级到：

1. **RAG（检索增强生成）**：给模型提供外部文档作为参考
2. **Tool Use（函数调用）**：让模型能调用计算器、搜索等工具
3. **Streaming（流式输出）**：逐字显示模型回答
4. **Web UI（网页界面）**：用 FastAPI + HTML 替换命令行
5. **多种模型切换**：运行时动态切换模型
