# rag_agent.py

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap

# --- Load environment variables ---
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# --- Initialize clients once ---
qdrant = QdrantClient(host="qdrant", port=6333)
embedder = OpenAIEmbeddings(api_key=openai_api_key)
llm = ChatOpenAI(api_key=openai_api_key)  # Reuse this across all functions
collection_name = "study_chunks"

# --- Semantic Search ---
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

# --- One-shot RAG chain (still usable) ---
template = """You are an academic study assistant. Use the following content to answer the question.
If you don’t know the answer, say so honestly.

Context:
{context}

Question:
{question}

Answer:"""

prompt = ChatPromptTemplate.from_template(template)

rag_chain = (
    RunnableMap({
        "context": lambda x: "\n\n".join([doc.page_content for doc in semantic_search(x["question"])]),
        "question": lambda x: x["question"]
    })
    | prompt
    | llm
)

def ask_rag_agent(question):
    try:
        answer = rag_chain.invoke({"question": question})
        return str(answer.content)
    except Exception as e:
        return f"❌ Semantic search failed: {e}"

# --- Chat-based RAG (multi-turn) ---
def chat_with_rag(user_question, chat_history, top_k=5):
    try:
        # Limit to last 3–5 turns to avoid overloading prompt
        recent_history = chat_history[-5:]

        # Build dialogue from history
        history_text = ""
        for user_msg, assistant_msg in recent_history:
            history_text += f"User: {user_msg}\nAssistant: {assistant_msg}\n"

        # Run semantic search
        context_docs = semantic_search(user_question, top_k=top_k)
        context = "\n\n".join([doc.page_content for doc in context_docs])

        # Compose final prompt with hallucination guardrails
        full_prompt = f"""You are an academic study assistant helping the user understand their uploaded notes.

You may use general knowledge **only if it is a well-known fact** (e.g., basic definitions, historical dates, scientific terms), 
but do not guess or make up information.

If a question is not clearly answered in the notes or your general knowledge, say:
"⚠️ Sorry, I couldn't confidently find that answer in your notes or general knowledge."

Here is the past conversation:
{history_text}

Here are some relevant notes from the user's documents:
{context}

Now respond to the user's new question:
{user_question}
"""

        response = llm.invoke(full_prompt)
        return response.content

    except Exception as e:
        return f"❌ Chat-based RAG failed: {e}"
