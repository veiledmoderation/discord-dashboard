from pymongo import MongoClient
import os

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

autorole_col = db["autorole"]


def get_config():
    return autorole_col.find_one() or {"role_id": None}


def update_config(role_id):
    autorole_col.update_one({}, {"$set": {"role_id": role_id}}, upsert=True)
