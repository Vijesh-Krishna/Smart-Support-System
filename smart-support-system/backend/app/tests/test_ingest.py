# backend/app/tests/test_ingest.py
from app.services.ingest_service import ingest_pdf
from app.services.db_service import query_document

# Ingest sample PDF (replace with your file path)
ingest_pdf("app/sample_data/return_policy.pdf", "return_policy")


# Query
result = query_document("How many days will it take to process my refund?")
print(result)
