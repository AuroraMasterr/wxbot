import os
import openai
from prompt import prompts

openai.api_key = os.environ["OPENAI_API_KEY"]
openai.base_url = os.environ["OPENAI_URL"]
openai.default_headers = {"x-foo": "true"}


def gen_system(type="tech_geek"):
    system_message = dict()
    system_message["role"] = "system"
    system_message["content"] = prompts[type]
    return system_message


def gen_message(role, m):
    message = dict()
    message["role"] = role
    message["content"] = m
    return message


# system_message = gen_system(type="tech_geek")
system_message = gen_system(type="cat_girl")

history_messages = []
WINDOW_SIZE = 50


def set_system(type):
    global system_message
    system_message = gen_system(type)


def update_history(message):
    global history_messages
    history_messages.append(message)
    if len(history_messages) > 10 * WINDOW_SIZE:
        history_messages = history_messages[-WINDOW_SIZE:]


def get_reply(m):
    update_history(gen_message("user", m))
    print(history_messages)
    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[system_message] + history_messages[-WINDOW_SIZE:],
    )
    reply = completion.choices[0].message.content
    update_history(gen_message("assistant", reply))
    return reply
