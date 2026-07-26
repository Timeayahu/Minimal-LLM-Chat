from nexus.context import MemoryStore, Message, Session
from nexus.llm.client import stream_llm
from nexus.settings import MAX_HISTORY_ROUNDS


def build_messages_with_memory( # 长期记忆注入
    messages: list[Message], # system prompt + assistant
    memory_store: MemoryStore,
    memory_limit: int = 10,
) -> list[Message]:
    """构造发给模型的消息列表，把长期记忆临时注入 system 区域。"""
    memory_text = memory_store.to_messages_text(limit=memory_limit)
    memory_message: Message = {
        "role": "system",
        "content": (
            "以下是跨会话长期记忆。"
            "这些信息可能包含用户偏好、稳定事实和学习状态。"
            "回答时优先参考这些记忆，但如果用户本轮明确表达了不同要求，"
            "以用户本轮要求为准。\n"
            f"{memory_text}"
        ),
    }

    if not messages:
        return [memory_message]

    return [messages[0], memory_message, *messages[1:]] # *用于给list元素解


def handle_chat_message(
    session: Session,
    memory_store: MemoryStore,
    user_input: str,
) -> str:
    """处理一轮普通聊天：保存用户输入、调用模型、保存回答
    一轮普通聊天需要的原料：上下文，上下文是模型的外部感知。上下文包含：系统级提示词，助手提示词，用户指令，工具类Schema，Skill的description
    """
    messages = session.messages
    messages.append({"role": "user", "content": user_input})
    session.trim(MAX_HISTORY_ROUNDS)
    model_messages = build_messages_with_memory(messages, memory_store)

    part_of_ans = []
    print("AI: ", end="", flush=True)
    for chunk in stream_llm(model_messages): #调用模型生成流式回复
        print(chunk, end="", flush=True)
        part_of_ans.append(chunk)
    print()

    answer = "".join(part_of_ans)
    messages.append({"role": "assistant", "content": answer})
    return answer
