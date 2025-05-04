import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from datetime import datetime
import os
import pandas as pd
from embeddings.embed_utils import embed_and_store

# --- Streamlit page setup ---
st.set_page_config(
    page_title="AI Study Coach – Upload Center",
    page_icon="📘",
    layout="wide"
)

# --- Styling ---
st.markdown("""
    <style>
    body { background-color: #0d1117; color: white; }
    .main { padding: 2rem 5rem; }
    h1 { font-size: 3rem; color: #58a6ff; text-align: center; }
    h4 { text-align: center; font-size: 1.3rem; color: #8b949e; }
    .stTextArea textarea {
        font-size: 1.1rem !important; line-height: 1.6;
        background-color: #161b22; color: white;
    }
    .stFileUploader, .stDownloadButton, .stTextInput {
        font-size: 1.1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("## 📘 AI Study Coach")
st.markdown("#### by *Saud Muzaffar*")
st.markdown("---")
st.markdown("### 🚀 Upload your notes and let AI do the studying!")

# --- Upload ---
uploaded_file = st.file_uploader(
    "📄 Drop a PDF or image file (PNG, JPG, JPEG) below",
    type=["pdf", "png", "jpg", "jpeg"]
)

# --- PDF extraction function ---
def extract_text_from_pdf(file, force_ocr=False):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    full_text = ""

    with st.spinner("🔍 Extracting text from PDF..."):
        for page_num, page in enumerate(doc):
            text = page.get_text()

            if force_ocr or not text.strip():
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_bytes))
                text = pytesseract.image_to_string(img)

            full_text += f"\n\n--- Page {page_num + 1} ---\n\n{text}"

    return full_text

# --- Image extraction function ---
def extract_text_from_image(file):
    with st.spinner("🧠 Running OCR on image..."):
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
    return text

# --- Main logic ---
if uploaded_file:
    file_type = uploaded_file.type
    st.success(f"✅ Uploaded: `{uploaded_file.name}` on {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Optional OCR toggle
    force_ocr = st.checkbox("🧠 Force OCR for all pages (for scanned books)", value=False)
    if force_ocr:
        st.warning("⚠️ OCR can be very slow on large files. Please be patient...")

    # Extract text
    if file_type == "application/pdf":
        extracted_text = extract_text_from_pdf(uploaded_file, force_ocr=force_ocr)
    elif file_type.startswith("image/"):
        extracted_text = extract_text_from_image(uploaded_file)
    else:
        st.error("❌ Unsupported file type.")
        st.stop()

    # Preview and log
    st.info(f"📄 Extracted {len(extracted_text)} characters from the uploaded file.")
    st.markdown("### 🧾 Preview Extracted Text")
    st.text_area("Scroll through your extracted notes below:", extracted_text[:5000], height=500)

    # Download button
    st.download_button(
        label="💾 Download Extracted Text",
        data=extracted_text,
        file_name=uploaded_file.name.rsplit(".", 1)[0] + ".txt",
        mime="text/plain"
    )

    # Save .txt
    os.makedirs("uploads/raw_text", exist_ok=True)
    filename = uploaded_file.name.rsplit(".", 1)[0] + ".txt"
    filepath = os.path.join("uploads/raw_text", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    # Log to CSV
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

    # --- Embed & store (problem 1 fix: immediate after upload) ---
    with st.spinner("📦 Embedding and uploading chunks to Qdrant..."):
        chunks = embed_and_store(extracted_text, metadata={"source": filename})
        st.success(f"✅ Successfully embedded and stored {chunks} chunks into Qdrant.")
