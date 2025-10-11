# app/core/config.py
import os
from dotenv import load_dotenv

# Load env file
load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    CHROMA_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
    EMB_MODEL: str = os.getenv("EMB_MODEL", "all-MiniLM-L6-v2")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecretkey")
    JWT_ALGORITHM: str = "HS256"

settings = Settings()
