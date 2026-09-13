from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

ann_col = db["announcements"]

def now():
    return datetime.utcnow().isoformat()

def get_all():
    return list(ann_col.find().sort("time", -1))

def create(title, content, channel_id):
    ann_col.insert_one({
        "time": now(),
        "title": title,
        "content": content,
        "channel_id": channel_id
    })

def set_channel(channel_id):
    ann_col.update_one({}, {"$set": {"default_channel": channel_id}}, upsert=True)
