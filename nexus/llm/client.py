from openai import APIConnectionError, APIStatusError, OpenAI
from nexus.settings import BASE_URL, MAX_TOKENS, MODEL, TEMPERATURE, require_api_key


client = OpenAI(
    api_key=require_api_key(),
    base_url=BASE_URL,
)


def ask_llm(messages):
    """发起一次非流式 Chat Completions 请求，并把常见 API 异常转成可读文本。"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
    except APIConnectionError as exc:
        return (
            "API 连接失败。\n"
            f"当前 OPENAI_BASE_URL={BASE_URL}\n"
            "请检查：\n"
            "1. 如果使用本地模型服务，请先启动它，并确认端口地址正确。\n"
            "2. 如果使用云端平台，请把 .env 里的 OPENAI_BASE_URL 改成平台提供的地址。\n"
            "3. 如果需要代理，请确认代理程序已经启动。\n"
            f"原始错误：{exc}"
        )
    except APIStatusError as exc:
        return (
            "API 服务返回错误。\n"
            f"状态码：{exc.status_code}\n"
            f"当前 OPENAI_BASE_URL={BASE_URL}\n"
            f"当前 OPENAI_MODEL={MODEL}\n"
            "请优先查看本地模型服务窗口里的报错日志。"
        )

    return response.choices[0].message.content

def stream_llm(messages):
    """发起流式模型请求，逐个 yield 文本 chunk，供 CLI 边接收边显示。"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=True,
        )
    except APIConnectionError as exc:
        yield (
            "API 连接失败。\n"
            f"当前 OPENAI_BASE_URL={BASE_URL}\n"
            "请检查网络、base_url、代理或本地模型服务。\n"
            f"原始错误：{exc}"
        )
        return
    except APIStatusError as exc:
        yield (
            "API 服务返回错误。\n"
            f"状态码：{exc.status_code}\n"
            f"当前 OPENAI_BASE_URL={BASE_URL}\n"
            f"当前 OPENAI_MODEL={MODEL}"
        )
        return

    for chunk in response:
        content = chunk.choices[0].delta.content
        if content is not None:
            yield content
