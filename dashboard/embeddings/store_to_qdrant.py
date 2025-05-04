from dotenv import load_dotenv
load_dotenv()

import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# ✅ Sample text to embed
sample_text = """
Newton's First Law of Motion states that an object at rest will remain at rest, and an object in motion will continue in motion at a constant velocity unless acted upon by a net external force.
This is also known as the law of inertia. The greater the mass of an object, the more it resists changes to its state of motion.
"""

# 🔨 Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=40)
chunks = splitter.split_text(sample_text)

# 🧠 Embed chunks
embedder = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
vectors = embedder.embed_documents(chunks)

# 🔌 Connect to Qdrant
client = QdrantClient(host="localhost", port=6333)

# 🏗️ Create collection if not exists
client.recreate_collection(
    collection_name="study_chunks",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)

# 🧱 Store embeddings + metadata
points = [
    PointStruct(
        id=i,
        vector=vectors[i],
        payload={
            "text": chunks[i],
            "chunk_id": i
        }
    )
    for i in range(len(vectors))
]

client.upsert(collection_name="study_chunks", points=points)

print("✅ Stored", len(points), "vectors in Qdrant.")
