from openai import OpenAI
import json

client = OpenAI()


SYSTEM_PROMPT = """
You are an autonomous QA engineer.

Given discovered UI elements:
1. Infer likely user flows
2. Identify possible edge cases
3. Generate exploratory actions
4. Predict areas where bugs may occur

Return JSON only.
"""


async def generate_test_plan(elements):
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps(elements),
            },
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)