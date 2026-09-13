from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

tickets_col = db["tickets"]
ticket_messages_col = db["ticket_messages"]
tickets_evidence_col = db["tickets_evidence"]
tickets_transcripts_col = db["tickets_transcripts"]

def now():
    return datetime.utcnow().isoformat()

def get_all_tickets():
    return list(tickets_col.find())

def get_ticket(ticket_id):
    return tickets_col.find_one({"id": ticket_id})

def add_reply(ticket_id, text, author="Staff"):
    ticket_messages_col.insert_one({
        "ticket_id": ticket_id,
        "time": now(),
        "text": text,
        "author": author
    })

def update_status(ticket_id, status):
    tickets_col.update_one({"id": ticket_id}, {"$set": {"status": status}})

def update_priority(ticket_id, priority):
    tickets_col.update_one({"id": ticket_id}, {"$set": {"priority": priority}})

def add_evidence(ticket_id, url, note=""):
    tickets_evidence_col.insert_one({
        "ticket_id": ticket_id,
        "url": url,
        "note": note,
        "time": now()
    })

def get_messages(ticket_id):
    return list(ticket_messages_col.find({"ticket_id": ticket_id}).sort("time", 1))

def get_evidence(ticket_id):
    return list(tickets_evidence_col.find({"ticket_id": ticket_id}).sort("time", -1))

def generate_transcript(ticket_id):
    ticket = get_ticket(ticket_id) or {}
    messages = get_messages(ticket_id)
    transcript = {
        "ticket_id": ticket_id,
        "subject": ticket.get("subject", ""),
        "username": ticket.get("username", ""),
        "messages": messages,
        "generated_at": now(),
    }
    tickets_transcripts_col.insert_one(transcript)
    return transcript
