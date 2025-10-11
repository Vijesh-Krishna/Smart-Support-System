from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services import conversation_service
from app.utils.security import require_role
from app.services.rag_pipeline import query_groq_rag, generate_suggestions_from_rag
from app.services.rag_service import answer_question
from app.services.analytics_service import record_query

router = APIRouter(prefix="/chat", tags=["Chat"])

# -----------------------------
# Request / Response Models
# -----------------------------
class ChatQuery(BaseModel):
    product_id: Optional[str] = ""
    question: str

class QARequest(BaseModel):
    product_id: str
    question: str

class MessageSchema(BaseModel):
    chat_id: str
    product_id: str
    question: str

class ChatMessage(BaseModel):
    sender: str
    text: str
    timestamp: str
    product_id: str
    sources: List[str]

class ChatResponse(BaseModel):
    id: str
    title: str
    messages: List[ChatMessage]
    created_at: str
    updated_at: str

class SuggestionResponse(BaseModel):
    suggestions: List[str]

# -----------------------------
# Helpers
# -----------------------------
def is_failed_query(answer_text: str) -> bool:
    fallback_texts = [
        "I don't have that information",
        "I don't have info on that yet. Try rephrasing or contact support.",
        "No answer",
        "No data",
        "No results"
    ]
    if not answer_text:
        return True
    return any(ft.lower() in answer_text.lower() for ft in fallback_texts)

# -----------------------------
# Multi-Chat System
# -----------------------------
@router.get("/all", response_model=List[ChatResponse])
def get_all_chats(user=Depends(require_role("user"))):
    return conversation_service.get_all_chats(user["sub"])

@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat_by_id(chat_id: str, user=Depends(require_role("user"))):
    chat = conversation_service.get_chat(user["sub"], chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.post("/new", response_model=ChatResponse)
def new_chat(user=Depends(require_role("user"))):
    return conversation_service.create_new_chat(user["sub"])

@router.post("/{chat_id}/message", response_model=ChatResponse)
def send_message(chat_id: str, message: MessageSchema, user=Depends(require_role("user"))):
    if not message.question.strip() or len(message.question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Please provide a valid question.")

    # Get AI response from RAG pipeline
    answer = query_groq_rag(message.product_id, message.question)
    answer_text = answer.get("answer", str(answer))

    # Save user message
    conversation_service.add_message(
        username=user["sub"],
        chat_id=chat_id,
        role="user",
        text=message.question,
        product_id=message.product_id,
        sources=[]
    )

    # Save assistant message
    conversation_service.add_message(
        username=user["sub"],
        chat_id=chat_id,
        role="assistant",
        text=answer_text,
        product_id=message.product_id,
        sources=answer.get("sources", [])
    )

    # Record analytics
    success = not is_failed_query(answer_text)
    record_query(message.product_id, success, message.question, answer_text)

    updated_chat = conversation_service.get_chat(user["sub"], chat_id)
    if not updated_chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return updated_chat

# -----------------------------
# Legacy Endpoints (Backward Compatibility)
# -----------------------------
@router.post("/", response_model=ChatResponse)
def chat_post(request: ChatQuery, user=Depends(require_role("user"))):
    if not request.question.strip() or len(request.question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Please provide a valid question.")

    answer = query_groq_rag(request.product_id, request.question)
    answer_text = answer.get("answer", str(answer))

    chats = conversation_service.get_all_chats(user["sub"])
    chat = chats[-1] if chats else conversation_service.create_new_chat(user["sub"])

    conversation_service.add_message(
        username=user["sub"],
        chat_id=chat["id"],
        role="user",
        text=request.question,
        product_id=request.product_id,
        sources=[]
    )
    conversation_service.add_message(
        username=user["sub"],
        chat_id=chat["id"],
        role="assistant",
        text=answer_text,
        product_id=request.product_id,
        sources=answer.get("sources", [])
    )

    success = not is_failed_query(answer_text)
    record_query(request.product_id, success, request.question, answer_text)

    return conversation_service.get_chat(user["sub"], chat["id"])

@router.post("/qa", response_model=ChatResponse)
def qa_post(request: QARequest, user=Depends(require_role("user"))):
    if not request.question.strip() or len(request.question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Please provide a valid question.")

    answer = answer_question(request.product_id, request.question)
    answer_text = answer.get("answer", str(answer))

    chats = conversation_service.get_all_chats(user["sub"])
    chat = chats[-1] if chats else conversation_service.create_new_chat(user["sub"])

    conversation_service.add_message(
        username=user["sub"],
        chat_id=chat["id"],
        role="user",
        text=request.question,
        product_id=request.product_id,
        sources=[]
    )
    conversation_service.add_message(
        username=user["sub"],
        chat_id=chat["id"],
        role="assistant",
        text=answer_text,
        product_id=request.product_id,
        sources=answer.get("sources", [])
    )

    success = not is_failed_query(answer_text)
    record_query(request.product_id, success, request.question, answer_text)

    return conversation_service.get_chat(user["sub"], chat["id"])

# -----------------------------
# AI Suggestions per Product
# -----------------------------
@router.get("/{product_id}/suggestions", response_model=SuggestionResponse)
def get_query_suggestions(product_id: str, user=Depends(require_role("user"))):
    """
    Generate top 3 AI suggestions for user queries based on product's PDF / vector DB.
    """
    suggestions = generate_suggestions_from_rag(product_id)
    if not suggestions or len(suggestions) == 0:
        raise HTTPException(status_code=404, detail="No suggestions available for this product.")
    return {"suggestions": suggestions}

# -----------------------------
# Conversation History (Legacy)
# -----------------------------
@router.get("/history", response_model=List[ChatResponse])
def get_history(user=Depends(require_role("user"))):
    return conversation_service.get_all_chats(user["sub"])

@router.delete("/history")
def clear_history(user=Depends(require_role("user"))):
    conversation_service.clear_conversation_history(user["sub"])
    return {"message": f"History cleared for {user['sub']}"}

# -----------------------------
# Delete a single chat
# -----------------------------
@router.delete("/{chat_id}", response_model=dict)
def delete_single_chat(chat_id: str, user=Depends(require_role("user"))):
    chat = conversation_service.get_chat(user["sub"], chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    conversation_service.delete_chat(user["sub"], chat_id)
    return {"message": f"Chat {chat_id} deleted successfully"}
