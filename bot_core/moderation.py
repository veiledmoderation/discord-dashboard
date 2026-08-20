# ============================================================
# MODERATION SYSTEM — Matches EXACTLY what app.py expects
# ============================================================

from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

moderation_actions_col = db["moderation_actions"]


# ============================================================
# Add Moderation Action
# ============================================================

def add_action(staff_name: str, action: str, target_user_id: str, reason: str):
    """
    Records a moderation action such as warn, kick, ban, mute, unmute.
    """

    entry = {
        "id": moderation_actions_col.count_documents({}) + 1,
        "staff_name": staff_name,
        "action": action,
        "target_user_id": target_user_id,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }

    moderation_actions_col.insert_one(entry)
    return entry


# ============================================================
# Load Moderation Actions (optional helper)
# ============================================================

def load_actions(limit: int = 50):
    """
    Returns recent moderation actions.
    Not required by app.py, but useful for future pages.
    """
    return list(moderation_actions_col.find().sort("timestamp", -1).limit(limit))
