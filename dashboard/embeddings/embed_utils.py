# --- embed_utils.py ---

# Import needed libraries
import os
import uuid
import re
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize embedding model
embedder = OpenAIEmbeddings(api_key=openai_api_key)

# Initialize Qdrant client (default to Docker setup)
qdrant = QdrantClient(host="qdrant", port=6333)
collection_name = "study_chunks"

# Ensure the collection exists in Qdrant
if not qdrant.collection_exists(collection_name=collection_name):
    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )

def extract_section_title(text):
    """
    Attempts to extract a section heading using heuristics like:
    - Numbered headings (e.g. 5.1 Introduction)
    - Markdown headings (## Title)
    """
    lines = text.strip().splitlines()
    for line in lines:
        if re.match(r"^(\d+[\.:])?\s*[A-Z].{3,}$", line.strip()):
            return line.strip()
    return None

def embed_and_store(text, metadata=None, batch_size=50):
    """
    Chunks the text, embeds in batches, and stores to Qdrant.
    Adds page number, title, and source to chunk metadata.
    """
    # Split with overlap for better RAG continuity
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    # Split into chunks
    chunks = splitter.split_text(text)
    total_chunks = len(chunks)
    all_points = []

    # Process in batches
    for i in range(0, total_chunks, batch_size):
        batch = chunks[i:i + batch_size]

        # Try embedding the batch
        try:
            vectors = embedder.embed_documents(batch)
        except Exception as e:
            print(f"[⚠️ Embedding Failed] Batch {i//batch_size + 1}: {e}")
            continue

        # Generate metadata-rich PointStructs
        for chunk, vector in zip(batch, vectors):
            point_metadata = {
                "text": chunk,
                "source": metadata.get("source", "unknown") if metadata else "unknown",
                "chunk_title": extract_section_title(chunk),
                "page_hint": chunk[:20]  # rough indication for UI
            }

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=point_metadata
            )
            all_points.append(point)

        # Upload batch to Qdrant
        try:
            qdrant.upsert(collection_name=collection_name, points=all_points[-len(batch):])
        except Exception as e:
            print(f"[❌ Qdrant Upsert Failed] Batch {i//batch_size + 1}: {e}")

    return len(all_points)
