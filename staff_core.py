from pymongo import MongoClient
import os
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

staff_col = db["staff"]
staff_reports_col = db["staff_reports"]
staff_report_notes_col = db["staff_report_notes"]

def now():
    return datetime.utcnow().isoformat()

def get_all_staff():
    return list(staff_col.find())

def get_staff(user_id):
    return staff_col.find_one({"user_id": user_id})

def get_staff_activity(user_id):
    staff = get_staff(user_id)
    return {
        "activity": staff.get("activity", []),
        "tickets": staff.get("tickets", []),
        "mod_actions": staff.get("mod_actions", []),
    }

def get_all_reports():
    return list(staff_reports_col.find())

def get_report(report_id):
    return staff_reports_col.find_one({"id": report_id})

def add_report_note(report_id, text, author="HeadOfStaff+"):
    staff_report_notes_col.insert_one({
        "report_id": report_id,
        "time": now(),
        "text": text,
        "author": author
    })
    staff_reports_col.update_one(
        {"id": report_id},
        {"$push": {"notes": {"time": now(), "text": text, "author": author}}}
    )

def update_report_status(report_id, status):
    staff_reports_col.update_one({"id": report_id}, {"$set": {"status": status}})

def assign_report(report_id, staff_id, staff_name):
    staff_reports_col.update_one(
        {"id": report_id},
        {
            "$set": {
                "assigned_staff_id": staff_id,
                "assigned_staff_name": staff_name,
            }
        },
    )
