import streamlit as st
from LeadScoring import leadScoring  # if you keep leadScoring in another file like `utils.py`, otherwise define it inline
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Lead Scorer", layout="wide")

st.title("💬 Persian Lead Scoring Chatbot")

st.markdown("Paste a **Persian chat** between a salesperson and a client. The system will analyze it and score the lead.")

chat_input = st.text_area("📨 Chat transcript (in Persian)", height=250)

threshold = st.slider("🎯 Scoring threshold", 1, 10, 8)

if st.button("Score Lead"):
    if chat_input.strip():
        with st.spinner("Analyzing chat..."):
            try:
                result = leadScoring(chat_input, threshold=threshold)
#                 result = {
#   "criteria": {
#     "intent": {
#       "score": 1,
#       "explanation": "The customer shows some interest in the services by asking to recharge their account, indicating a desire to use the product. However, there is no explicit mention of a strong intent to purchase additional services or products."
#     },
#     "ask about price": {
#       "score": 2,
#       "explanation": "The seller provides detailed pricing information for the services, and the customer expresses a desire to recharge their account, which indicates an interest in the costs associated with the services."
#     },
#     "urgency": {
#       "score": 1,
#       "explanation": "While the customer wants to recharge their account, there is no clear indication of urgency or a specific timeline for when they want to complete this action."
#     },
#     "engagement": {
#       "score": 2,
#       "explanation": "The conversation is clear and relevant, with the customer actively engaging by asking for a recharge and the seller providing detailed instructions and additional strategies for generating leads."
#     },
#     "handoff_trigger": {
#       "score": 1,
#       "explanation": "The customer does not explicitly request a follow-up or additional information beyond the recharge process, but they do show some interest in lead generation strategies, which could warrant further assistance."
#     }
#   },
#   "total_score": 7,
#   "lead_class": "natural",
#   "chat": "Customer: send it\n\nSeller: Here is the download link for the plugin: [Download Plugin](https://example.com/download) \n\nFor cost calculations, you only need to recharge your panel as needed. Each automated process costs 2,500 Tomans, and for SMS campaigns, the price is 189 Tomans per page (67 characters) deducted from your balance. You can start with an initial recharge of 500,000 Tomans to test the system. \n\nIf you need further assistance, feel free to ask!\n\nCustomer: i want to charge my account\n\nSeller: To recharge your account, please follow these steps:\n\n1. **Log in** to your account on our platform.\n2. Navigate to the **\"Recharge\"** or **\"Account Balance\"** section.\n3. Choose the amount you wish to add to your account.\n4. Select your preferred payment method and complete the payment process.\n\nIf you encounter any issues or need further assistance, feel free to reach out!\n\nCustomer: leaad\n\nSeller: If you're looking to generate leads, here are some effective strategies:\n\n1. **Create a Lead Magnet:** Offer valuable content (e.g., eBooks, discounts, or free trials) in exchange for customer information.\n  \n2. **Utilize Social Media:** Promote your lead magnet on platforms like Instagram and Facebook to attract potential customers.\n\n3. **Email Marketing:** Send targeted campaigns to your existing contacts to encourage them to refer new leads.\n\n4. **Landing Pages:** Design dedicated landing pages for your offers that capture visitor information efficiently.\n\n5. **Networking:** Attend events or webinars related to your industry to connect with potential leads directly.\n\nIf you need more specific advice or details on any of these methods, let me know!"
# }
                st.success("✅ Analysis Complete")
                st.subheader("🔍 Detailed Scores")
                for key, value in result["criteria"].items():
                    st.markdown(f"**{key}**")
                    st.progress(value["score"] / 2)
                    st.markdown(f"_Explanation_: {value['explanation']}")
                    st.markdown("---")
                st.subheader("📊 Summary")
                st.markdown(f"**Total Score**: {result['total_score']}")
                st.markdown(f"**Lead Classification**: `{result['lead_class']}`")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
    else:
        st.warning("Please paste some chat text.")
