from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

appeals_col = db["appeals"]
appeal_messages_col = db["appeal_messages"]

def now():
    return datetime.utcnow().isoformat()

def get_all_appeals():
    return list(appeals_col.find())

def get_appeal(appeal_id):
    return appeals_col.find_one({"id": appeal_id})

def add_reply(appeal_id, text, author="Staff"):
    appeal_messages_col.insert_one({
        "appeal_id": appeal_id,
        "time": now(),
        "text": text,
        "author": author
    })
    appeals_col.update_one(
        {"id": appeal_id},
        {"$push": {"messages": {"time": now(), "text": text, "author": author}}}
    )

def update_status(appeal_id, status):
    appeals_col.update_one({"id": appeal_id}, {"$set": {"status": status}})

def assign_staff(appeal_id, staff_id, staff_name):
    appeals_col.update_one(
        {"id": appeal_id},
        {
            "$set": {
                "assigned_staff_id": staff_id,
                "assigned_staff_name": staff_name,
            }
        },
    )
