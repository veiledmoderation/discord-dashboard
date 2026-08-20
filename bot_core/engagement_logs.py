# ============================================================
# ENGAGEMENT LOGS — Matches EXACTLY what app.py expects
# ============================================================

from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

engagement_logs_col = db["engagement_logs"]


# ============================================================
# Log Engagement Action
# ============================================================

def log_engagement_action(staff_name: str, action: str, event_id: int):
    """
    Logs an engagement action such as creating or closing an event.
    """

    log_entry = {
        "staff_name": staff_name,
        "action": action,
        "event_id": event_id,
        "timestamp": datetime.utcnow().isoformat()
    }

    engagement_logs_col.insert_one(log_entry)
    return log_entry


# ============================================================
# Load Engagement Logs (optional helper)
# ============================================================

def load_engagement_logs(limit: int = 50):
    """
    Returns recent engagement logs.
    Not required by app.py, but useful for future pages.
    """
    return list(engagement_logs_col.find().sort("timestamp", -1).limit(limit))
