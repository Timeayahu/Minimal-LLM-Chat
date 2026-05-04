from llm_client import ask_llm
from memory import load_history, save_history
from config import MODEL

SYSTEM_PROMPT = "你是一个耐心的 AI 应用开发老师。"


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
        elif user_input == "/exit":
            save_history(messages)
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})
        answer = ask_llm(messages)
        messages.append({"role": "assistant", "content": answer})

        print("AI:", answer)


if __name__ == "__main__":
    main()
