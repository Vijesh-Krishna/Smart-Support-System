import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from app.services.analytics_service import record_query  # Import analytics

# Path to store conversation history
CONVO_FILE = os.path.join(os.path.dirname(__file__), "conversations.json")

CANONICAL_FAILED_MSG = "I don't have info on that yet. Try rephrasing or contact support."

def _load_conversations() -> Dict[str, List[dict]]:
    if os.path.exists(CONVO_FILE):
        with open(CONVO_FILE, "r") as f:
            return json.load(f)
    return {}

def _save_conversations(data: Dict[str, List[dict]]):
    with open(CONVO_FILE, "w") as f:
        json.dump(data, f, indent=2)

def normalize_fallback_text(text: str) -> str:
    if not text:
        return CANONICAL_FAILED_MSG
    t = text.lower().strip()
    if (
        "i don't have that information" in t
        or "i dont have that information" in t
        or "i don’t have that information" in t
        or "i don't have info" in t
        or "no answer" in t
        or "no data" in t
        or "no results" in t
    ):
        return CANONICAL_FAILED_MSG
    return text

def create_new_chat(username: str) -> dict:
    all_convos = _load_conversations()
    if username not in all_convos:
        all_convos[username] = []

    chat_id = str(uuid.uuid4())
    new_chat = {
        "id": chat_id,
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    all_convos[username].append(new_chat)
    _save_conversations(all_convos)
    return new_chat

def get_all_chats(username: str) -> List[dict]:
    all_convos = _load_conversations()
    return all_convos.get(username, [])

def get_chat(username: str, chat_id: str) -> Optional[dict]:
    all_convos = _load_conversations()
    for chat in all_convos.get(username, []):
        if chat["id"] == chat_id:
            return chat
    return None

def add_message(username: str, chat_id: str, role: str, text: str, product_id: str = "", sources: List[str] = []):
    all_convos = _load_conversations()
    for chat in all_convos.get(username, []):
        if chat["id"] == chat_id:
            normalized_text = normalize_fallback_text(text)

            chat["messages"].append({
                "sender": role,
                "text": normalized_text,
                "timestamp": datetime.utcnow().isoformat(),
                "product_id": product_id,
                "sources": sources
            })
            chat["updated_at"] = datetime.utcnow().isoformat()

            if chat["title"] == "New Chat" and role == "user":
                chat["title"] = text[:20] + ("..." if len(text) > 20 else "")

            _save_conversations(all_convos)

            # ✅ Log analytics for failed queries
            if role == "bot":
                success = normalized_text != CANONICAL_FAILED_MSG
                record_query(product_id, success, query=text if not success else "", answer=normalized_text)

            return chat
    return None

def delete_chat(username: str, chat_id: str):
    all_convos = _load_conversations()
    if username in all_convos:
        all_convos[username] = [c for c in all_convos[username] if c["id"] != chat_id]
        _save_conversations(all_convos)

def clear_conversation_history(username: str):
    all_convos = _load_conversations()
    if username in all_convos:
        all_convos[username] = []
        _save_conversations(all_convos)
