# 📘 Enhanced QA Agent with Source Tracing and Score Filtering

import streamlit as st
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

# --- Load environment variables ---
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# --- Validate API Key ---
if not openai_api_key:
    st.error("❌ OPENAI_API_KEY not loaded. Please check your .env file.")
    st.stop()

# --- Page Config ---
st.set_page_config(page_title="🤖 Ask AI Study Coach", layout="wide")
st.title("🤖 Ask your Study Coach")

# --- Initialize Services ---
try:
    client = QdrantClient(host="qdrant", port=6333)
    embedder = OpenAIEmbeddings(api_key=openai_api_key)
    llm = ChatOpenAI(api_key=openai_api_key, model="gpt-3.5-turbo", temperature=0)
except Exception as e:
    st.error(f"❌ Service initialization failed: {e}")
    st.stop()

# --- Search Function with Filtering ---
def semantic_search(query, top_k=10, min_score=0.75):
    try:
        query_vector = embedder.embed_query(query)
        results = client.search(
            collection_name="study_chunks",
            query_vector=query_vector,
            limit=top_k
        )
        # Filter by score threshold
        return [r for r in results if r.score >= min_score]
    except Exception as e:
        st.error(f"❌ Semantic search failed: {e}")
        return []

# --- Format Context for LLM ---
def format_context(results, max_chars=3000):
    context_blocks = []
    total_len = 0

    for r in results:
        chunk = r.payload.get("text", "")
        source = r.payload.get("source", "unknown")
        score = round(r.score, 3)

        block = f"--- Source: {source} | Score: {score} ---\n{chunk.strip()}"
        if total_len + len(block) > max_chars:
            break
        context_blocks.append(block)
        total_len += len(block)

    return "\n\n".join(context_blocks)

# --- Answer Generation ---
def generate_answer(query):
    results = semantic_search(query)
    if not results:
        return "No relevant content found in your uploaded files."

    context = format_context(results)
    messages = [
        SystemMessage(content="You are a helpful study assistant. Answer the question using only the provided context."),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {query}")
    ]

    try:
        response = llm(messages)
        return response.content
    except Exception as e:
        return f"❌ LLM generation failed: {e}"

# --- UI ---
query = st.text_input("Ask a question about your uploaded notes:")

if st.button("🧠 Get Answer") and query.strip():
    with st.spinner("Thinking..."):
        answer = generate_answer(query)
        st.markdown("### 📘 Answer:")
        st.success(answer)
