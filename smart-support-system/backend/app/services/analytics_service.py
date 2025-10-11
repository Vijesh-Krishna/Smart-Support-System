import os
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ---------------------------
# FastAPI App
# ---------------------------
app = FastAPI(title="Analytics Service")

# File to persist analytics
ANALYTICS_FILE = os.path.join(os.path.dirname(__file__), "../../data/analytics.json")

# Default structure
analytics: Dict[str, Any] = {
    "total_users": 0,
    "failed_queries": [],
    "queries_per_product": {}
}

# ---------------------------
# Helpers for persistence
# ---------------------------
def load_analytics():
    global analytics
    if os.path.exists(ANALYTICS_FILE):
        try:
            with open(ANALYTICS_FILE, "r") as f:
                analytics = json.load(f)
        except Exception:
            print("⚠️ Failed to load analytics.json, starting fresh")
            analytics = {
                "total_users": 0,
                "failed_queries": [],
                "queries_per_product": {}
            }

def save_analytics():
    os.makedirs(os.path.dirname(ANALYTICS_FILE), exist_ok=True)
    with open(ANALYTICS_FILE, "w") as f:
        json.dump(analytics, f, indent=2)

# ---------------------------
# Analytics functions
# ---------------------------
def get_analytics() -> Dict[str, Any]:
    return analytics

def set_total_users(count: int):
    analytics["total_users"] = count
    save_analytics()

def record_user(username: str):
    analytics["total_users"] += 1
    save_analytics()

def log_failed_query(product_id: str, query: str, answer: str = ""):
    canonical_failed_msg = "I don't have info on that yet. Try rephrasing or contact support."
    if not answer or "don't have" in answer.lower() or "no answer" in answer.lower() or "no data" in answer.lower():
        answer = canonical_failed_msg

    analytics["failed_queries"].append({
        "product_id": product_id,
        "query": query,
        "answer": answer,
        "timestamp": datetime.utcnow().isoformat()
    })
    save_analytics()

def increment_queries(product_id: str):
    if product_id not in analytics["queries_per_product"]:
        analytics["queries_per_product"][product_id] = 0
    analytics["queries_per_product"][product_id] += 1
    save_analytics()

def record_query(product_id: str, success: bool, query: str, answer: str = ""):
    increment_queries(product_id)
    if not success:
        log_failed_query(product_id, query, answer)

def clear_failed_queries():
    analytics["failed_queries"] = []
    save_analytics()

# ---------------------------
# Pydantic Models
# ---------------------------
class FailedQuery(BaseModel):
    product_id: str
    query: str
    answer: str = ""

# ---------------------------
# FastAPI Endpoints
# ---------------------------
@app.post("/analytics/log_failed_query")
async def api_log_failed_query(fq: FailedQuery):
    try:
        log_failed_query(fq.product_id, fq.query, fq.answer)
        return {"status": "success", "message": "Failed query logged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/get")
async def api_get_analytics():
    return get_analytics()

@app.post("/analytics/clear_failed_queries")
async def api_clear_failed_queries():
    clear_failed_queries()
    return {"status": "success", "message": "Failed queries cleared"}

# ---------------------------
# Initialize at startup
# ---------------------------
load_analytics()
