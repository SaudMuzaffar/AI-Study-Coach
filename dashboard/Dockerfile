# Use slim Python 3.10 as base
FROM python:3.10-slim

# Set working directory in container
WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the full dashboard app code
COPY . /app

# Set PYTHONPATH to recognize local modules
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Run Streamlit app
CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
