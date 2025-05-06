# 2_QA_Agent.py – Chat-style RAG Agent

import streamlit as st
from dotenv import load_dotenv
from embeddings.rag_agent import chat_with_rag  # ✅ Our upgraded chat RAG
import os

# --- Load environment variables ---
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

# --- Page Setup ---
st.set_page_config(page_title="💬 Chat with AI Study Coach", layout="wide")
st.title("💬 Chat with Your Study Coach")

# --- Initialize message history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar controls ---
st.sidebar.title("Settings")
top_k = st.sidebar.slider("🔍 Number of context chunks", min_value=2, max_value=10, value=5)

# --- Display past conversation ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat input box ---
user_input = st.chat_input("Ask a question based on your uploaded notes...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build history format: list of (user, assistant) turns
    history = []
    for i in range(0, len(st.session_state.messages) - 1, 2):
        if st.session_state.messages[i]["role"] == "user" and st.session_state.messages[i + 1]["role"] == "assistant":
            history.append((st.session_state.messages[i]["content"], st.session_state.messages[i + 1]["content"]))

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_with_rag(user_input, chat_history=history, top_k=top_k)
            st.markdown(response)

    # Save assistant reply to state
    st.session_state.messages.append({"role": "assistant", "content": response})
