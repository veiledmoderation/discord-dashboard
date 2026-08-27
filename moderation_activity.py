from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

mod_activity_col = db["moderation_activity"]


def record_mod_activity(staff_name, action):
    mod_activity_col.insert_one({
        "staff": staff_name,
        "action": action,
        "time": datetime.utcnow().isoformat()
    })
