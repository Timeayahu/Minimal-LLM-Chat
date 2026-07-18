from nexus.context import MemoryStore, Message, Session
from nexus.llm.client import stream_llm
from nexus.settings import MAX_HISTORY_ROUNDS


def build_messages_with_memory(
    messages: list[Message],
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

    return [messages[0], memory_message, *messages[1:]] # *用于给list元素解包


def handle_chat_message(
    session: Session,
    memory_store: MemoryStore,
    user_input: str,
) -> str:
    """处理一轮普通聊天：保存用户输入、调用模型、保存回答。"""
    messages = session.messages
    messages.append({"role": "user", "content": user_input})
    session.trim(MAX_HISTORY_ROUNDS)
    model_messages = build_messages_with_memory(messages, memory_store)

    part_of_ans = []
    print("AI: ", end="", flush=True)
    for chunk in stream_llm(model_messages):
        print(chunk, end="", flush=True)
        part_of_ans.append(chunk)
    print()

    answer = "".join(part_of_ans)
    messages.append({"role": "assistant", "content": answer})
    return answer
