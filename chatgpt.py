import os
import openai
from prompt import gen_system

openai.api_key = os.environ["OPENAI_API_KEY"]
openai.base_url = os.environ["OPENAI_URL"]
openai.default_headers = {"x-foo": "true"}


system_message = gen_system(type="tech_geek")

def get_reply(message):
    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            system_message,
            {
                "role": "user",
                "content": message,
            },
        ],
    )
    return completion.choices[0].message.content
