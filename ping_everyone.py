from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

ping_col = db["ping"]


def get_all():
    return list(ping_col.find().sort("time", -1))


def send_ping(channel_id, message):
    ping_col.insert_one({
        "channel_id": channel_id,
        "message": message,
        "time": datetime.utcnow().isoformat()
    })
