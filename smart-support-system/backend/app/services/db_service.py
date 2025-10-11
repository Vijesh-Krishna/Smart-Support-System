# backend/app/services/db_service.py
import chromadb
from sentence_transformers import SentenceTransformer

# Initialize Chroma client (local persistence)
chroma_client = chromadb.PersistentClient(path="chroma_db")

# Create a collection (like a table in SQL)
collection = chroma_client.get_or_create_collection("support_docs")

# Load embedding model (free, runs locally)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def add_document(doc_id: str, text: str):
    """Add a document to ChromaDB"""
    embedding = embedding_model.encode([text]).tolist()
    collection.add(documents=[text], embeddings=embedding, ids=[doc_id])

def query_document(query: str, top_k: int = 1):
    """Search for the most relevant document"""
    query_embedding = embedding_model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)
    return results
