# 📘 AI Study Coach – MVP README

## 🔥 Overview
AI Study Coach is a dockerized Streamlit-based SaaS app that allows students to upload notes (PDFs, images), extract text (including OCR), view and manage uploaded content, and later perform smart tasks like semantic search, quiz generation, and performance tracking — all based on their **own study material**.

This is **Module 1** of the full build process.

---

## ✅ Features (Module 1 Completed)

- Upload PDFs, PNG, JPG, JPEG files manually
- Extract text using **PyMuPDF** (PDF) and **Tesseract OCR** (images / scanned PDFs)
- Save extracted `.txt` files and metadata to disk
- Browse uploaded files via **Uploaded Notes page**
- Delete notes from disk with one click
- Search uploaded files by filename
- Clean **dark-themed** multi-page **Streamlit UI** with branding ("AI Study Coach by Saud Muzaffar")
- Fully Dockerized (runs via `docker-compose`)

---

## 📁 Folder Structure (MVP)

```
ai-study-coach/
├── dashboard/
│   ├── Home.py                  # Upload center
│   ├── pages/
│   │   └── Uploaded_Notes.py   # Browse/delete notes
│   ├── .streamlit/
│   │   └── config.toml         # Theme + sidebar behavior
│   └── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
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
- Home (upload page)
- Uploaded Notes (preview + delete)

Sidebar is auto-collapsed for a clean layout.

---

## 🧭 Next Module: Embedding + Vector Search

In the next phase, we will:
- Chunk extracted text using LangChain
- Embed using OpenAI or HuggingFace models
- Store in ChromaDB or Qdrant
- Enable semantic search + smart Q&A

Stay tuned! 🚀

