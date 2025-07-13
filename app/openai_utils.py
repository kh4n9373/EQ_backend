# Hàm mock, sau này sẽ tích hợp OpenAI API
import json
import re
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.base_url = os.getenv("OPENAI_BASE_URL")

def analyze_eq(situation: str, question: str, answer_text: str) -> dict:
    prompt = f"""
Bạn là một chuyên gia EQ. Hãy phân tích câu trả lời dưới đây và chấm điểm theo 5 trụ cột EQ. 
Đồng thời giải thích lý do cho từng điểm (vì sao bạn cho điểm, vì sao cho điểm cao, vì sao không cho điểm tuyệt đối).

Các trụ cột EQ:
- Self-Awareness: Tự nhận thức về cảm xúc của bản thân
- Empathy: Hiểu và cảm thông với cảm xúc của người khác
- Self-Regulation: Kiểm soát cảm xúc và Khả năng tự điều chỉnh
- Communication: Kỹ nănng giao tiếp
- Decision-Making: Quyết định và hành động cuối cùng

Tình huống:
"{situation}"
Câu hỏi:
"{question}"
Câu trả lời:
"{answer_text}"

Hãy trả về kết quả dưới dạng JSON với cấu trúc sau:
{{
  "scores": {{
    "self_awareness": <điểm từ 0 đến 10>,
    "empathy": <điểm>,
    "self_regulation": <điểm>,
    "communication": <điểm>,
    "decision_making": <điểm>
  }},
  "reasoning": {{
    "self_awareness": "<giải thích ngắn gọn>",
    "empathy": "<giải thích>",
    "self_regulation": "<giải thích>",
    "communication": "<giải thích>",
    "decision_making": "<giải thích>"
  }}
}}
    """

    response = openai.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[
            {"role": "system", "content": "Bạn là một chuyên gia EQ và đánh giá hành vi con người dựa trên phản ứng cảm xúc."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    reply = response.choices[0].message.content
    # Trích JSON từ nội dung trả về
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
                "decision_making": None
            },
            "reasoning": {
                "self_awareness": "Không phân tích được.",
                "empathy": "Không phân tích được.",
                "self_regulation": "Không phân tích được.",
                "communication": "Không phân tích được.",
                "decision_making": "Không phân tích được."
            },
            "error": str(e)
        }
