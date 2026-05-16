from config import MAX_HISTORY_ROUNDS
from llm_client import stream_llm
from memory import trim_messages
from models import Message


def handle_chat_message(messages: list[Message], user_input: str) -> None:
    """处理一轮普通聊天：保存用户输入、调用模型、保存回答。"""
    messages.append({"role": "user", "content": user_input})
    trim_messages(messages, MAX_HISTORY_ROUNDS)

    part_of_ans = []
    print("AI: ", end="", flush=True)
    for chunk in stream_llm(messages):
        print(chunk, end="", flush=True)
        part_of_ans.append(chunk)
    print()

    answer = "".join(part_of_ans)
    messages.append({"role": "assistant", "content": answer})
