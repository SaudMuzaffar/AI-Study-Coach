# 📘 AI Study Coach – MVP README
Youtube demo @ https://www.youtube.com/watch?v=T-BnhxutV9w
## 🔥 Overview

AI Study Coach is a dockerized Streamlit-based SaaS app that allows students to upload notes (PDFs, images), extract text (including OCR), view and manage uploaded content, and later perform smart tasks like semantic search, quiz generation, and performance tracking — all based on their **own study material**.

This is **Module 1** of the full build process.

---

## ✅ Features (MVP Completed)

* Upload PDFs, PNG, JPG, JPEG files manually
* Extract text using **PyMuPDF** (PDF) and **Tesseract OCR** (images / scanned PDFs)
* Optional "🧠 Force OCR" mode for fully scanned books
* Auto-warns about slow OCR at upload time
* **Visual progress feedback** during long uploads and embedding
* Extracted `.txt` files and upload metadata stored in `uploads/`
* Automatically chunk, embed, and store into **Qdrant vector DB** on upload
* Preview extracted text instantly (up to 20,000 chars in UI)
* Browse uploaded files via **Uploaded Notes page**
* Delete notes from disk with one click
* Search uploaded files by filename
* Ask questions via **QA Agent** using semantic search and RAG
* Auto-generate custom multiple-choice quizzes from study material
* Track quiz score history with timestamp and file info
* Store and sync user preferences across pages (e.g., font size, top\_k)
* Clean **dark-themed** multi-page **Streamlit UI** with branding ("AI Study Coach by Saud Muzaffar")
* Fully Dockerized (runs via `docker-compose`)

---

## 📁 Folder Structure (MVP)

```
ai-study-coach/
├── dashboard/
│   ├── .streamlit/
│   ├── embeddings/
│   ├── pages/
│   │   ├── 1_Upload_Notes.py
│   │   ├── 2_QA_Agent.py
│   │   ├── 3_Quiz_Me.py
│   │   ├── 4_Quiz_History.py
│   │   └── 6_Settings.py
│   ├── Home.py
│   └── requirements.txt
├── uploads/
│   ├── raw_text/
│   ├── quiz_results.csv
│   └── upload_log.csv
├── .env
├── .gitignore
├── bfg.jar
├── docker-compose.yml
├── Dockerfile
├── ReadMe.md
├── setup.py
├── venv/
├── os/
└── sys/
```

---

## 🐳 Docker Setup

### Dockerfile

Make sure this exists in the root and looks like this:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY dashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard/ dashboard/
WORKDIR /app/dashboard

EXPOSE 8501

CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### docker-compose.yml

```yaml
version: '3.9'

services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - .:/app
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
```

---

## 🚀 How to Run (Local or Server)

```bash
# Build and run via Docker
cd ai-study-coach

docker-compose up --build
```

Visit: [http://localhost:8501](http://localhost:8501)

You’ll see:

* Home (upload page)
* Uploaded Notes (preview + delete)
* QA Agent (ask questions from uploaded content)

Sidebar is auto-collapsed for a clean layout.

---

## 🧠 Current Architecture

* LangChain used for chunking & embedding
* OpenAI for embeddings + LLM
* Qdrant as fast vector database
* RAG system: Top-k semantic results are retrieved → passed to GPT-3.5 → answer generated
* All processed automatically at upload time

---

## 🗭 Next Steps

* Final polish and performance optimizations
* Optional: deploy to cloud (Render, Hugging Face, etc.)
* Optional: add user authentication for multi-user SaaS
