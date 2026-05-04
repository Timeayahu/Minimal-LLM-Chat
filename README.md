# Minimal LLM Chat

一个用于学习 AI 应用开发的最小命令行聊天助手。

这个项目从最小模型调用开始，逐步加入命令行循环、多轮对话记忆、JSON 历史保存和模型参数配置。

## 功能

- 调用 OpenAI-compatible Chat Completions API
- 支持连续命令行聊天
- 使用 `messages` 保存多轮上下文
- 退出时自动保存对话历史
- 启动时自动读取历史
- 支持 `/help`、`/reset`、`/save`、`/model`、`/exit` 命令
- 通过 `.env` 配置模型、API 地址和生成参数

## 文件结构

```text
ai-learning-chat/
├── main.py          # 程序入口，处理命令行交互
├── config.py        # 读取 .env 配置
├── llm_client.py    # 封装模型调用
├── memory.py        # 保存和读取对话历史
├── requirements.txt # Python 依赖
├── .env.example     # 配置模板
├── .gitignore       # Git 忽略规则
└── logs/            # 对话历史目录，不提交 Git
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
/model  查看当前模型
/exit   保存并退出
```

## 学习重点

这个项目练习的是 AI 应用最基础的数据流：

```text
.env -> config.py -> llm_client.py -> main.py -> memory.py
```

其中最重要的概念是 `messages`。它是一个列表，保存了 system、user、assistant 三类消息。模型本身不会自动记住上一轮对话，我们每次调用 API 时把完整 `messages` 发过去，它才表现得像有记忆。

## 下一步计划

- 限制最多保留最近 10 轮对话
- 增加多个历史文件
- 增加流式输出
- 增加简单的工具调用
