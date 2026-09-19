import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("FEATHERLESS_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.featherless.ai/v1"
)


def analyze_market(prompt):
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=300
    )

    return response.choices[0].message.content