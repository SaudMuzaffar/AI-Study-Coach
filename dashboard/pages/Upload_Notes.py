import streamlit as st
import pandas as pd
import os

# --- Page Config ---
st.set_page_config(
    page_title="AI Study Coach – Uploaded Notes",
    page_icon="📘",
    layout="wide"
)

# --- Custom Styling (same as Home.py) ---
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

# --- Header ---
st.markdown("## 📘 AI Study Coach")
st.markdown("#### by *Saud Muzaffar*")
st.markdown("---")
st.markdown("### 📂 Previously Uploaded Notes")

# --- Load upload log ---
log_path = "uploads/upload_log.csv"
if not os.path.exists(log_path):
    st.warning("No uploaded notes found.")
    st.stop()

df = pd.read_csv(log_path)

# --- Search Box ---
search_term = st.text_input("🔍 Search by filename (case-insensitive):")
filtered_df = df[df["filename"].str.contains(search_term, case=False, na=False)]

# --- File Selection Dropdown ---
if not filtered_df.empty:
    selected_file = st.selectbox("Select a file to preview", filtered_df["filename"].tolist())
    file_path = filtered_df[filtered_df["filename"] == selected_file]["text_file"].values[0]

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        st.text_area("🧾 Extracted Text", text[:10000], height=500)
    else:
        st.warning("Text file not found.")

    # --- Delete Option ---
    if st.button("🗑️ Delete this file"):
        try:
            # Remove the .txt file
            os.remove(file_path)
            # Remove from CSV
            df = df[df["filename"] != selected_file]
            df.to_csv(log_path, index=False)
            st.success(f"Deleted '{selected_file}' successfully.")
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting file: {e}")
else:
    st.warning("No matching files found.")
