from core.db import MongoDB

db = MongoDB()
print("✅ Connected to MongoDB Atlas")
print("Collections:", db.db.list_collection_names())
