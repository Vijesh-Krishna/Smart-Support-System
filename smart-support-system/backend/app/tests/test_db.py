# backend/app/tests/test_db.py
from app.services.db_service import add_document, query_document

# Add sample doc
add_document("1", "You can return a product within 30 days of purchase.")
add_document("2", "Our company offers a 1-year warranty on all products.")

# Query
result = query_document("what is the return policy")
print(result)   
