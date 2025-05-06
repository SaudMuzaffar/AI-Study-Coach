# 6_Settings.py – App Settings & Personalization

import streamlit as st

st.set_page_config(page_title="⚙️ Settings", layout="wide")
st.title("⚙️ AI Study Coach – Settings & Preferences")

st.markdown("Customize how your assistant behaves across pages.")

# --- Font Size Control ---
font = st.slider("🖋️ Default Font Size for Questions", min_value=12, max_value=26, value=18)

# --- Top-K Control for RAG ---
top_k = st.slider("🔍 Default Number of Context Chunks (for Q&A)", min_value=2, max_value=10, value=5)

# --- Reset session state ---
if st.button("♻️ Clear All Session State"):
    st.session_state.clear()
    st.success("✅ Session state cleared.")

# --- Save to session state for other pages to use ---
st.session_state.default_font_size = font
st.session_state.default_top_k = top_k
