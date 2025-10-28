from openai import OpenAI
import os
print(os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful travel planner."},
        {"role": "user", "content": "Plan a 2-day trip in Auckland for a couple with a small budget."},
    ],
)

print(response.choices[0].message.content)
