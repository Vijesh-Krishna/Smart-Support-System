# backend/app/services/chat_service.py
from sqlalchemy.orm import Session
from app.models.chat_model import Chat, Message
from app.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_chats(username: str):
    """Fetch all chats belonging to a specific user."""
    db = SessionLocal()
    chats = db.query(Chat).filter(Chat.username == username).order_by(Chat.created_at.desc()).all()
    return [
        {
            "id": chat.id,
            "title": chat.title,
            "created_at": chat.created_at,
            "messages": [
                {"id": msg.id, "sender": msg.sender, "text": msg.text, "timestamp": msg.timestamp}
                for msg in chat.messages
            ],
        }
        for chat in chats
    ]


def create_new_chat(username: str):
    """Create a new chat for the given user."""
    db = SessionLocal()
    new_chat = Chat(username=username, title=f"Chat with {username}")
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    db.close()
    return {"id": new_chat.id, "title": new_chat.title, "created_at": new_chat.created_at, "messages": []}


def add_message_to_chat(chat_id: int, username: str, sender: str, text: str, bot_reply: str):
    """Add a message from user and bot to a chat session."""
    db = SessionLocal()
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.username == username).first()
    if not chat:
        db.close()
        return {"error": "Chat not found"}

    user_msg = Message(chat_id=chat_id, sender=sender, text=text)
    bot_msg = Message(chat_id=chat_id, sender="bot", text=bot_reply)

    db.add_all([user_msg, bot_msg])
    db.commit()
    db.refresh(chat)
    db.close()

    return {
        "id": chat.id,
        "title": chat.title,
        "created_at": chat.created_at,
        "messages": [
            {"sender": msg.sender, "text": msg.text, "timestamp": msg.timestamp}
            for msg in chat.messages
        ],
    }
