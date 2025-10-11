# backend/app/models/chat_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=func.now())
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    sender = Column(String)  # 'user' or 'bot'
    text = Column(String)
    timestamp = Column(DateTime, default=func.now())

    chat = relationship("Chat", back_populates="messages")
