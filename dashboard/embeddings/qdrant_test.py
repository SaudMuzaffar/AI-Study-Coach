from qdrant_client import QdrantClient

# 🔌 Connect to local Qdrant running at http://localhost:6333
client = QdrantClient(host="localhost", port=6333)

# ✅ Print status
print("Qdrant connected:", client.get_collections())
