import os
from app.services.rag_pipeline import query_groq_rag

def test_query_groq_rag():
    os.environ["GROQ_API_KEY"] = "your_test_key_here"  # or load from env
    question = "What is the return policy?"
    context = "Customers can return items within 30 days for a full refund."
    answer = query_groq_rag(question, context)
    assert "30 days" in answer or "return" in answer.lower()
