from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

ANNOUNCEMENTS = db["announcements"]
CONFIG = db["config"]

def get_all():
    return list(ANNOUNCEMENTS.find().sort("timestamp", -1))

def create(title, content, channel_id):
    ANNOUNCEMENTS.insert_one({
        "title": title,
        "content": content,
        "channel_id": channel_id,
        "timestamp": datetime.utcnow().isoformat()
    })

def set_channel(channel_id):
    CONFIG.update_one(
        {"server_id": os.getenv("RITUALS_GUILD_ID")},
        {"$set": {"announcement_channel": channel_id}},
        upsert=True
    )

def get_channel():
    cfg = CONFIG.find_one({"server_id": os.getenv("RITUALS_GUILD_ID")}) or {}
    return cfg.get("announcement_channel")
