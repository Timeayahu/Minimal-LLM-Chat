from openai import OpenAI
from config import BASE_URL, MAX_TOKENS, MODEL, TEMPERATURE, require_api_key


client = OpenAI(
    api_key=require_api_key(),
    base_url=BASE_URL,
)


def ask_llm(messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    return response.choices[0].message.content


def know_inner_obj(messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    # print('---------------------------')
    # print('response',response)
    # print('---------------------------')
    # print('response.choices',response.choices)
    # print('---------------------------')
    print('response.choices[0].message',response.choices[0].message)
    print('---------------------------')


if __name__ == "__main__":
    messages = [
        {'role': 'system', 'content': '你是一个刘华强'},
        {'role': 'user', 'content': '生异形吗你们哥几个，哥俩'}

    ]
    ask_llm(messages)
