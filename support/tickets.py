from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client.veilmodwebsite

tickets_col = db.tickets

def get_all_tickets():
    return list(tickets_col.find())

def get_ticket(ticket_id):
    return tickets_col.find_one({"_id": ticket_id})

def get_evidence(ticket_id):
    t = tickets_col.find_one({"_id": ticket_id})
    return t.get("evidence", [])
