import json
import os
from datetime import datetime

FILE = "moderation_logs.json"


def load_logs():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r") as f:
        return json.load(f)


def filter_logs(staff=None, target=None, action=None, start_date=None, end_date=None):
    logs = load_logs()
    result = logs

    if staff:
        result = [l for l in result if l["staff"].lower() == staff.lower()]

    if target:
        result = [l for l in result if l["target_user"].lower() == target.lower()]

    if action:
        result = [l for l in result if l["action"].lower() == action.lower()]

    if start_date:
        sd = datetime.fromisoformat(start_date)
        result = [l for l in result if datetime.fromisoformat(l["timestamp"]) >= sd]

    if end_date:
        ed = datetime.fromisoformat(end_date)
        result = [l for l in result if datetime.fromisoformat(l["timestamp"]) <= ed]

    return result


def search_logs(query):
    logs = load_logs()
    query = query.lower()

    return [
        l for l in logs
        if query in l["staff"].lower()
        or query in l["target_user"].lower()
        or query in l["action"].lower()
        or query in l["timestamp"].lower()
    ]


def sort_logs(logs, sort_type):
    if sort_type == "newest":
        return sorted(logs, key=lambda x: x["timestamp"], reverse=True)
    if sort_type == "oldest":
        return sorted(logs, key=lambda x: x["timestamp"])
    if sort_type == "staff":
        return sorted(logs, key=lambda x: x["staff"].lower())
    if sort_type == "action":
        return sorted(logs, key=lambda x: x["action"].lower())
    return logs


def paginate(logs, page, per_page=25):
    start = (page - 1) * per_page
    end = start + per_page
    return logs[start:end]
