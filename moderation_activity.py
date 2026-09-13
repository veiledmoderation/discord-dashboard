from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

staff_col = db["staff"]

def now():
    return datetime.utcnow().isoformat()

def record_mod_activity(staff_name, action_text):
    staff_col.update_one(
        {"username": staff_name},
        {"$push": {"activity": f"{now()} — {action_text}"}}
    )
