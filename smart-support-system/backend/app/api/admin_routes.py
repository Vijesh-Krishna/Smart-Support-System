# backend/app/api/admin_routes.py
import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from app.services.ingest_service import (
    ingest_pdf,
    list_products,
    list_documents,
    search_documents,
    get_all_products_metadata,
    delete_document_by_file_id,
    delete_product_if_empty
)
from app.utils.security import require_role
from app.services import auth_service
from app.services.analytics_service import get_analytics, set_total_users, clear_failed_queries

router = APIRouter()

# ----------------------------
# Document Ingestion (Admin)
# ----------------------------
@router.post("/upload")
def upload_doc(file: UploadFile = File(...), admin=Depends(require_role("admin"))):
    file_name = file.filename

    # Auto-rename if file exists
    existing_files = [f["file_name"] for p in get_all_products_metadata() for f in p.get("files", [])]
    original_name = file_name
    counter = 1
    while file_name in existing_files:
        name, ext = os.path.splitext(original_name)
        file_name = f"{name}_{counter}{ext}"
        counter += 1

    temp_path = f"{file_name}"
    with open(temp_path, "wb") as f:
        f.write(file.file.read())

    try:
        product_id = os.path.splitext(file_name)[0]
        file_meta = ingest_pdf(product_id, temp_path)

        # Optional: add size info (in bytes)
        if os.path.exists(temp_path):
            file_meta["size"] = os.path.getsize(temp_path)

        # Optional: store local path if you want download to work
        file_meta["local_path"] = temp_path

    finally:
        os.remove(temp_path)

    return {
        "message": f"File {file_name} ingested for product {product_id}",
        "file": file_meta
    }


# ----------------------------
# File Download (Admin)
# ----------------------------
@router.get("/files/{file_id}/download")
def download_file(file_id: str, admin=Depends(require_role("admin"))):
    """
    Allows admin to download/view a raw uploaded file
    """
    products = get_all_products_metadata()
    for product in products:
        for f in product.get("files", []):
            if f.get("file_id") == file_id:
                file_path = f.get("local_path")
                if file_path and os.path.exists(file_path):
                    return FileResponse(file_path, filename=f.get("file_name"), media_type="application/octet-stream")
                else:
                    raise HTTPException(status_code=404, detail="File not found on server")
    raise HTTPException(status_code=404, detail="File ID not found")


# ----------------------------
# Document Delete (Admin)
# ----------------------------
@router.delete("/delete/{file_id}")
def delete_file(file_id: str, admin=Depends(require_role("admin"))):
    product_id = delete_document_by_file_id(file_id)
    if not product_id:
        raise HTTPException(status_code=404, detail="File not found")

    deleted_product = delete_product_if_empty(product_id)
    if deleted_product:
        return {"message": f"File '{file_id}' deleted and product '{product_id}' removed (no files left)"}

    return {"message": f"File '{file_id}' deleted successfully"}


# ----------------------------
# Product Delete (Admin)
# ----------------------------
@router.delete("/delete_product/{product_id}")
def delete_product(product_id: str, admin=Depends(require_role("admin"))):
    try:
        success = delete_product_if_empty(product_id)
        if success:
            return {"message": f"Product '{product_id}' deleted successfully"}
        else:
            raise HTTPException(status_code=400, detail=f"Product '{product_id}' not empty or not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ----------------------------
# Analytics Clear Failed Queries
# ----------------------------
@router.delete("/analytics/clear_failed_queries")
def clear_failed_queries_endpoint(admin=Depends(require_role("admin"))):
    """
    Clears all failed queries from analytics.
    """
    try:
        clear_failed_queries()
        return {"message": "All failed queries cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# Products
# ----------------------------
@router.get("/products_metadata")
def products_metadata(admin=Depends(require_role("admin"))):
    """
    Returns metadata for all products.
    Adds 'size' if possible, but safely without breaking.
    """
    products = get_all_products_metadata()

    for product in products:
        for f in product.get("files", []):
            # Size in bytes, optional
            if "size" not in f or not f["size"]:
                local_path = f.get("local_path")
                if local_path and os.path.exists(local_path):
                    f["size"] = os.path.getsize(local_path)
                else:
                    f["size"] = None
            # Keep other existing metadata
    return {"products": products}


@router.get("/products/{product_id}/documents")
def list_product_documents(product_id: str, admin=Depends(require_role("admin"))):
    docs = list_documents(product_id)
    return {"product_id": product_id, "documents": docs}


@router.get("/products/{product_id}/search")
def search_product_documents(product_id: str, query: str, top_k: int = 5, admin=Depends(require_role("admin"))):
    docs = search_documents(product_id, query, top_k)
    return {"product_id": product_id, "query": query, "results": docs}


# ----------------------------
# User Management (Admin)
# ----------------------------
@router.get("/users")
def list_users(admin=Depends(require_role("admin"))):
    return {"total_users": len(auth_service.list_users()), "users": auth_service.list_users()}


@router.delete("/users/{username}")
def delete_user(username: str, admin=Depends(require_role("admin"))):
    success = auth_service.delete_user(username)
    if not success:
        raise HTTPException(status_code=404, detail="User not found or cannot delete admin")
    return {"message": f"User '{username}' deleted successfully"}


# ----------------------------
# Analytics
# ----------------------------
@router.get("/analytics")
def get_admin_analytics(admin=Depends(require_role("admin"))):
    set_total_users(len(auth_service.list_users()))
    return get_analytics()
