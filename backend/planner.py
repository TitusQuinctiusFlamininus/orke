import requests
import json


SYSTEM_PROMPT = """
You are an autonomous QA engineer.

Return ONLY valid JSON.

Schema:
{
  "flows": [
    {
      "name": "string",
      "actions": [
        {
          "action": "click|fill",
          "selector": "string",
          "value": "string|null"
        }
      ],
      "expected": "string"
    }
  ]
}
"""


async def generate_test_plan(elements):

    prompt = f"""
    UI Elements:
    {json.dumps(elements, indent=2)}
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5-coder:7b",
            "prompt": SYSTEM_PROMPT + prompt,
            "stream": False,
        },
        timeout=120,
    )

    result = response.json()

    raw_response = result["response"]

    print("RAW MODEL RESPONSE:")
    print(raw_response)

    try:
        start = raw_response.index("{")
        end = raw_response.rindex("}") + 1

        json_str = raw_response[start:end]

        return json.loads(json_str)

    except Exception as e:
        print("JSON PARSE ERROR:", e)

        return {
            "flows": []
        }