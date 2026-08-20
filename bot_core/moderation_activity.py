# ============================================================
# MODERATION ACTIVITY — Matches EXACTLY what app.py expects
# ============================================================

from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

moderation_activity_col = db["moderation_activity"]


# ============================================================
# Record Moderation Activity
# ============================================================

def record_mod_activity(staff_name: str, action: str):
    """
    Records a moderation staff activity such as warn, kick, ban, mute, unmute.
    """

    entry = {
        "staff_name": staff_name,
        "action": action,
        "timestamp": datetime.utcnow().isoformat()
    }

    moderation_activity_col.insert_one(entry)
    return entry


# ============================================================
# Load Moderation Activity (optional helper)
# ============================================================

def load_mod_activity(limit: int = 50):
    """
    Returns recent moderation activity entries.
    Not required by app.py, but useful for future pages.
    """
    return list(moderation_activity_col.find().sort("timestamp", -1).limit(limit))
