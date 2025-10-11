# backend/app/api/user_routes.py
from fastapi import APIRouter
from app.services.ingest_service import list_products

router = APIRouter()

# ----------------------------
# List all product IDs for normal users
# ----------------------------
@router.get("/products")
def user_products():
    """
    Returns only product IDs for users.
    Example response: {"products": ["Resume.final", "return_policy"]}
    """
    product_ids = list_products()
    return {"products": product_ids}
