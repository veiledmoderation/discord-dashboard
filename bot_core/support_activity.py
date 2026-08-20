# ============================================================
# SUPPORT ACTIVITY — Matches EXACTLY what app.py expects
# ============================================================

from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

support_activity_col = db["support_activity"]


# ============================================================
# Record Support Activity
# ============================================================

def record_activity(staff_name: str, action: str):
    """
    Records a support staff activity such as creating or closing a ticket.
    """

    entry = {
        "staff_name": staff_name,
        "action": action,
        "timestamp": datetime.utcnow().isoformat()
    }

    support_activity_col.insert_one(entry)
    return entry


# ============================================================
# Load Support Activity (optional helper)
# ============================================================

def load_activity(limit: int = 50):
    """
    Returns recent support activity entries.
    Not required by app.py, but useful for future pages.
    """
    return list(support_activity_col.find().sort("timestamp", -1).limit(limit))
