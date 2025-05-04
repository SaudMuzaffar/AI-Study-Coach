# rag_agent.py

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap, RunnableLambda

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Init Qdrant and embeddings
qdrant = QdrantClient(host="qdrant", port=6333)
embedder = OpenAIEmbeddings(api_key=openai_api_key)
collection_name = "study_chunks"

# Function to perform semantic search from Qdrant
def semantic_search(query, top_k=5):
    query_vector = embedder.embed_query(query)
    search_result = qdrant.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k
    )

    docs = []
    for hit in search_result:
        payload = hit.payload
        doc_text = payload.get("text", "")
        source = payload.get("source", "unknown")
        docs.append(Document(page_content=doc_text, metadata={"source": source}))

    return docs

# Prompt Template for RAG-style generation
template = """You are an academic study assistant. Use the following content to answer the question.
If you don’t know the answer, say so honestly.

Context:
{context}

Question:
{question}

Answer:"""

prompt = ChatPromptTemplate.from_template(template)
llm = ChatOpenAI(api_key=openai_api_key)

# Chain to generate answers
rag_chain = (
    RunnableMap({
        "context": lambda x: "\n\n".join([doc.page_content for doc in semantic_search(x["question"])]),
        "question": lambda x: x["question"]
    })
    | prompt
    | llm
)

# Expose RAG Agent
def ask_rag_agent(question):
    try:
        answer = rag_chain.invoke({"question": question})
        return str(answer.content)
    except Exception as e:
        return f"❌ Semantic search failed: {e}"
