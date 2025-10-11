# backend/app/services/ingest_service.py
import os
import fitz  # PyMuPDF
import chromadb
import uuid
from datetime import datetime
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

# -------------------------
# Config
# -------------------------
CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
EMB_MODEL = os.getenv("EMB_MODEL", "all-MiniLM-L6-v2")

embed_model = SentenceTransformer(EMB_MODEL)
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)

# -------------------------
# Utilities
# -------------------------
def split_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_text(text)

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# -------------------------
# Core functions
# -------------------------
def add_document_chroma(doc_id: str, text: str, product_id: str, file_name: str, file_id: str):
    collection_name = f"product_{product_id}"
    try:
        collection = chroma_client.get_collection(collection_name)
    except Exception:
        collection = chroma_client.create_collection(name=collection_name)

    embedding = embed_model.encode([text])[0].tolist()

    collection.add(
        ids=[doc_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[{
            "file_name": file_name,
            "file_id": file_id,
            "uploaded_at": datetime.utcnow().isoformat()
        }]
    )

def ingest_pdf(product_id: str, pdf_path: str) -> dict:
    file_id = str(uuid.uuid4())
    file_name = os.path.basename(pdf_path)

    raw_text = extract_text_from_pdf(pdf_path)
    if not raw_text.strip():
        raise ValueError("No text could be extracted from the PDF.")

    chunks = split_text(raw_text)

    for i, chunk in enumerate(chunks):
        add_document_chroma(f"{product_id}_{file_id}_{i}", chunk, product_id, file_name, file_id)

    return {
        "file_id": file_id,
        "file_name": file_name,
        "chunks": len(chunks),
        "uploaded_at": datetime.utcnow().isoformat(),
        "pdf_path": pdf_path
    }

# -------------------------
# New function: index existing file by file_id
# -------------------------
def index_file_by_id(file_id: str, product_id: str = None, pdf_path: str = None, file_name: str = None):
    if not pdf_path or not product_id or not file_name:
        raise ValueError("product_id, pdf_path, and file_name are required to index the file.")

    raw_text = extract_text_from_pdf(pdf_path)
    if not raw_text.strip():
        raise ValueError("No text could be extracted from the PDF for indexing.")

    chunks = split_text(raw_text)
    for i, chunk in enumerate(chunks):
        add_document_chroma(f"{product_id}_{file_id}_{i}", chunk, product_id, file_name, file_id)

    return True

# -------------------------
# Product / document management
# -------------------------
def list_products() -> list:
    products = []
    for c in chroma_client.list_collections():
        if c.name.startswith("product_"):
            product_id = c.name[len("product_"):]
            products.append(product_id)
    return products

def list_documents(product_id: str) -> list:
    collection_name = f"product_{product_id}"
    try:
        collection = chroma_client.get_collection(collection_name)
    except Exception:
        return []

    results = collection.get()
    return [
        {"id": doc_id, "text": doc, "metadata": meta}
        for doc_id, doc, meta in zip(
            results.get("ids", []),
            results.get("documents", []),
            results.get("metadatas", [])
        )
    ]

def search_documents(product_id: str, query: str, top_k: int = 5):
    collection_name = f"product_{product_id}"
    try:
        collection = chroma_client.get_collection(collection_name)
    except Exception:
        return []

    query_embedding = embed_model.encode([query])[0].tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    return [
        {"id": doc_id, "text": doc, "metadata": meta}
        for doc_id, doc, meta in zip(
            results.get("ids", []),
            results.get("documents", []),
            results.get("metadatas", [])
        )
    ]

def get_all_products_metadata():
    all_metadata = []
    for product_id in list_products():
        docs = list_documents(product_id)
        files_meta = {}
        for doc in docs:
            if not doc.get("metadata"):
                continue
            file_id = doc["metadata"]["file_id"]
            if file_id not in files_meta:
                files_meta[file_id] = {
                    "file_name": doc["metadata"]["file_name"],
                    "file_id": file_id,
                    "uploaded_at": doc["metadata"]["uploaded_at"],
                    "chunks": 0,
                }
            files_meta[file_id]["chunks"] += 1

        all_metadata.append({
            "product_id": product_id,
            "files": list(files_meta.values())
        })
    return all_metadata

# -------------------------
# Deletion logic (updated)
# -------------------------
def delete_document_by_file_id(file_id: str):
    """
    Delete all chunks of a file given its file_id.
    Return the product_id it belonged to (for cleanup).
    """
    for product_id in list_products():
        collection_name = f"product_{product_id}"
        try:
            collection = chroma_client.get_collection(collection_name)
        except Exception:
            continue

        results = collection.get()
        ids_to_delete = [
            doc_id for doc_id, meta in zip(results.get("ids", []), results.get("metadatas", []))
            if meta and meta.get("file_id") == file_id
        ]

        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            # ✅ return product_id so caller can decide if product should be deleted
            return product_id
    return None

def delete_product_if_empty(product_id: str):
    """
    Delete the product collection if it has no files left.
    """
    collection_name = f"product_{product_id}"
    try:
        collection = chroma_client.get_collection(collection_name)
    except Exception:
        return False

    results = collection.get()
    if not results.get("ids"):
        chroma_client.delete_collection(name=collection_name)
        return True
    return False
