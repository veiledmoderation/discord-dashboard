import json
import os

FILE = "departments.json"


def load_departments():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        return json.load(f)


def save_departments(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_department(user_id):
    data = load_departments()
    return data.get(str(user_id), None)


def set_department(user_id, department):
    data = load_departments()
    data[str(user_id)] = department
    save_departments(data)
