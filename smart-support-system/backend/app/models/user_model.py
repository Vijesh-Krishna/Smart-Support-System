# backend/app/models/user_model.py

from pydantic import BaseModel

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    username: str
    role: str
    access_token: str

class ChatRequest(BaseModel):
    product_id: str
    question: str

class UserInDB(BaseModel):
    username: str
    hashed_password: str
    role: str = "user"
