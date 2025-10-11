import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Routers
from app.api import auth_routes, chat_routes, admin_routes, user_routes

# Database setup
from app.database import Base, engine
from app.models import chat_model  # ✅ ensures Chat & Message models are registered

# Auth service for default admin
from app.services.auth_service import decode_token, create_user

# ---------------------------
# Load environment variables
# ---------------------------
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# ---------------------------
# FastAPI App Initialization
# ---------------------------
app = FastAPI(title="🚀 Smart Support System")

# ---------------------------
# Database Initialization
# ---------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------
# Create Default Admin User
# ---------------------------
@app.on_event("startup")
def create_default_admin():
    """Create a default admin user if not already present."""
    try:
        create_user("admin", "admin123", role="admin")
        print("✅ Default admin user ensured (username='admin', password='admin123')")
    except ValueError:
        print("ℹ️ Default admin user already exists")

# ---------------------------
# CORS Middleware
# ---------------------------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Routers
# ---------------------------
app.include_router(chat_routes.router)
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])

# ---------------------------
# Root Endpoint
# ---------------------------
@app.get("/")
def root():
    """Root API endpoint for health check."""
    return {"message": "🚀 Smart Support System is running"}

# ---------------------------
# Middleware: Request Logging
# ---------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    user_info = "Anonymous"

    # Extract token if present
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        if payload:
            user_info = f"{payload.get('sub')} ({payload.get('role')})"

    # Process request
    response = await call_next(request)
    duration = time.time() - start_time

    print(
        f"[{request.method}] {request.url.path} | User: {user_info} | "
        f"Time: {duration:.2f}s | Status: {response.status_code}"
    )

    return response