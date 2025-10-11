# backend/app/api/auth_routes.py

from fastapi import APIRouter, HTTPException
from app.models.user_model import UserRegister, UserLogin, TokenResponse
from app.services import auth_service

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
def register_user(user: UserRegister):
    # Check if username already exists
    if auth_service.get_user(user.username):
        raise HTTPException(status_code=400, detail="Username already exists")

    # Create new user with default role = "user"
    created_user = auth_service.create_user(user.username, user.password)

    # Generate token using username and role
    token = auth_service.generate_token(created_user.username, created_user.role)

    return {
        "username": created_user.username,
        "role": created_user.role,
        "access_token": token
    }

@router.post("/login", response_model=TokenResponse)
def login_user(user: UserLogin):
    """
    Authenticate user. Returns 401 if credentials are invalid.
    """
    token = auth_service.authenticate_user(user.username, user.password)
    if not token:
        # User does not exist or password incorrect
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # At this point, user is valid
    db_user = auth_service.get_user(user.username)
    if not db_user:
        # Extra safety check
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "username": db_user.username,
        "role": db_user.role,
        "access_token": token
    }
