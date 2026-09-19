import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def analyze_market(prompt):
    api_key = os.getenv("FEATHERLESS_API_KEY")
    if not api_key:
        raise RuntimeError(
            "FEATHERLESS_API_KEY is not set. Add it to a .env file."
        )

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.featherless.ai/v1",
        timeout=20.0,
    )

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
