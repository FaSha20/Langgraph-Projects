import re
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import Runnable
import json
from dotenv import load_dotenv
# import openai

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

    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
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
    # prompt_template = ChatPromptTemplate.from_template(prompt)

    chain: Runnable = prompt_template | llm | StrOutputParser()
    response = chain.invoke({"chat": chat})
    # response = get_gemini_api_response(prompt.replace("{chat}", chat))
    return {
  "criteria": {
    "intent": {
      "score": 1,
      "explanation": response + "The customer shows some interest in the services by asking to recharge their account, indicating a desire to use the product. However, there is no explicit mention of a strong intent to purchase additional services or products."
    },
    "ask about price": {
      "score": 2,
      "explanation": "The seller provides detailed pricing information for the services, and the customer expresses a desire to recharge their account, which indicates an interest in the costs associated with the services."
    },
    "urgency": {
      "score": 1,
      "explanation": "While the customer wants to recharge their account, there is no clear indication of urgency or a specific timeline for when they want to complete this action."
    },
    "engagement": {
      "score": 2,
      "explanation": "The conversation is clear and relevant, with the customer actively engaging by asking for a recharge and the seller providing detailed instructions and additional strategies for generating leads."
    },
    "handoff_trigger": {
      "score": 1,
      "explanation": "The customer does not explicitly request a follow-up or additional information beyond the recharge process, but they do show some interest in lead generation strategies, which could warrant further assistance."
    }
  },
  "total_score": 7,
  "lead_class": "natural",
  "chat": "Customer: send it\n\nSeller: Here is the download link for the plugin: [Download Plugin](https://example.com/download) \n\nFor cost calculations, you only need to recharge your panel as needed. Each automated process costs 2,500 Tomans, and for SMS campaigns, the price is 189 Tomans per page (67 characters) deducted from your balance. You can start with an initial recharge of 500,000 Tomans to test the system. \n\nIf you need further assistance, feel free to ask!\n\nCustomer: i want to charge my account\n\nSeller: To recharge your account, please follow these steps:\n\n1. **Log in** to your account on our platform.\n2. Navigate to the **\"Recharge\"** or **\"Account Balance\"** section.\n3. Choose the amount you wish to add to your account.\n4. Select your preferred payment method and complete the payment process.\n\nIf you encounter any issues or need further assistance, feel free to reach out!\n\nCustomer: leaad\n\nSeller: If you're looking to generate leads, here are some effective strategies:\n\n1. **Create a Lead Magnet:** Offer valuable content (e.g., eBooks, discounts, or free trials) in exchange for customer information.\n  \n2. **Utilize Social Media:** Promote your lead magnet on platforms like Instagram and Facebook to attract potential customers.\n\n3. **Email Marketing:** Send targeted campaigns to your existing contacts to encourage them to refer new leads.\n\n4. **Landing Pages:** Design dedicated landing pages for your offers that capture visitor information efficiently.\n\n5. **Networking:** Attend events or webinars related to your industry to connect with potential leads directly.\n\nIf you need more specific advice or details on any of these methods, let me know!"
}
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
