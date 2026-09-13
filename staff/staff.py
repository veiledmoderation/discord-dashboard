from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client.veilmodwebsite

staff_col = db.staff
reports_col = db.staff_reports

def get_all_staff():
    return list(staff_col.find())

def get_staff(user_id):
    return staff_col.find_one({"user_id": user_id})

def get_staff_reports(user_id):
    return list(reports_col.find({"user_id": user_id}))

def get_report(report_id):
    return reports_col.find_one({"_id": report_id})
