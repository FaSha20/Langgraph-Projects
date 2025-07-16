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
