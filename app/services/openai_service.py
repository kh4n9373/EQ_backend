import json
import re

import openai

from app.constants.prompt_library import SITUATION_ANALYZE_PROMPT
from app.core.config import settings


class OpenAIService:
    def __init__(self):
        pass

    def analyze_eq(self, situation: str, question: str, answer_text: str) -> tuple:
        prompt = SITUATION_ANALYZE_PROMPT
        client = openai.OpenAI(
            api_key=settings.openai_api_key, base_url=settings.openai_base_url
        )
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"""
SITUATION: {situation}

QUESTION: {question}

ANSWER: {answer_text}
""",
                },
            ],
            temperature=0.3,
        )

        reply = response.choices[0].message.content
        try:
            json_str = re.search(r"\{.*\}", reply, re.DOTALL).group()
            result = json.loads(json_str)
            # print("MODEL RESPONSE: ", result)
            return result["scores"], result["reasoning"]
        except Exception as e:
            return {
                "scores": {
                    "self_awareness": None,
                    "empathy": None,
                    "self_regulation": None,
                    "communication": None,
                    "decision_making": None,
                },
                "reasoning": {
                    "self_awareness": "Không phân tích được.",
                    "empathy": "Không phân tích được.",
                    "self_regulation": "Không phân tích được.",
                    "communication": "Không phân tích được.",
                    "decision_making": "Không phân tích được.",
                },
                "error": str(e),
            }
