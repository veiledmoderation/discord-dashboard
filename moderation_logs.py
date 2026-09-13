from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

mod_logs_col = db["moderation_logs"]

def now():
    return datetime.utcnow().isoformat()

def log_mod_action(staff_name, action_type, target_user, reason=""):
    mod_logs_col.insert_one({
        "time": now(),
        "text": f"{staff_name} {action_type} {target_user} ({reason})"
    })
