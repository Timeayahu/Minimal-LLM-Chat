# Memory Flow

这份文档用于复盘第五阶段第 22 课的 Memory 数据流。

它回答一个核心问题：

```text
长期记忆和当前会话到底怎样分开，又怎样在调用模型前重新组合？
```

## 一句话总览

当前 Memory 数据流是：

```text
/remember
-> MemoryStore.add()
-> memory_data/memories.json
-> MemoryStore.load()
-> to_messages_text()
-> build_messages_with_memory() / decide_agent_step()
-> model messages
-> final answer
```

## 两种记忆

当前项目里有两种不同的记忆：

- `Session`: 当前会话记忆，保存 system、user、assistant 消息。
- `MemoryStore`: 长期记忆，保存跨会话稳定信息。

它们解决的问题不一样：

```text
Session.messages 解决“这次对话刚刚说过什么”。
MemoryStore 解决“跨很多次对话仍然值得记住什么”。
```

## Session

`Session` 负责短期上下文。

它保存：

- 当前会话名
- 当前会话 messages
- Agent trace
- 等待确认的工具调用

普通聊天或 Agent 回复会写入 `Session.messages`。当消息太多时，`trim()` 会裁剪旧对话，避免每次请求都带太长上下文。

这意味着 `Session.messages` 不是永久记忆。它是一次会话内的工作窗口。

## MemoryStore

`MemoryStore` 负责长期记忆。

它保存到：

```text
memory_data/memories.json
```

每条记忆现在包含：

- `id`: 记忆 ID
- `kind`: 记忆类型，例如 `fact`、`preference`、`learning`
- `content`: 记忆内容
- `created_at`: 创建时间

目前长期记忆通过 `/remember` 手动写入。省略类型时默认为 `fact`：

```text
/remember 用户喜欢用中文解释代码
/remember preference 用户喜欢先理解概念再看代码
/remember learning 用户正在学习 Agent Memory 架构
```

后续再让 Agent 自动判断什么值得记住。

## 写入流程

用户输入 `/remember ...` 后，命令层会调用：

```text
context["memory_store"].add(content)
```

`MemoryStore.add()` 会：

1. 生成一个递增 ID。
2. 创建一条 `MemoryItem`。
3. append 到内存中的 `memories` 列表。
4. 调用 `save()` 写入 JSON 文件。

这条路径不经过 `Session.messages`，因为它不是当前聊天内容，而是跨会话资料。

## 管理流程

长期记忆现在可以通过 ID 管理：

```text
/memories              查看最近记忆及其 ID
/memory mem_0001       查看一条记忆详情
/forget mem_0001       删除一条记忆
```

删除会立刻写回 JSON 文件。新增记忆会使用当前最大编号的下一个 ID，因此删除旧记忆后也不会复用它的 ID。

## 读取流程

程序启动时，`create_app_context()` 会调用：

```text
MemoryStore.load()
```

这样长期记忆会进入应用上下文：

```text
context["memory_store"]
```

后续命令、普通聊天和 Agent Loop 都通过 `context` 访问同一个长期记忆对象。

## Prompt 注入

长期记忆不会直接塞进 `Session.messages`。

普通聊天调用模型前，会通过：

```text
build_messages_with_memory(session.messages, memory_store)
```

临时构造一份发给模型的 messages：

```text
system prompt
-> long-term memory system message
-> recent user / assistant messages
```

这样模型能看到长期记忆，但本地保存的会话历史仍然保持干净。

## Agent 规划

Agent Loop 每一步调用 `decide_agent_step()` 时，也会传入：

```text
context["memory_store"].to_messages_text()
```

planner 因此可以在决定工具调用或最终回答时参考长期记忆。

这让长期记忆不仅影响最终措辞，也可能影响 Agent 的行动选择。

## 当前边界

当前实现仍然是教学版：

- 长期记忆需要用户通过 `/remember` 手动写入。
- 支持 `fact`、`preference`、`learning` 三种手动记忆类型。
- 支持查看和删除指定记忆，但还没有更新、去重或搜索。
- 还没有让 Agent 自动判断什么值得保存。
- 还没有独立的 `PromptBuilder`。

这些暂时不是问题。第 22 课的目标是先把短期 Session 和长期 Memory 分开，并确认长期记忆可以进入模型上下文。

## 下一步

下一课可以继续演进两个方向：

- 增强命令层：支持更新、去重和搜索记忆。
- 增强 Agent 层：让模型在回答后提出候选长期记忆，但先让用户确认再保存。
