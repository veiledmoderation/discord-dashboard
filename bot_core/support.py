# ============================================================
# SUPPORT SYSTEM — Matches EXACTLY what app.py expects
# ============================================================

from pymongo import MongoClient
import os

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

tickets_col = db["tickets"]


# ============================================================
# Create Ticket
# ============================================================

def create_ticket(user_id: int, username: str, issue_type: str, description: str):
    """
    Creates a new support ticket and returns the ticket object.
    """

    ticket = {
        "id": tickets_col.count_documents({}) + 1,
        "user_id": user_id,
        "username": username,
        "issue_type": issue_type,
        "description": description,
        "status": "open",
        "messages": [],
    }

    tickets_col.insert_one(ticket)
    return ticket


# ============================================================
# Load Tickets
# ============================================================

def load_tickets():
    """
    Returns all tickets sorted by ID descending.
    """
    return list(tickets_col.find().sort("id", -1))


# ============================================================
# Close Ticket
# ============================================================

def close_ticket(ticket_id: int):
    """
    Marks a ticket as closed.
    """
    tickets_col.update_one(
        {"id": ticket_id},
        {"$set": {"status": "closed"}}
    )
