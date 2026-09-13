from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client.veilmodwebsite

appeals_col = db.appeals

def get_all_appeals():
    return list(appeals_col.find())

def get_appeal(appeal_id):
    return appeals_col.find_one({"_id": appeal_id})
