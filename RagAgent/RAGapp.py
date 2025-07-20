
import streamlit as st
import os
from ragAgentt import *
import pandas as pd

st.set_page_config(page_title="FAQ RAG Assistant 🤖", layout="wide")

st.title("FAQ (RAG Assistant) 💬")
st.markdown("با استفاده از هوش مصنوعی، به سوالات شما از مجموعه سوالات متداول (FAQ) پاسخ می‌دهم.")

# --- File Paths and Initial Setup ---
# Define your actual JSON file path here for the RAG system
json_file_path = r".\dobare_faqs.json"

# --- RAG Initialization (cached) ---
@st.cache_resource # Caching the initialization of RAG components
def initialize_rag_components(file_path):
    st.write("🔄 در حال بارگذاری و آماده‌سازی سیستم RAG... (این ممکن است چند لحظه طول بکشد)")
    documents = load_and_chunk_json_faqs(file_path)
    st.success(f"✅ {len(documents)} تکه (chunk) از داده‌ها بارگذاری و آماده شد.")
    vectorstore, embeddings = setup_vector_store(documents, EMBEDDING_MODEL_NAME, VECTOR_DB_PATH)
    st.success("✅ پایگاه داده و مدل تعبیه (embedding) آماده هستند.")
    persian_prompt = create_persian_prompt_template()
    st.success("✅ الگوی (Prompt) فارسی آماده شد.")
    return vectorstore, persian_prompt

# Call the initialization function
vectorstore, persian_prompt = initialize_rag_components(json_file_path)

st.divider()

# --- User Input ---
user_query = st.text_input("سؤال خود را وارد کنید:", placeholder="مثال: ساعات کاری شما چیست؟")

if user_query:
    st.info(f"شما پرسیدید: **{user_query}**")
    
    try:
        # Call the RAG pipeline with user's query
        with st.spinner("در حال جستجو و تولید پاسخ..."):
            answer, retrieved_context = \
                rag_pipeline(user_query, vectorstore, persian_prompt)
        
        st.success("پاسخ تولید شد:")
        st.write(f"**پاسخ:** {answer}")

        st.divider()

        # --- Display Retrieved Chunks ---
        st.subheader("تکه‌های بازیابی شده (Retrieved Chunks) 📚")
        if retrieved_context:
            for i, doc in enumerate(retrieved_context):
                with st.expander(f"تکه #{i+1} (ID: {doc.metadata.get('question_id', 'N/A')})"):
                    st.markdown(f"**محتوا:** {doc.page_content}")
                    st.markdown(f"**اطلاعات فراداده:** {json.dumps(doc.metadata, ensure_ascii=False, indent=2)}")
        else:
            st.warning("هیچ تکه‌ای برای این پرس و جو بازیابی نشد.")

    except Exception as e:
        st.error(f"خطایی رخ داد: {e}")
        st.warning("لطفاً مطمئن شوید که کلید API OpenAI شما تنظیم شده است و فایل JSON در مسیر صحیح قرار دارد.")

st.sidebar.header("درباره این برنامه")
st.sidebar.info(
    "این برنامه یک نمونه از سیستم RAG (بازیابی-تقویت-تولید) است که از سؤالات متداول (FAQ) شما استفاده می‌کند. "
    "با وارد کردن سؤال، سیستم ابتدا تکه‌های مرتبط را از پایگاه داده بازیابی کرده، سپس پاسخ را با کمک یک مدل زبان بزرگ (LLM) تولید می‌کند."
)