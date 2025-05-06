# 4_Quiz_History.py – Enhanced Quiz History Viewer

import streamlit as st
import pandas as pd
import os
from io import StringIO
from datetime import datetime

# --- Page Setup ---
st.set_page_config(page_title="📊 Quiz History", layout="wide")
st.title("📊 Quiz History Log")

# --- File Path ---
history_path = "uploads/quiz_results.csv"

# --- Load Data ---
if not os.path.exists(history_path):
    st.warning("No quiz history found. Take a quiz to start logging results.")
    st.stop()

df = pd.read_csv(history_path)

# --- Preprocessing ---
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp", ascending=False)

# --- Sidebar Filters ---
st.sidebar.header("📌 Filter Quiz History")

# Filter by file
file_filter = st.sidebar.selectbox("Filter by File", ["All"] + sorted(df["filename"].unique().tolist()))
if file_filter != "All":
    df = df[df["filename"] == file_filter]

# Filter by score
min_score, max_score = int(df["score"].min()), int(df["score"].max())
score_range = st.sidebar.slider("Score Range", min_score, max_score, (min_score, max_score))
df = df[(df["score"] >= score_range[0]) & (df["score"] <= score_range[1])]

# Filter by date
min_date, max_date = df["timestamp"].min().date(), df["timestamp"].max().date()
selected_date = st.sidebar.date_input("Show records from", value=min_date, min_value=min_date, max_value=max_date)
df = df[df["timestamp"].dt.date >= selected_date]

# --- Clear Log Button ---
if st.sidebar.button("🗑️ Clear Entire History"):
    confirm = st.sidebar.checkbox("Confirm Delete")
    if confirm:
        os.remove(history_path)
        st.success("✅ Quiz history log cleared.")
        st.experimental_rerun()

# --- Main Table View ---
st.markdown("### 📄 Filtered Quiz Attempts")

if df.empty:
    st.info("No records found for selected filters.")
    st.stop()

# Display with expandable details
for idx, row in df.iterrows():
    with st.expander(f"📌 {row['timestamp']} — {row['filename']} — Score: {row['score']}/{row['total_questions']}"):
        st.markdown(f"**Correct Answers:** {row['correct_answers'] or '—'}")
        st.markdown(f"**Incorrect Answers:** {row['incorrect_answers'] or '—'}")

# --- Download CSV ---
csv_buffer = StringIO()
df.to_csv(csv_buffer, index=False)
st.download_button(
    label="⬇️ Download Filtered Results as CSV",
    data=csv_buffer.getvalue(),
    file_name="filtered_quiz_history.csv",
    mime="text/csv"
)
