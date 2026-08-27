from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

mod_actions_col = db["moderation_actions"]


def add_action(staff_name, action_type, target_user, reason):
    entry = {
        "staff": staff_name,
        "action": action_type,
        "target": target_user,
        "reason": reason,
        "time": datetime.utcnow().isoformat()
    }
    mod_actions_col.insert_one(entry)
    return entry
