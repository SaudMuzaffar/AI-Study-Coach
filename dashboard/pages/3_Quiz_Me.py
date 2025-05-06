# 3_Quiz_Me.py – Interactive MCQ Quiz with Custom Font Size

import streamlit as st
import os
import pandas as pd
import random
from embeddings.quiz_generator import generate_mcqs
from langchain.text_splitter import RecursiveCharacterTextSplitter
import csv
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="📝 Quiz Yourself", layout="wide")
st.title("📝 Quiz Yourself from Your Notes")

# --- Load upload log ---
log_path = "uploads/upload_log.csv"
if not os.path.exists(log_path):
    st.warning("No uploaded files found.")
    st.stop()

df = pd.read_csv(log_path)

# --- Deduplicate dropdown ---
dedup_df = df.drop_duplicates(subset=["filename"], keep="last")
file_options = sorted(dedup_df["filename"].tolist())

# --- Sidebar Controls ---
selected_file = st.sidebar.selectbox("📂 Choose a file", file_options)
num_questions = 10  # fixed
font_size = st.sidebar.slider("🔠 Font Size", 14, 26, 18)

# --- Load Text Content ---
selected_row = df[df["filename"] == selected_file].iloc[-1]
file_path = selected_row["text_file"]

if not os.path.exists(file_path):
    st.error("Text file not found.")
    st.stop()

with open(file_path, "r", encoding="utf-8") as f:
    full_text = f.read()

# --- Reset Quiz ---
if st.button("🔄 Start New Quiz"):
    st.session_state.quiz_started = False
    st.session_state.submitted = False
    st.session_state.responses = []
    st.session_state.quiz_data = []

# --- Init session state ---
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
    st.session_state.submitted = False
    st.session_state.responses = []
    st.session_state.quiz_data = []

# --- Generate quiz once ---
if not st.session_state.quiz_started:
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_text(full_text)
    selected_chunk = random.choice(chunks)

    with st.spinner("Generating quiz..."):
        raw_mcq = generate_mcqs(selected_chunk, num_questions)
        questions = raw_mcq.strip().split("\n\n")

        quiz_data = []
        for q in questions:
            lines = q.strip().split("\n")
            if len(lines) < 5:
                continue
            q_obj = {
                "question": lines[0],
                "options": lines[1:5],
                "answer": lines[5].split("Answer:")[1].strip()
            }
            quiz_data.append(q_obj)

        st.session_state.quiz_data = quiz_data
        st.session_state.quiz_started = True
        st.session_state.responses = [None] * len(quiz_data)

# --- Style Injection ---
st.markdown(f"""
<style>
/* Question text */
.quiz-question {{
    font-size: {font_size}px !important;
    font-weight: 600;
    margin-bottom: 8px;
}}

/* MCQ options (streamlit radio buttons) */
.css-1c7y2kd div[data-baseweb="radio"] label span {{
    font-size: {font_size - 2}px !important;
}}
</style>
""", unsafe_allow_html=True)


# --- Display Quiz ---
if st.session_state.quiz_started:
    st.subheader("🧠 Your Quiz")

    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown(f"<div class='quiz-question'>{q['question']}</div>", unsafe_allow_html=True)
        user_choice = st.radio(
            f"Choose for Q{i+1}",
            q["options"],
            key=f"q{i}",
            index=None,
            label_visibility="collapsed"
        )
        st.session_state.responses[i] = user_choice

    if st.button("✅ Submit Answers"):
        st.session_state.submitted = True

# --- Show Results ---
if st.session_state.get("submitted", False):
    score = 0
    st.markdown("---")
    st.subheader("📊 Results")

    for i, q in enumerate(st.session_state.quiz_data):
        user_ans = st.session_state.responses[i]
        correct_ans = q["answer"]
        st.markdown(f"<div class='quiz-question'>Q{i+1}. {q['question']}</div>", unsafe_allow_html=True)
        if user_ans is None:
            st.warning("No answer selected.")
        elif user_ans.startswith(correct_ans):
            st.success(f"✅ Correct: {user_ans}")
            score += 1
        else:
            st.error(f"❌ Your Answer: {user_ans} | ✅ Correct: {correct_ans}")
        st.markdown("---")

    st.success(f"🏁 Final Score: {score} / {len(st.session_state.quiz_data)}")

    # ✅ Logging should be inside this block
    history_path = "uploads/quiz_results.csv"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = selected_file
    total_q = len(st.session_state.quiz_data)
    correct_qs = []
    incorrect_qs = []

    for i, q in enumerate(st.session_state.quiz_data):
        user_ans = st.session_state.responses[i]
        correct_ans = q["answer"]
        if user_ans and user_ans.startswith(correct_ans):
            correct_qs.append(f"Q{i+1}")
        else:
            incorrect_qs.append(f"Q{i+1}")

    if not os.path.exists(history_path):
        with open(history_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "filename", "score", "total_questions", "correct_answers", "incorrect_answers"])

    with open(history_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            timestamp,
            filename,
            score,
            total_q,
            ",".join(correct_qs),
            ",".join(incorrect_qs)
        ])