# FAQ RAG Assistant 🤖

This project implements a Retrieval Augmented Generation (RAG) system designed to answer user queries based on a predefined set of Frequently Asked Questions (FAQs). It leverages a vector database for efficient retrieval of relevant information and a Large Language Model (LLM) for generating concise and accurate answers in Persian.

-----

## Features ✨

  * **Multilingual Embeddings:** Utilizes `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` for robust multilingual (including Persian) document embedding.
  * **Intelligent Chunking:** Splits FAQ content into optimized chunks (approx. 1500 characters with 50 character overlap) to maintain semantic precision and context.
  * **Persistent Vector Database:** Uses ChromaDB for development, allowing for efficient storage and retrieval of document embeddings without re-processing on every run.
  * **Two-Stage Retrieval with Metadata Filtering:**
      * **Stage 1:** Retrieves initial relevant FAQ entries based on semantic similarity.
      * **Stage 2:** Filters by `question_id` to retrieve all associated chunks for selected FAQ entries, ensuring comprehensive context for the LLM.
  * **Conceptual Reranking (BM25):** Includes a conceptual BM25 reranker to boost keyword-exact matches within the retrieved documents, improving precision. The system also tracks and reports if the reranker changed the order of retrieved documents.
  * **LLM-Powered Generation:** Employs `gpt-4o-mini` to generate answers based on the retrieved context and a specifically designed Persian prompt.
  * **Streamlit User Interface:** Provides a simple and interactive web application for users to submit queries and view results.
  * **Detailed Logging:** Outputs RAG answers, retrieved context, and reranker status to a file for analysis and debugging.

-----

## Project Structure 📁

```
.
├── RAGapp.py               # Main Streamlit application
├── ragAgent.py             # RAG logic
├── dobare_faqs.json        # Your actual FAQ JSON file (path configured in rag_app.py)
├── chroma_db_faq/          # Persistent directory for ChromaDB (created on first run)
└── rag_output.txt          # Log file for RAG query outputs and configuration
```

-----

## Setup and Installation 🛠️

1.  **Clone the repository (or save the code):**
    Save the provided Python code into a file named `rag_app.py`.

2.  **Install Dependencies:**
    Open your terminal or command prompt and run the following command to install all necessary Python packages:

    ```bash
    pip install streamlit langchain-community langchain-openai langchain-huggingface langchain-chroma sentence-transformers tiktoken pandas
    ```

3.  **Prepare your FAQ Data:**

      * Create a JSON file with your FAQ data in the format `[{"question": "...", "answer": "..."}, ...]`.
      * **Place this file at the path specified in `rag_app.py`:**
        `json_file_path = r"F:\Fatemeh\web-backend\FatemehLocal\RagAgent\dobare_faqs.json"`
        Make sure the file name and exact path match this configuration. A dummy `faqs.json` will be created if `faqs.json` does not exist in the same directory as `rag_app.py` for initial testing.

4.  **Set OpenAI API Key:**
    The application requires an OpenAI API key for the LLM. It's recommended to set this as an environment variable:

    ```bash
    export OPENAI_API_KEY="your_openai_api_key_here" # For Linux/macOS
    set OPENAI_API_KEY="your_openai_api_key_here"    # For Windows
    ```

    Alternatively, you can hardcode it directly in `rag_app.py` (line `os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"`) but this is less secure for production.

-----

## Usage ▶️

1.  **Run the Streamlit Application:**
    Navigate to the directory containing `rag_app.py` in your terminal and execute:
    ```bash
    streamlit run rag_app.py
    ```
2.  **Interact with the App:**
    Your web browser will automatically open the Streamlit application.
      * Enter your query in Persian into the text input field.
      * Press Enter or click outside the text box to submit the query.
      * The application will display the generated answer, the retrieved document chunks, and information about the reranker's impact.
      * The RAG process details (query, answer, retrieved context, reranker status, and configuration) will also be logged to `rag_output.txt` in the project directory.

-----

## Customization and Improvement ⚙️

  * **FAQ Data:** Update `dobare_faqs.json` with your actual FAQ content.
  * **Embedding Model:** Experiment with different multilingual `sentence-transformers` models on Hugging Face for potentially better performance or specific language needs.
  * **Chunking Strategy:** Adjust `CHUNK_SIZE` and `CHUNK_OVERLAP` in `rag_app.py` to optimize context for your specific document structure.
  * **Vector Database:** For production, consider Qdrant for its advanced features like hybrid search and filtering at scale. This would require updating the `setup_vector_store` and retrieval logic.
  * **Reranker:**
      * Implement more sophisticated rerankers (e.g., Cross-Encoder models) for higher precision.
      * Refine the conceptual BM25 re-ranking by integrating a dedicated library like `rank_bm25` for more accurate keyword scoring.
      * Explore LlamaIndex's built-in reranking modules (CohereRerank, LLMRerank, RRF) for more advanced reranking capabilities.
  * **LLM:** Upgrade to `gpt-4` for higher accuracy and deeper reasoning, if cost permits.
  * **Prompt Engineering:** Fine-tune the `create_persian_prompt_template()` for better answer quality and adherence to specific response formats.

-----

## Troubleshooting ❓

  * **`ModuleNotFoundError` / `ImportError`:** Ensure all dependencies are installed correctly using `pip install -U ...`. Pay attention to LangChain's modularized imports (`langchain_huggingface`, `langchain_chroma`).
  * **`TypeError: ... got multiple values for keyword argument 'where'`:** This means your `similarity_search` call is incorrect. Ensure you're passing the actual semantic `query` string as the `query` argument, and your metadata filter in the `where` parameter.
  * **`Not enough values to unpack`:** Verify that the `rag_pipeline` function's `return` statement explicitly returns all 5 expected values (`answer`, `retrieved_docs`, `reranker_changed_order`, `pre_rerank_order_summary`, `post_rerank_order_summary`).
  * **API Key Issues:** Check if your `OPENAI_API_KEY` is correctly set as an environment variable or directly in the script.
  * **File Not Found:** Double-check the `json_file_path` in `rag_app.py` to ensure it points to the exact location of your `dobare_faqs.json` file.
  * **ChromaDB Persistence:** If you want to force a fresh rebuild of the vector database, delete the `chroma_db_faq` folder. Otherwise, the app will load the existing database.