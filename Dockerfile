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
