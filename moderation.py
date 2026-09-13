from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

mod_actions_col = db["moderation_actions"]

def now():
    return datetime.utcnow().isoformat()

def add_action(staff_name, action_type, target_user, reason=""):
    mod_actions_col.insert_one({
        "time": now(),
        "staff_name": staff_name,
        "action_type": action_type,
        "target_user": target_user,
        "reason": reason
    })
