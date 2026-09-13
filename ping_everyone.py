from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

ping_col = db["ping_everyone"]

def now():
    return datetime.utcnow().isoformat()

def get_all():
    return list(ping_col.find().sort("time", -1))

def send_ping(channel_id, message):
    ping_col.insert_one({
        "time": now(),
        "text": f"[{channel_id}] {message}"
    })
