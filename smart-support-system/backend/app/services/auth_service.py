# backend/app/services/auth_service.py

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict

import jwt
from passlib.context import CryptContext

from app.models.user_model import UserInDB
from app.core.config import settings

# ---------------- Persistence Setup ---------------- #

USER_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def _load_users() -> Dict[str, UserInDB]:
    """Load users from JSON file into memory."""
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            raw = json.load(f)
            return {
                username: UserInDB(**data)
                for username, data in raw.items()
            }
    return {}

def _save_users():
    """Save current users to JSON file (internal)."""
    with open(USER_FILE, "w") as f:
        serializable = {
            username: user.dict()
            for username, user in fake_users_db.items()
        }
        json.dump(serializable, f, indent=2)

# Public wrapper (so other routes can call it safely if needed)
def save_users():
    """Persist current in-memory users to JSON file."""
    _save_users()

# Load users into memory at startup
fake_users_db: Dict[str, UserInDB] = _load_users()

# ---------------- Password Utilities ---------------- #

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

# ---------------- User Utilities ---------------- #

def create_user(username: str, password: str, role: str = "user") -> UserInDB:
    """Create and store a user (persists to JSON)."""
    if username in fake_users_db:
        raise ValueError("User already exists")

    user = UserInDB(
        username=username,
        hashed_password=hash_password(password),
        role=role
    )
    fake_users_db[username] = user
    _save_users()
    return user

def delete_user(username: str) -> bool:
    """Delete a user by username (persists to JSON)."""
    if username not in fake_users_db:
        return False
    if username == "admin":
        # Prevent accidental removal of default admin
        return False
    del fake_users_db[username]
    _save_users()
    return True

def list_users() -> Dict[str, dict]:
    """Return all users (username + role only for security)."""
    return {
        username: {"username": user.username, "role": user.role}
        for username, user in fake_users_db.items()
    }

def get_user(username: str) -> Optional[UserInDB]:
    """Get a single user by username."""
    return fake_users_db.get(username)

def get_user_role(username: str) -> str:
    """Return the role of the user."""
    user = fake_users_db.get(username)
    if user:
        return user.role
    return "user"

# ---------------- Auth Utilities ---------------- #

def authenticate_user(username: str, password: str) -> Optional[str]:
    """
    Authenticate user and return a JWT token if valid.
    Returns None if authentication fails.
    """
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user.hashed_password):
        return None

    return generate_token(username, user.role)

def generate_token(username: str, role: str) -> str:
    """Generate a JWT token for a given username and role."""
    token_data = {
        "sub": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=5)  # token lifetime
    }
    return jwt.encode(token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    """
    Decode JWT token and return payload if valid.
    Returns None if invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None