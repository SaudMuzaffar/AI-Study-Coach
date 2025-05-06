import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from embeddings.embed_utils import embed_and_store

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Study Coach – Uploaded Notes",
    page_icon="📘",
    layout="wide"
)

# Styling
st.markdown("""
    <style>
    body {
        background-color: #0d1117;
        color: white;
    }
    .main {
        padding: 2rem 5rem;
    }
    h1 {
        font-size: 3rem;
        color: #58a6ff;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    h4 {
        text-align: center;
        font-size: 1.3rem;
        color: #8b949e;
        margin-top: 0;
    }
    .stTextArea textarea {
        font-size: 1.1rem !important;
        line-height: 1.6;
        background-color: #161b22;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("## 📘 AI Study Coach")
st.markdown("#### by *Saud Muzaffar*")
st.markdown("---")
st.markdown("### 📂 Previously Uploaded Notes")

# Load upload log
log_path = "uploads/upload_log.csv"
if not os.path.exists(log_path):
    st.warning("No uploaded notes found.")
    st.stop()

df = pd.read_csv(log_path)

# --- Deduplicate dropdown options (keep latest entries only) ---
dedup_df = df.drop_duplicates(subset=["filename"], keep="last")

# --- Search box ---
search_term = st.text_input("🔍 Search by filename (case-insensitive):")
filtered_df = dedup_df[dedup_df["filename"].str.contains(search_term, case=False, na=False)]

# --- File selection ---
if not filtered_df.empty:
    selected_file = st.selectbox("Select a file to preview", filtered_df["filename"].tolist())
    selected_row = df[df["filename"] == selected_file].iloc[-1]  # get latest matching row
    file_path = selected_row["text_file"]

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Preview logic
        max_preview_chars = 20000
        if len(text) > max_preview_chars:
            st.warning("⚠️ Only the first 20,000 characters are shown below. The full text is saved and embedded.")

        st.text_area(
            "📟 Extracted Text Preview",
            text[:max_preview_chars],
            height=600
        )

        st.info("📌 This file was already embedded at upload time.")

        # Delete option
        if st.button("🗑️ Delete this file"):
            try:
                os.remove(file_path)
                df = df.drop(selected_row.name)  # only delete that specific row
                df.to_csv(log_path, index=False)
                st.success(f"✅ Deleted '{selected_file}' successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error deleting file: {e}")
    else:
        st.warning("⚠️ Text file not found.")
else:
    st.warning("No matching files found.")
