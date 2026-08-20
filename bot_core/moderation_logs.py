# ============================================================
# MODERATION LOGS — Matches EXACTLY what app.py expects
# ============================================================

from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

moderation_logs_col = db["moderation_logs"]


# ============================================================
# Log Moderation Action
# ============================================================

def log_mod_action(staff_name: str, action: str, target_user_id: str):
    """
    Logs a moderation action such as warn, kick, ban, mute, unmute.
    """

    log_entry = {
        "staff_name": staff_name,
        "action": action,
        "target_user_id": target_user_id,
        "timestamp": datetime.utcnow().isoformat()
    }

    moderation_logs_col.insert_one(log_entry)
    return log_entry


# ============================================================
# Load Moderation Logs (optional helper)
# ============================================================

def load_mod_logs(limit: int = 50):
    """
    Returns recent moderation logs.
    Not required by app.py, but useful for future pages.
    """
    return list(moderation_logs_col.find().sort("timestamp", -1).limit(limit))
