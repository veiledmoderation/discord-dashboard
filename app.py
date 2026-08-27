from flask import Flask, render_template, request, redirect, jsonify
from pymongo import MongoClient
import os
from datetime import datetime

# ===== IMPORT BACKEND MODULES =====
import moderation
import moderation_logs
import moderation_activity
import qa
import autorole
import announcements
import ping_everyone

# ===== FLASK APP =====
app = Flask(__name__)

# ===== MONGO SETUP =====
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

# Collections
staff_col = db["staff"]
tickets_col = db["tickets"]
ticket_messages_col = db["ticket_messages"]
dashboard_feed = db["dashboard_feed"]
tickets_feed = db["tickets_feed"]
qna_feed = db["qna_feed"]
autorole_feed = db["autorole_feed"]
announcement_feed = db["announcement_feed"]
ping_feed = db["ping_feed"]
settings_col = db["settings"]

# ===== UTIL =====
def now():
    return datetime.utcnow().isoformat()

def feed(col, text):
    col.insert_one({"time": now(), "text": text})

def fetch_feed(col, limit=30):
    return list(col.find().sort("time", -1).limit(limit))

# ===== HOME / DASHBOARD =====
@app.route("/")
@app.route("/dashboard")
def dashboard():
    stats = {
        "total_users": staff_col.count_documents({}),
        "tickets_today": tickets_col.count_documents({"opened_date": datetime.utcnow().strftime("%Y-%m-%d")}),
        "active_staff": staff_col.count_documents({"status": "active"}),
        "mod_actions_today": dashboard_feed.count_documents({})
    }
    return render_template("dashboard.html", stats=stats)

# ===== LOGIN =====
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":
            return redirect("/dashboard")
        else:
            error = "Invalid login."

    return render_template("login.html", error=error)

# ===== STAFF PORTAL =====
@app.route("/staff")
def staff():
    all_staff = list(staff_col.find())
    return render_template("staff.html", staff=all_staff)

@app.route("/staff/profile/<user_id>")
def staff_profile(user_id):
    staff = staff_col.find_one({"user_id": user_id})
    feedback = staff.get("feedback", [])
    activity_log = staff.get("activity", [])
    tickets_month = staff.get("tickets_month", 0)
    tickets_total = staff.get("tickets_total", 0)
    rating_avg = staff.get("rating_avg", 0)
    rating_count = staff.get("rating_count", 0)

    return render_template(
        "staff_profile.html",
        staff=staff,
        feedback=feedback,
        activity_log=activity_log,
        tickets_month=tickets_month,
        tickets_total=tickets_total,
        rating_avg=rating_avg,
        rating_count=rating_count
    )

@app.route("/staff/activity/<user_id>")
def staff_activity_page(user_id):
    staff = staff_col.find_one({"user_id": user_id})
    activity = staff.get("activity", [])
    tickets = staff.get("tickets", [])
    mod_actions = staff.get("mod_actions", [])

    return render_template(
        "staff_activity.html",
        staff=staff,
        activity=activity,
        tickets=tickets,
        mod_actions=mod_actions
    )

# ===== TICKETS =====
@app.route("/tickets")
def tickets_page():
    all_tickets = list(tickets_col.find())
    return render_template("tickets.html", tickets=all_tickets)

@app.route("/tickets/view/<ticket_id>")
def ticket_view(ticket_id):
    ticket = tickets_col.find_one({"id": ticket_id})
    return render_template("ticket_view.html", ticket=ticket)

@app.route("/tickets/reply/<ticket_id>", methods=["POST"])
def ticket_reply(ticket_id):
    msg = request.form["message"]
    ticket_messages_col.insert_one({
        "ticket_id": ticket_id,
        "time": now(),
        "text": msg,
        "author": "Staff"
    })

    feed(tickets_feed, f"Reply added to ticket #{ticket_id}")
    return redirect(f"/tickets/view/{ticket_id}")

# ===== SETTINGS =====
@app.route("/settings")
def settings():
    settings = settings_col.find_one() or {}
    return render_template("settings.html", settings=settings)

@app.route("/settings/update", methods=["POST"])
def settings_update():
    new_settings = {
        "prefix": request.form["prefix"],
        "log_channel": request.form["log_channel"],
        "staff_role": request.form["staff_role"],
        "ticket_category": request.form["ticket_category"]
    }
    settings_col.update_one({}, {"$set": new_settings}, upsert=True)
    return redirect("/settings")

# ===== LOGS =====
@app.route("/logs")
def logs():
    mod_logs = list(dashboard_feed.find().sort("time", -1))
    ticket_logs = list(tickets_feed.find().sort("time", -1))
    system_logs = list(qna_feed.find().sort("time", -1))
    return render_template("logs.html", mod_logs=mod_logs, ticket_logs=ticket_logs, system_logs=system_logs)

# ===== MODERATION ROUTES =====
@app.route("/moderation/action", methods=["POST"])
def moderation_action():
    staff_name = request.form["staff_name"]
    action_type = request.form["action_type"]
    target_user = request.form["target_user"]
    reason = request.form.get("reason", "")

    moderation.add_action(staff_name, action_type, target_user, reason)
    moderation_logs.log_mod_action(staff_name, action_type, target_user, reason)
    moderation_activity.record_mod_activity(staff_name, f"{action_type} {target_user}")

    feed(dashboard_feed, f"{staff_name} {action_type} {target_user} ({reason})")
    return redirect("/logs")

# ===== Q&A ROUTES =====
@app.route("/qna")
def qna_page():
    questions = qa.get_all_questions()
    return render_template("qa.html", questions=questions)

@app.route("/qna/edit/<question_id>", methods=["GET", "POST"])
def qna_edit(question_id):
    if request.method == "POST":
        new_answer = request.form["answer"]
        qa.update_answer(question_id, new_answer)
        feed(qna_feed, f"Q&A updated: {question_id}")
        return redirect("/qna")

    question = qa.get_question(question_id)
    return render_template("qa_edit.html", question=question)

# ===== AUTOROLE ROUTES =====
@app.route("/autorole")
def autorole_page():
    config = autorole.get_config()
    return render_template("auto_roles.html", config=config)

@app.route("/autorole/update", methods=["POST"])
def autorole_update():
    role_id = request.form["role_id"]
    autorole.update_config(role_id)
    feed(autorole_feed, f"Autorole updated: {role_id}")
    return redirect("/autorole")

# ===== ANNOUNCEMENTS ROUTES =====
@app.route("/announcements")
def announcements_page():
    all_ann = announcements.get_all()

    # Channels saved by bot in settings_col
    settings = settings_col.find_one() or {}
    channels = settings.get("guild_channels", [])

    return render_template("announcements.html", announcements=all_ann, channels=channels)

@app.route("/announcements/create", methods=["POST"])
def announcements_create():
    title = request.form["title"]
    content = request.form["content"]
    channel_id = request.form["channel_id"]

    announcements.create(title, content, channel_id)
    announcements.set_channel(channel_id)

    feed(announcement_feed, f"Announcement created: {title}")
    return redirect("/announcements")

# ===== PING EVERYONE ROUTES =====
@app.route("/ping-everyone")
def ping_page():
    pings = ping_everyone.get_all()
    return render_template("ping_everyone.html", pings=pings)

@app.route("/ping-everyone/send", methods=["POST"])
def ping_send():
    channel_id = request.form["channel_id"]
    message = request.form["message"]
    ping_everyone.send_ping(channel_id, message)
    feed(ping_feed, f"Ping sent to {channel_id}: {message}")
    return redirect("/ping-everyone")

# ===== API LIVE FEEDS =====
@app.route("/api/live/dashboard")
def api_dashboard():
    return jsonify(fetch_feed(dashboard_feed))

@app.route("/api/live/tickets")
def api_tickets():
    return jsonify(fetch_feed(tickets_feed))

@app.route("/api/live/ticket")
def api_ticket():
    return jsonify(fetch_feed(ticket_messages_col))

@app.route("/api/live/qna")
def api_qna():
    return jsonify(fetch_feed(qna_feed))

@app.route("/api/live/autorole")
def api_autorole():
    return jsonify(fetch_feed(autorole_feed))

@app.route("/api/live/announcement")
def api_announcement():
    return jsonify(fetch_feed(announcement_feed))

@app.route("/api/live/ping")
def api_ping():
    return jsonify(fetch_feed(ping_feed))

# ===== CONFIG API (bot + dashboard sync) =====
@app.route("/api/config", methods=["GET"])
def api_get_config():
    settings = settings_col.find_one() or {}
    return jsonify(settings)

@app.route("/api/config", methods=["POST"])
def api_save_config():
    payload = request.json or {}
    settings_col.update_one({}, {"$set": payload}, upsert=True)
    return jsonify({"status": "ok"})

# ===== ERROR PAGE =====
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", message="Page not found"), 404

# ===== RUN / DASHBOARD STARTER =====
def start_dashboard(host="0.0.0.0", port=None, debug=False):
    if port is None:
        port = int(os.environ.get("PORT", 5000))
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    start_dashboard(debug=True)
