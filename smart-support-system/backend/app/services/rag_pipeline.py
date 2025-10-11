# backend/app/services/rag_pipeline.py

import os
from dotenv import load_dotenv
from groq import Groq
from app.services.rag_service import retrieve_top_k, _build_prompt

# ✅ Correct path to load .env
load_dotenv(
    dotenv_path=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    )
)

# ✅ Initialize Groq client safely
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("❌ GROQ_API_KEY is missing. Please set it in your .env file")

groq_client = Groq(api_key=api_key)


def query_groq_rag(product_id: str, question: str):
    """Query Groq LLM with retrieved context."""
    docs, _ = retrieve_top_k(product_id, question, k=3)
    if not docs:
        return {
            "answer": "No documents found for this product.",
            "sources": [],
            "confidence": 0.0,
            "escalate_to_human": True,
        }

    prompt = _build_prompt(question, docs)

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful customer support AI."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=512,
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": [d["document"][:200] for d in docs],
        "confidence": 1.0,
        "escalate_to_human": False,
    }


def generate_suggestions_from_rag(product_id: str, num_suggestions: int = 3):
    """
    ✅ Generate top-N query suggestions dynamically from vector store for a product.
    Reuses retrieve_top_k to avoid using undefined vector_db.
    """
    try:
        # 🧠 Get top 10 representative chunks from vector DB for this product
        docs, _ = retrieve_top_k(product_id, "", k=10)
        if not docs:
            return []

        # 📝 Extract meaningful sentences from docs
        candidates = []
        for d in docs:
            text = d["document"]
            sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 8]
            candidates.extend(sentences)

        # ✨ Select top-N as suggestions (convert to questions if needed)
        suggestions = []
        for s in candidates[:num_suggestions]:
            if not s.endswith("?"):
                s = f"What is {s[:80]}?"
            suggestions.append(s)

        return suggestions

    except Exception as e:
        print(f"❌ Error generating suggestions: {e}")
        return []
