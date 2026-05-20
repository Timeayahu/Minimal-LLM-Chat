from config import MAX_HISTORY_ROUNDS
from llm_client import stream_llm
from memory import Session


def handle_chat_message(session: Session, user_input: str) -> None:
    """处理一轮普通聊天：保存用户输入、调用模型、保存回答。"""
    messages = session.messages
    messages.append({"role": "user", "content": user_input})
    session.trim(MAX_HISTORY_ROUNDS)

    part_of_ans = []
    print("AI: ", end="", flush=True)
    for chunk in stream_llm(messages):
        print(chunk, end="", flush=True)
        part_of_ans.append(chunk)
    print()

    answer = "".join(part_of_ans)
    messages.append({"role": "assistant", "content": answer})
