from typing import List
from llm_client import ask_llm
from memory import load_history, save_history
from config import MAX_HISTORY_ROUNDS, MODEL


SYSTEM_PROMPT = "你是一个耐心的 AI 应用开发老师。"


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


def main():
    print("欢迎来我的频道，今天想聊点什么？")

    messages = load_history() or [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    while True:
        user_input = input("You: ")

        if user_input == "/help":
            print("""
    可用命令：
        /help 查看帮助
        /exit 退出程序
        /reset 清空上下文
        /save 保存对话记录
        /model 查看当前模型
        /count 查看当前对话记忆轮数
            """)
            continue

        elif user_input == "/reset":
            del messages[1:]
            print("上下文已清空")
            continue
        elif user_input == "/save":
            save_history(messages)
            print("System: 当前对话已保存。")
            continue
        elif user_input == "/model":
            print("当前模型：", MODEL)
            continue
        elif user_input == "/count":
            print("当前聊天记忆轮数为：", check_current_chat_nums(messages))
            continue
        elif user_input == "/exit":
            save_history(messages)
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})
        #添加trim_mess 判断，是否超出了限制
        trim_messages(messages, MAX_HISTORY_ROUNDS)
        answer = ask_llm(messages)
        messages.append({"role": "assistant", "content": answer})

        print("AI:", answer)


if __name__ == "__main__":
    main()
