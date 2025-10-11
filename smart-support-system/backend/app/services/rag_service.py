# backend/app/services/rag_service.py
import os
import re
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from groq import Groq

# --- Setup ---
CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
EMB_MODEL = os.getenv("EMB_MODEL", "all-MiniLM-L6-v2")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

embed_model = SentenceTransformer(EMB_MODEL)
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)

# Groq LLM client
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set in environment")
groq_client = Groq(api_key=GROQ_API_KEY)


# --- Similarity ---
def _cosine_sim(a: List[float], b: List[float]) -> float:
    a = np.array(a, dtype=float).flatten()
    b = np.array(b, dtype=float).flatten()
    if np.linalg.norm(a) == 0.0 or np.linalg.norm(b) == 0.0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# --- Retrieve ---
def retrieve_top_k(product_id: str, query: str, k: int = 4):
    collection_name = f"product_{product_id}"
    try:
        collection = chroma_client.get_collection(collection_name)
    except Exception:
        return [], None

    q_emb = embed_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[q_emb],
        n_results=k,
        include=["documents", "metadatas", "embeddings"]
    )

    docs = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    embeddings = results.get("embeddings", [[]])[0]

    for i in range(len(documents)):
        docs.append({
            "id": f"doc_{i+1}",
            "document": documents[i],
            "metadata": metadatas[i] if i < len(metadatas) else {},
            "embedding": embeddings[i] if i < len(embeddings) else None
        })

    return docs, q_emb


# --- Build Prompt ---
def _build_prompt(question: str, docs: List[Dict]) -> str:
    context_parts = []
    for idx, d in enumerate(docs, start=1):
        excerpt = d["document"].strip()
        if len(excerpt) > 1500:
            excerpt = excerpt[:1500] + " ... [truncated]"
        context_parts.append(f"Source {idx} ({d['id']}):\n{excerpt}\n")
    context = "\n\n".join(context_parts).strip()

    return (
        "You are a helpful, concise customer support assistant.\n"
        "Answer the question ONLY using the provided context.\n"
        "If the answer is not present, say: \"I don't have that information.\".\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\nAnswer:"
    )


# --- Ask LLM ---
def answer_question(product_id: str, query: str) -> Dict:
    docs, _ = retrieve_top_k(product_id, query, k=4)

    if not docs:
        return {
            "product_id": product_id,
            "query": query,
            "answer": "I don’t have that information.",
            "sources": []
        }

    prompt = _build_prompt(query, docs)

    # Call Groq
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",  # free Groq LLM
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=300,
    )

    answer = response.choices[0].message.content

    return {
        "product_id": product_id,
        "query": query,
        "answer": answer.strip(),
        "sources": [d["document"] for d in docs]
    }


# --- New: generate_suggestions ---
def generate_suggestions(product_id: str, n: int = 3) -> List[str]:
    """
    Generate up to `n` short, user-facing question suggestions
    based on the top chunks for the given product.
    """
    # Attempt to retrieve top chunks (use a neutral query so we get representative chunks)
    docs, _ = retrieve_top_k(product_id, "overview", k=6)

    if not docs:
        # Fallback generic suggestions
        return [
            "What is this product about?",
            "How do I use this product?",
            "What are the main features?"
        ][:n]

    # Build a short context from the top chunks (trim to ~1000 chars each)
    content = "\n\n".join([d["document"][:1200] for d in docs])

    prompt = (
        f"You are given documentation excerpts for a product. Produce {n} short, "
        "user-friendly suggested queries that a user might ask the support bot. "
        "Keep each suggestion concise (a short question), and only output the suggestions "
        "as a short bullet list or numbered lines (no additional commentary).\n\n"
        f"Context excerpts:\n{content}\n\n"
        "Output 3 questions:"
    )

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes example user queries."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=200,
        )
        text = response.choices[0].message.content
    except Exception:
        # LLM unavailable -> fallback to safe defaults
        return [
            "What is this product about?",
            "How do I use this product?",
            "Where can I find setup instructions?"
        ][:n]

    # Parse output into lines and clean bullets/numbering
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        # remove leading bullets or numbering like "1.", "-", "•", "1)"
        s = re.sub(r'^[\-\*\•\d\.\)\s]+', '', s).strip()
        if s:
            lines.append(s)

    # If no clear lines, try splitting on punctuation as a fallback
    if not lines:
        parts = re.split(r'[;\n\.]\s+', text)
        for p in parts:
            p = p.strip()
            if p:
                lines.append(p)

    # Unique and limit
    seen = set()
    results = []
    for l in lines:
        if l.lower() not in seen:
            seen.add(l.lower())
            results.append(l)
        if len(results) >= n:
            break

    # Final fallback
    if len(results) < n:
        defaults = [
            "What is this product about?",
            "How do I use this product?",
            "What are the main features?"
        ]
        for d in defaults:
            if d not in results:
                results.append(d)
            if len(results) >= n:
                break

    return results[:n]
