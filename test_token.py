from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

load_dotenv()

client = InferenceClient(
    model="HuggingFaceH4/zephyr-7b-beta",
    token=os.getenv("HF_TOKEN")
)

response = client.chat_completion(
    messages=[
        {"role": "user", "content": "Say hello in one sentence"}
    ],
    max_tokens=30
)

print(response.choices[0].message.content)
