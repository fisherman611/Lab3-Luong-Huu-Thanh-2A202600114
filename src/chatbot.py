import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")
base_url = os.getenv("NVIDIA_BASE_URL")

client = OpenAI(
  base_url = base_url,
  api_key = api_key
)

system_prompt = "Bạn là trợ lý du lịch, trả lời ngắn gọn trong 500 từ, thực tế và theo ngân sách."
user_prompt = "Tôi muốn đi du lịch trong tầm giá 5 triệu, bạn có gợi ý nào không?"

completion = client.chat.completions.create(
  model="openai/gpt-oss-20b",
  messages=[
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
  ],
  temperature=1,
  top_p=1,
  max_tokens=1000,
  stream=True
)

for chunk in completion:
  if not getattr(chunk, "choices", None):
    continue
  reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
  if reasoning:
    print(reasoning, end="")
  if chunk.choices and chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")