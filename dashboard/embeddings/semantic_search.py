# semantic_search.py (enhanced)

from dotenv import load_dotenv
load_dotenv()

import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from langchain_openai import OpenAIEmbeddings

# 🧠 Connect to Qdrant
db = QdrantClient(host="localhost", port=6333)

# 🔐 Load OpenAI embedder
embedder = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

# 🔍 Function to perform semantic search with optional filtering
def semantic_search(query: str, top_k: int = 5, source_filter: str = None):
    # 1. Embed the user query
    query_vector = embedder.embed_query(query)

    # 2. Build optional filter
    query_filter = None
    if source_filter:
        query_filter = Filter(  # Only return matches from a specific file
            must=[
                FieldCondition(
                    key="source",
                    match=MatchValue(value=source_filter)
                )
            ]
        )

    # 3. Search Qdrant with or without filter
    results = db.search(
        collection_name="study_chunks",
        query_vector=query_vector,
        limit=top_k,
        query_filter=query_filter,
        with_payload=True
    )

    # 4. Format results with confidence scores
    top_chunks = []
    for hit in results:
        score = round(hit.score, 3)
        source = hit.payload.get("source", "unknown")
        text = hit.payload.get("text", "")
        title = hit.payload.get("title")
        top_chunks.append({
            "score": score,
            "text": text,
            "source": source,
            "title": title
        })

    return top_chunks

# ✅ Standalone test
if __name__ == "__main__":
    hits = semantic_search("what is the conclusion of the book?", source_filter="introductory-guide-to-ppc.txt")
    for i, chunk in enumerate(hits):
        print(f"\n🔹 Result {i+1} [Score: {chunk['score']}] - Source: {chunk['source']}")
        if chunk["title"]:
            print(f"📌 Title: {chunk['title']}")
        print(chunk['text'])
        print("-" * 80)
