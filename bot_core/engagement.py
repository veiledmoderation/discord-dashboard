# ============================================================
# ENGAGEMENT SYSTEM — Matches EXACTLY what app.py expects
# ============================================================

from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

events_col = db["events"]


# ============================================================
# Create Event
# ============================================================

def create_event(staff_name: str, event_type: str, description: str):
    """
    Creates a new engagement event and returns the event object.
    """

    event = {
        "id": events_col.count_documents({}) + 1,
        "staff_name": staff_name,
        "event_type": event_type,
        "description": description,
        "status": "open",
        "timestamp": datetime.utcnow().isoformat()
    }

    events_col.insert_one(event)
    return event


# ============================================================
# Load Events
# ============================================================

def load_events():
    """
    Returns all engagement events sorted by newest first.
    """
    return list(events_col.find().sort("id", -1))


# ============================================================
# Close Event
# ============================================================

def close_event(event_id: int):
    """
    Marks an engagement event as closed.
    """
    events_col.update_one(
        {"id": event_id},
        {"$set": {"status": "closed"}}
    )
