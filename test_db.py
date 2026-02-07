# test_db.py
from core.db import MongoDB

db = MongoDB()

db.save_case({
    "test": "mongo cloud working",
    "data": 123
})

print(db.get_all_cases())
