from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

qa_col = db["qa"]


def get_all_questions():
    return list(qa_col.find())


def get_question(question_id):
    return qa_col.find_one({"id": question_id})


def update_answer(question_id, new_answer):
    qa_col.update_one(
        {"id": question_id},
        {"$set": {
            "answer": new_answer,
            "updated": datetime.utcnow().isoformat()
        }}
    )
