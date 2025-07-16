import re
# from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import Runnable
import json
from dotenv import load_dotenv
import openai

load_dotenv()

client = openai.OpenAI(
    api_key="AIzaSyBpizwBkvyHbLLhLrbRurRNwLnt1BR_r-c",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
LLM_API_MODEL = "gemini-2.0-flash-lite"

def get_gemini_api_response(prompt: str) -> str:
    resp = client.chat.completions.create(
        model=LLM_API_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=2048
    )
    return resp.choices[0].message.content

def leadScoring(chat: str, threshold=8) -> dict:
    """Function to score leads based on chat messages."""

    def json_parser(response: str) -> dict:
        """Parse the JSON response from the model."""
        json_match = re.search(r'{.*}', response, re.DOTALL)
        if json_match:
            json_text = json_match.group()
            try:
                data = json.loads(json_text)
                return data
            except json.JSONDecodeError as e:
                print("⚠️ JSON parsing error:", e)
        else:
            print("⚠️ No JSON object found.")

    # llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    prompt = """
    شما یک دستیار بازاریابی هستید که چت بین فروشنده و مشتری شرکت را تحلیل می‌کنید.
    هدف: امتیازدهی به کیفیت لید بر اساس ۵ معیار زیر است ، برای اینکه مشخص شود آیا باید به کارشناس انسانی ارجاع داده شود یا خیر.

    برای هر معیار، امتیاز ۰ (ندارد)، ۱ (کم)، یا ۲ (قوی) بده و توضیح بده چرا.

    معیارها:
    1. قصد خرید (آیا علاقه‌مند به خدمات/محصول هستند؟)
    2. علاقه به قیمت (آیا به هزینه خدمات علاقه نشان داده‌اند؟ مثل پرسش درباره قیمت، تخفیف یا مقایسه با رقبا)
    3. فوریت یا زمان تصمیم‌گیری (آیا سریع می‌خواهند اقدام کنند؟)
    4. میزان تعامل (آیا پیام واضح، مرتبط و جدی است؟)
    5. درخواست ارجاع (آیا خواستار تماس، اطلاعات بیشتر یا پیگیری هستند؟)

    پاسخ را به فرمت JSON مثل زیر برگردان:
    {{
        "criteria": {{
            "intent": {{
            "score": <0|1|2>,
            "explanation": "<توضیح>"
            }},
            "ask about price": {{           
            "score": <0|1|2>,
            "explanation": "<توضیح>"
            }},
            "urgency": {{
            "score": <0|1|2>,
            "explanation": "<توضیح>"
            }},
            "engagement": {{    
            "score": <0|1|2>,
            "explanation": "<توضیح>"
            }},
            "handoff_trigger": {{
            "score": <0|1|2>,
            "explanation": "<توضیح>"
            }}
        }}
    }}

    متن چت:
    \"\"\"
    {chat}
    \"\"\"
    """
    prompt_template = ChatPromptTemplate.from_template(prompt)

    # chain: Runnable = prompt_template | llm | StrOutputParser()
    # response = chain.invoke({"chat": chat})
    response = get_gemini_api_response(prompt.replace("{chat}", chat))
    cleaned = json_parser(response)
    scores_raw = cleaned["criteria"]
    scores = {key: value["score"] for key, value in scores_raw.items()}
    cleaned["total_score"] = sum(scores.values())
    cleaned["lead_class"] = "interested" if cleaned.get("total_score", 0) >= threshold else "natural" if cleaned.get("total_score", 0) >= threshold//2 else "non-interested"
    return cleaned


# chat_input = """
# سلام، ما فروشگاه لوازم آرایشی هستیم. می‌خواستیم بدونیم فرایند جذب مشتری  تون چجوریه؟ هزینه‌هاش چنده؟
# """
# response= leadScoring(chat_input, threshold=8)
# print(json.dumps(response, indent=2, ensure_ascii=False))
