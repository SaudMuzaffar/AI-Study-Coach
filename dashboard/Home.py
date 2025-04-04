import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from datetime import datetime
import os
import pandas as pd

# Page config
st.set_page_config(
    page_title="AI Study Coach – Upload Center",
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
    .stFileUploader, .stDownloadButton, .stTextInput {
        font-size: 1.1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("## 📘 AI Study Coach")
st.markdown("#### by *Saud Muzaffar*")
st.markdown("---")
st.markdown("### 🚀 Upload your notes and let AI do the studying!")

# File uploader (PDF + Images)
uploaded_file = st.file_uploader(
    "📄 Drop a PDF or image file (PNG, JPG, JPEG) below",
    type=["pdf", "png", "jpg", "jpeg"]
)

# Extract text from PDF (with OCR fallback)
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    full_text = ""

    for page in doc:
        text = page.get_text()
        full_text += text

        if not text.strip():
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            ocr_text = pytesseract.image_to_string(img)
            full_text += "\n\n" + ocr_text

    return full_text

# Extract text from an image using OCR
def extract_text_from_image(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return text

# Handle file
if uploaded_file:
    file_type = uploaded_file.type

    st.success(f"✅ Uploaded: `{uploaded_file.name}` on {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Determine extraction method
    if file_type == "application/pdf":
        extracted_text = extract_text_from_pdf(uploaded_file)
    elif file_type.startswith("image/"):
        extracted_text = extract_text_from_image(uploaded_file)
    else:
        st.error("Unsupported file type.")
        st.stop()

    # Preview extracted text
    st.markdown("### 🧾 Preview Extracted Text")
    st.text_area("Scroll through your extracted notes below:", extracted_text[:5000], height=500)

    # Download text
    st.download_button(
        label="💾 Download Extracted Text",
        data=extracted_text,
        file_name=uploaded_file.name.rsplit(".", 1)[0] + ".txt",
        mime="text/plain"
    )

    # Save and log
    os.makedirs("uploads/raw_text", exist_ok=True)
    filename = uploaded_file.name.rsplit(".", 1)[0] + ".txt"
    filepath = os.path.join("uploads/raw_text", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    log_path = "uploads/upload_log.csv"
    log_entry = {
        "filename": filename,
        "original_file": uploaded_file.name,
        "upload_time": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "text_file": filepath
    }

    if os.path.exists(log_path):
        df = pd.read_csv(log_path)
        df = pd.concat([df, pd.DataFrame([log_entry])], ignore_index=True)
    else:
        df = pd.DataFrame([log_entry])
    df.to_csv(log_path, index=False)
