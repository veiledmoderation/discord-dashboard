# ============================================================
# SUPPORT LOGS — Matches EXACTLY what app.py expects
# ============================================================

from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

support_logs_col = db["support_logs"]


# ============================================================
# Log Support Action
# ============================================================

def log_support_action(staff_name: str, action: str, ticket_id: int):
    """
    Logs a support action such as creating or closing a ticket.
    """

    log_entry = {
        "staff_name": staff_name,
        "action": action,
        "ticket_id": ticket_id,
        "timestamp": datetime.utcnow().isoformat()
    }

    support_logs_col.insert_one(log_entry)
    return log_entry


# ============================================================
# Load Support Logs (optional helper)
# ============================================================

def load_support_logs(limit: int = 50):
    """
    Returns recent support logs.
    Not required by app.py, but useful for future pages.
    """
    return list(support_logs_col.find().sort("timestamp", -1).limit(limit))
