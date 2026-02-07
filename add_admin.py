from core.db import MongoDB

db = MongoDB()

admin = {
    "username": "Jo",
    "password": "johan",
    "role": "admin"
}

db.users.insert_one(admin)
print("✅ Admin user added successfully.")
