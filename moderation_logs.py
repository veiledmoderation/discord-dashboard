from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

mod_logs_col = db["moderation_logs"]


def log_mod_action(staff_name, action, target_user, reason):
    mod_logs_col.insert_one({
        "staff": staff_name,
        "action": action,
        "target": target_user,
        "reason": reason,
        "time": datetime.utcnow().isoformat()
    })
