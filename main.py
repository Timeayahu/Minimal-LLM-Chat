from typing import Any
from commands import get_commands
from llm_client import stream_llm
from memory import generate_session_name, load_history
from config import MAX_HISTORY_ROUNDS, MODEL


SYSTEM_PROMPT = (
    "你是一个耐心的 AI 应用开发老师。"
    "无论用户使用什么语言提问，你都默认使用简体中文回答。"
    "除非用户明确要求英文、翻译成英文或输出英文内容，否则不要使用英文回答。"
)


def init_messages(session_name="default") -> list[dict[str, Any]]:
    """
    初始化消息列表，加载指定会话的历史记录。

    参数：
        session_name: 要加载的会话名称

    返回：
        包含 system prompt 的消息列表
    """
    messages = load_history(session_name)

    if not messages:
        return [{"role": "system", "content": SYSTEM_PROMPT}]

    if messages[0].get("role") == "system":
        messages[0]["content"] = SYSTEM_PROMPT
    else:
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    return messages


def trim_messages(current_memory:list, chat_limits:int):
    """
    记忆压缩：agent记忆最多只保留最近10轮对话

    实现：
        触发时机：当保存用户的聊天对话时，判断加入后，是否超出了10轮。若超出，则删除掉最开始的那条。
        若超过10轮：每次删除头一条历史对话记录

    input：接收来自load_memory的list
    output：更新后的list

    如何判断：查询当前list有多少次“user”出现，user的数量是对话轮数
    """
 
    while check_current_chat_nums(current_memory) > chat_limits:       
        del current_memory[1:3]
        
        
    
def check_current_chat_nums(current_memory):
    return  sum(1 for msg in current_memory if msg["role"] == "user")  


def parse_command(user_input: str) -> tuple[str, list[str]]:
    """从用户输入中解析命令名和参数。"""
    if not user_input.startswith("/"):
        return "", []

    parts = user_input.split()
    return parts[0], parts[1:]


def main():
    print("欢迎来我的频道，今天想聊点什么？")

    # 每次启动都自动创建一个新会话，避免覆盖旧的 default 历史。
    current_session = generate_session_name()
    messages = init_messages(current_session)
    commands = get_commands()

    while True:
        user_input = input("You: ")
        command_name, args = parse_command(user_input)
        command = commands.get(command_name)

        if command:
            context = {
                "messages": messages,
                "current_session": current_session,
                "commands": commands,
                "model": MODEL,
                "init_messages": init_messages,
            }
            should_continue = command.execute(context, args)
            messages = context["messages"] #状态同步，/new会修改messages，因此需要同步给messages变量
            current_session = context["current_session"]
            if should_continue:
                continue
            break

        if user_input.startswith("/"):
            print(f"未知命令：{command_name}")
            print("输入 /help 查看可用命令。")
            continue

        messages.append({"role": "user", "content": user_input})
        #添加trim_mess 判断，是否超出了限制
        trim_messages(messages, MAX_HISTORY_ROUNDS)
        part_of_ans = []
        print("AI: ", end="", flush=True)
        for chunk in stream_llm(messages):
            print(chunk, end='', flush=True)
            part_of_ans.append(chunk)
        print()
        answer = ''.join(part_of_ans)
        messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
