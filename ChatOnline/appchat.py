import streamlit as st
from LeadScoring import leadScoring, get_gemini_api_response
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Lead Scoring Chat", layout="wide")

st.title("💬 Persian Lead Scoring Chatbot")
st.markdown("شبیه‌سازی گفت‌وگوی مشتری و فروشنده. ابتدا فروشنده پیام می‌دهد، سپس شما پاسخ دهید. در پایان، روی «امتیازدهی» بزنید.")

# Define static content
FAQ = """سوال: کسب‌وکارتون چیه و در چه حوزه‌ای فعالیت می‌کنید؟
در کسب‌وکارهایی که تکرار به خرید معناداره و خریدها در بازه‌هایی زیر حداکثر ۶ ماه تکرار میشه، فیچرهایی مثل کش‌بک بیشترین اثر رو داره. اگر تکرار به خرید در بازه بزرگ‌تریه باید روی فیچرهایی مثل کمپین‌های پیامکی و نظرسنجی و گروه‌بندی و… هم مانور بدیم.
سوال: کسب‌وکارتون آنلاینه یا حضوری؟ اگر آنلاینه آیا سایت وردپرس یا پیج اینستاگرام دارید؟
برای کسب‌وکارها آنلاین می‌تونن سایت وردپرس یا پیج اینستاگرام رو به دوباره متصل کنن تا به صورت خودکار فرآیند‌ها انجام بشه.
سوال: تا الان شماره مشتریانتون رو جمع‌آوری کردید؟
اگر مشتری لیستی از شماره مشتریانش داره می‌تونیم کمپین پیامکی رو پیشنهاد بدیم. با اطمینان خاطر از اینکه قطعا کمپین پیامکی فروش خوبی به همراه داره.
سوال: چطوری به افزایش فروشم کمک می‌کنید؟
در پاسخ به این سوال به صورت مرحله به مرحله، لید مگنت، کش‌بک و کمپین‌های پیامکی رو به همراه اثر احتمالیش شرح بدیم.
 سوال: قیمت محصولتون به چه صورته؟
در پاسخ به این سوال: برای استفاده از نرم‌افزار باشگاه مشتریان نیازی به خرید اشتراک نیست. شما می‌تونید به مقدار نیازتون پنل رو شارژ کنید. به ازای هر روند خودکار ۲۵۰۰ تومان از شارژ پنلتون کسر میشه. برای کمپین‌های پیامکی هم قیمت هر صفحه پیامک (معادل ۶۷ کاراکتر) ۱۸۹ تومان هست که از شارژتون کم میشه. برای شروع می‌تونید با ۵۰۰ هزار تومن شارژ اولیه کارتون رو آغاز کنید و سیستم رو تست کنید. کاتالوگ قیمت رو ارسال کن.
چالش: اگر دیدیم مشتری چالش قیمتی داره.
شما می‌تونید هیچ هزینه‌ای پرداخت نکنید و از دوباره استفاده کنید. ما هیچ هزینه‌ای بابت روندها و پیامک‌ها دریافت نمی‌کنیم ولی در پایان هر ماه ۵ درصد از فروش ایجاد شده توسط دوباره رو باید به عنوان کمیسیون از حساب شما کسر میشه. پیشنهاد ما اینه که با مدل اقتصادی پیش برید چون از این مدل به صرفه‌تر هست.
سوال: افزونه وردپرس باشگاه مشتریان سایت رو کند نمی‌کنه؟
خیر. افزونه وردپرس دوباره فقط دیتای مبلغ سفارش و نام و شماره مشتری رو از طریق API برمی‌داره و تمام محاسبات روی دیتابیس‌های دوباره انجام میشه و حتی پیامک‌ها هم از طریق دوباره ارسال میشه و اصلا سایت رو کند نمی‌کنه.
سوال: می‌تونم مشتریان قبلی رو با باشگاه سینک کنم؟
بله. شما می‌تونید لیست مشتریان قبلی رو در وردپرس سینک کنید و مشکلی نداره.
سوال: برای نصب به راهنمایی نیاز دارم.
ارسال ویدیوی آموزشی نصب افزونه.
سوال: افزونه وردپرس دوباره، با قالب سایت من تداخل نداره؟
خیر. افزونه دوباره با اکثر قالب‌ها تست شده و هیچ تداخلی تاکنون با قالب‌های وردپرسی مشاهده نشده است.
 سوال: می‌تونم بدونم چه سایتایی از افزونه دوباره استفاده کردن یا می‌کنن؟
بله در ادامه لیستی از بخشی از سایت‌هایی که از دوباره استفاده می‌کنن براتون ارسال می‌کنیم.
خشکبار نجوان (https://najvanshop.ir/)
خشکبار اعتماد(https://www.etemadnuts.ir/)
روستاژ -ارگانیک و خشکبار (https://roostaj.com/)
وندا کالا-شکلات (https://vandakala.ir/)
مهرشاپ (https://mehrbeautyshop.com/)
فروشگاه خوشگل‌شو
(https://khoshgelshoo.com/)
فروشگاه نت آف (https://netoffshop.ir/)
دایان کالا (https://daiankala.com/)
اگه وسط کار به مشکلی بخورم، چطور با تیم پشتیبانی ارتباط بگیرم؟
دوباره پشتیبانی کامل، سریع و چندکاناله داره:
📞 تماس تلفنی: ۰۲۱-۹۱۰۷۰۷۵۴ داخلی ۱۷۳
💬 پیام در چت آنلاین در سایت دوباره
💬 واتس‌اپ: شماره مستقیم پشتیبان برای ارتباط فوری +989912152844
💬 تلگرام پشتیبانی به آی‌دی: https://t.me/dobare2024
⏱️ در روزهای کاری، زمان پاسخگویی معمولاً کمتر از ۲ ساعت و در روزهای تعطیل حداکثر ۱۲ ساعت هست.
"""
system_prompt = f"You are a helpful marketing assistant. this is frequently asked questions that normally you have been asked about:{FAQ}. Answer briefly and concisely without extra explanations."

starting_message = """سلام
وقت بخیر.
عاطفه شریفی هستم.
شما سایت وردپرسی دارین؟
ما یک افزونه برای افزایش نرخ تبدیل بازدیدکننده‌ها به خریدار و همچنین افزایش سبد خرید مشتری‌ها و نرخ بازگشت اون‌ها به سایت فروشگاهی ووکامرسی توسعه دادیم.
افزونه تا حالا 2000 نصب فعال در ژاکت داشته،
اگه تمایل دارید بیشتر توضیح بدم"""

# Initialize chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "agent", "message": starting_message}]

# Display all chat messages
for msg in st.session_state.chat_history:
    with st.chat_message("👤" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["message"])

# User inputs their message as buyer
user_message = st.chat_input("✍️ پاسخ خود را وارد کنید...")

user_messages = ""

if user_message:
    # Append user message
    st.session_state.chat_history.append({"role": "user", "message": user_message})
    
    user_messages += user_message
    # Generate agent response
    agent_response = get_gemini_api_response(system_prompt + "\n" + user_messages)
    st.session_state.chat_history.append({"role": "agent", "message": agent_response})

    st.rerun()

# Threshold slider
threshold = st.slider("🎯 آستانه امتیازدهی", 1, 10, 8)

# Score button
if st.button("Lead Score"):
    full_chat = ""
    for msg in st.session_state.chat_history:
        full_chat += ("مشتری: " if msg["role"] == "user" else "فروشنده: ") + msg["message"] + "\n"

    if full_chat.strip():
        with st.spinner("در حال تحلیل چت..."):
            try:
                result = leadScoring(full_chat, threshold=threshold)
                st.success("✅ تحلیل کامل شد")

                st.subheader("📊 نتایج تحلیلی")
                for key, value in result["criteria"].items():
                    st.markdown(f"**{key}**")
                    st.progress(value["score"] / 2)
                    st.markdown(f"_توضیح_: {value['explanation']}")
                    st.markdown("---")

                st.markdown(f"**امتیاز کل**: {result['total_score']}")
                st.markdown(f"**طبقه‌بندی لید**: `{result['lead_class']}`")

            except Exception as e:
                st.error(f"❌ مشکلی رخ داد: {e}")
    else:
        st.warning("مکالمه‌ای برای تحلیل وجود ندارد.")

# Reset chat
if st.button("🔄 Reset"):
    st.session_state.chat_history = [{"role": "agent", "message": starting_message}]
    st.rerun()
