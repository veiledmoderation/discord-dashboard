import json
import os
from datetime import datetime

FILE = "engagement_activity.json"


def load_activity():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r") as f:
        return json.load(f)


def save_activity(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


def record_engagement_activity(staff_name, action):
    activity = load_activity()

    entry = {
        "staff": staff_name,
        "action": action,
        "timestamp": datetime.now().isoformat()
    }

    activity.append(entry)
    save_activity(activity)
