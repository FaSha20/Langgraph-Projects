import os
import json
import re
from typing import List, Dict, Tuple
from datetime import datetime

from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import ChatOpenAI
# from langchain.chains import create_qa_chain
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv 

# --- Configuration ---
# Set your OpenAI API key
load_dotenv(override=True)

# Model and embedding settings
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 50
VECTOR_DB_PATH = "F:\\Fatemeh\\web-backend\\FatemehLocal\\RagAgent\\VDB\\chroma_db_faq"
GENERATION_MODEL_NAME = "gpt-4o-mini"
K_QUESTIONS_INDEX = 3
K_PER_FAQ_STAGE = 5

# Output file configuration
OUTPUT_FILE_NAME = "F:\\Fatemeh\\web-backend\\FatemehLocal\\RagAgent\\rag_output.txt"


# --- 1. Data Loading and Chunking (Adapted for JSON) ---
def load_and_chunk_json_faqs(json_file_path: str) -> List[Document]:
    """Loads FAQ data from a JSON file and splits it into chunks with metadata."""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        faq_data = json.load(f)

    documents = []
    for i, entry in enumerate(faq_data):
        question = entry.get("question", "")
        answer = entry.get("answer", "")
        
        combined_content = f"Question: {question}\nAnswer: {answer}"
        
        metadata = {
            "question_id": f"faq_entry_{i}",
            "original_question": question,
            "language": "fa"
        }
        documents.append(Document(page_content=combined_content, metadata=metadata))

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True,
    )
    
    chunks = text_splitter.split_documents(documents)
    return chunks

# --- 2. Embedding Model and Vector Database ---
def setup_vector_store(chunks: List[Document], embedding_model_name: str, db_path: str):
    """Sets up ChromaDB with the given chunks and embedding model."""
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
    
    # Check if vector store already exists and load it if it does
    if os.path.exists(db_path):
        print(f"Loading existing vector store from {db_path}...")
        vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)
    else:
        print(f"Creating new vector store at {db_path}...")
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=db_path
        )
        # vectorstore.persist() # Persist only if newly created
    return vectorstore, embeddings

# --- 3. Retriever Setup (Similarity + MMR) ---
def setup_retriever(vectorstore):
    """Sets up a retriever with similarity and MMR for diversity."""
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    mmr_retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": K_QUESTIONS_INDEX})
    return base_retriever, mmr_retriever

# --- 4. Hybrid Search (Conceptual for Chroma/Dev) ---
def bm25_rerank(query: str, documents: List[Document], top_n: int = 3) -> List[Document]:
    """
    A conceptual BM25 re-ranking function.
    """
    scored_docs = []
    query_terms = set(query.lower().split())

    for doc in documents:
        doc_content = doc.page_content.lower()
        score = sum(1 for term in query_terms if term in doc_content)
        scored_docs.append((score, doc))

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored_docs[:top_n]]

# --- 5. Prompt/Template Design ---
def create_persian_prompt_template():
    """Creates a few-shot prompt template for the LLM in Persian."""
    system_instruction = (
        "شما یک دستیار هوش مصنوعی هستید که به سؤالات بر اساس اطلاعات متن ارائه شده پاسخ می دهید. "
        " 'اگر پاسخ از متن قابل استخراج نیست، بگویید 'من نمی توانم پاسخ این سوال را بر اساس اطلاعات ارائه شده پیدا کنم.' "
        "سپس تلاش کنید بهترین حدسی که برای جواب دارید را ارائه دهید."
        "همیشه به زبان فارسی و مختصر پاسخ دهید."
    )

    template = (
        f"{system_instruction}\n\n"
        "متن سوال و پاسخ های مرتبط به شما داده شده است.تلاش کنیداز اطلاعات داده شده برای پاسخ استفاده کنید.\n\n"
        "Context: {context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )
    return PromptTemplate(template=template, input_variables=["context", "question"])

# --- RAG Orchestration ---
def rag_pipeline(query: str, vectorstore, prompt_template):
    """
    Orchestrates the RAG pipeline.
    """
    initial_retrieved_docs = vectorstore.similarity_search(query, k=K_QUESTIONS_INDEX)
    unique_question_ids = list(set(doc.metadata.get("question_id") for doc in initial_retrieved_docs if "question_id" in doc.metadata))

    final_context_docs = []
    for q_id in unique_question_ids:
        all_chunks_for_q_id = vectorstore.similarity_search(
            query=query,
            k=20, # Generous k to ensure all chunks of one FAQ are covered if split
            filter={"question_id": q_id}
        )
        final_context_docs.extend(all_chunks_for_q_id)

    unique_final_context_docs = []
    seen_hashes = set() # Use hash of page_content to deduplicate
    for doc in final_context_docs:
        doc_hash = hash(doc.page_content + str(doc.metadata))
        if doc_hash not in seen_hashes:
            unique_final_context_docs.append(doc)
            seen_hashes.add(doc_hash)
    
    # Apply BM25 re-ranking
    reranked_docs = bm25_rerank(query, unique_final_context_docs, top_n=K_PER_FAQ_STAGE * len(unique_question_ids))
    
    if reranked_docs == unique_final_context_docs:
        print("NOT CHANGED")
    else:
        print("CHANGED")
        print(unique_final_context_docs)
        
    context_text = "\n\n".join([doc.page_content for doc in reranked_docs])
    # print(context_text)

    llm = ChatOpenAI(model_name=GENERATION_MODEL_NAME, temperature=0.0)

    rag_chain = (
        {"context": lambda x: context_text, "question": RunnablePassthrough()}
        | prompt_template
        | llm
        | StrOutputParser()
    )

    return rag_chain.invoke(query), reranked_docs

# --- File Writing Function ---
def write_rag_output_to_file(query: str, answer: str, retrieved_context: List[Document], config: Dict, file_name: str):
    """Writes RAG output and configuration to a specified file."""
    with open(file_name, 'a', encoding='utf-8') as f: # Use 'a' for append mode
        f.write(f"--- RAG Output - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        f.write(f"Query: {query}\n\n")
        
        f.write("RAG Answer:\n")
        f.write(f"{answer}\n\n")
        
        f.write("Retrieved Context:\n")
        for i, doc in enumerate(retrieved_context):
            f.write(f"  Chunk {i+1}:\n")
            f.write(f"    Content: {doc.page_content}\n")
            f.write(f"    Metadata: {json.dumps(doc.metadata, ensure_ascii=False, indent=2)}\n")
        f.write("\n")

        f.write("Current RAG Configuration:\n")
        for key, value in config.items():
            f.write(f"  {key}: {value}\n")
        f.write("\n" + "="*80 + "\n\n")


if __name__ == "__main__":
    
    # To clear vector DB for a fresh start, uncomment the line below:
    # import shutil
    # if os.path.exists(VECTOR_DB_PATH):
    #     shutil.rmtree(VECTOR_DB_PATH)
    # print("Vector database persists unless manually deleted.")

    json_file_name = "F:\\Fatemeh\\web-backend\\FatemehLocal\\RagAgent\\dobare_faqs.json"
    print("Loading and chunking JSON FAQ documents...")
    documents = load_and_chunk_json_faqs(json_file_name)
    print(f"Generated {len(documents)} chunks from JSON data.")
 
    # 2. Setup Vector Store
    # This part now checks if the vector store exists and loads it
    # This prevents re-embedding on every run unless the folder is manually deleted.
    vectorstore, embeddings = setup_vector_store(documents, EMBEDDING_MODEL_NAME, VECTOR_DB_PATH)
    print("Vector store ready.")

    # # 3. Setup Retriever (embeddings not directly used here in this orchestrator, but required by setup_vector_store)
    base_retriever, mmr_retriever = setup_retriever(vectorstore)
    print("Retriever set up.")

    # # 4. Create Prompt Template
    persian_prompt = create_persian_prompt_template()
    print("Prompt template created.")

    # # --- RAG Configuration to log ---
    rag_config = {
        "EMBEDDING_MODEL_NAME": EMBEDDING_MODEL_NAME,
        "CHUNK_SIZE": CHUNK_SIZE,
        "CHUNK_OVERLAP": CHUNK_OVERLAP,
        "VECTOR_DB_PATH": VECTOR_DB_PATH,
        "GENERATION_MODEL_NAME": GENERATION_MODEL_NAME,
        "K_QUESTIONS_INDEX": K_QUESTIONS_INDEX,
        "K_PER_FAQ_STAGE": K_PER_FAQ_STAGE,
        "Output_File": OUTPUT_FILE_NAME
    }

    # # 5. Run RAG Pipeline and write to file
    queries_to_test = [
        "دوباره چطور مشتریان را به خرید مجدد ترغیب می کند؟",
        "دوباره برای کسب و کار ها با کدام چرخه خرید نرخ بازگشت سرمایه بالاتری خواهد داشت؟",
        'دوباره با قانون تجارت الکترونیک ایران سازگاره؟',
        "دوباره معادل کمپین تبلیغاتی است؟"
    ]

    for query in queries_to_test[3:]:
        print(f"\nProcessing Query: {query}")
        answer, retrieved_context = rag_pipeline(query, vectorstore, persian_prompt)
        write_rag_output_to_file(query, answer, retrieved_context, rag_config, OUTPUT_FILE_NAME)
        print(f"Output for query '{query}' written to {OUTPUT_FILE_NAME}")

    print("\nProcessing complete. Check 'rag_output.txt' for results.")