from flask import Flask, render_template, request, redirect, jsonify
from pymongo import MongoClient
from datetime import datetime
from flask_socketio import SocketIO
from bson import ObjectId
import os

# ===== FLASK APP =====
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "secret")

# ===== SOCKET.IO =====
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
socketio = SocketIO(app, cors_allowed_origins="*", message_queue=redis_url)

# ===== IMPORT MODULES =====
import moderation
import moderation_logs
import moderation_activity
import qa
import autorole
import announcements
import ping_everyone
import support_tickets
import support_appeals
import staff_core

# ===== MONGO =====
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

# Collections
staff_col = db["staff"]
tickets_col = db["tickets"]
ticket_messages_col = db["ticket_messages"]
tickets_transcripts_col = db["tickets_transcripts"]
tickets_evidence_col = db["tickets_evidence"]

dashboard_feed = db["dashboard_feed"]
tickets_feed = db["tickets_feed"]
qna_feed = db["qna_feed"]
autorole_feed = db["autorole_feed"]
announcement_feed = db["announcement_feed"]
ping_feed = db["ping_feed"]
settings_col = db["settings"]

appeals_col = db["appeals"]
appeal_messages_col = db["appeal_messages"]
appeals_feed = db["appeals_feed"]

staff_reports_col = db["staff_reports"]
staff_report_notes_col = db["staff_report_notes"]
staff_reports_feed = db["staff_reports_feed"]

sla_feed = db["sla_feed"]
priority_feed = db["priority_feed"]
assignment_feed = db["assignment_feed"]

# ===== UTIL =====
def now():
    return datetime.utcnow().isoformat()

def feed(col, text, channel=None):
    doc = {"time": now(), "text": text}
    col.insert_one(doc)
    if channel:
        socketio.emit(channel, doc, broadcast=True)

def fetch_feed(col, limit=30):
    return list(col.find().sort("time", -1).limit(limit))

# ===== FIX: ObjectId → string =====
def fix_ids(obj):
    if isinstance(obj, list):
        return [fix_ids(item) for item in obj]
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            if isinstance(v, ObjectId):
                new[k] = str(v)
            else:
                new[k] = fix_ids(v)
        return new
    return obj

# ===== SLA =====
def calculate_sla(opened_date):
    try:
        opened = datetime.strptime(opened_date, "%Y-%m-%d")
    except Exception:
        return "unknown"
    delta = datetime.utcnow() - opened
    hours = delta.total_seconds() / 3600
    if hours < 24:
        return "green"
    elif hours < 48:
        return "yellow"
    return "red"

# ===== ROUTES (unchanged except JSON fixes) =====

@app.route("/")
@app.route("/dashboard")
def dashboard():
    stats = {
        "total_users": staff_col.count_documents({}),
        "tickets_today": tickets_col.count_documents({"opened_date": datetime.utcnow().strftime("%Y-%m-%d")}),
        "active_staff": staff_col.count_documents({"status": "active"}),
        "mod_actions_today": dashboard_feed.count_documents({}),
    }
    return render_template("dashboard.html", stats=stats)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin":
            return redirect("/dashboard")
        error = "Invalid login."
    return render_template("login.html", error=error)

@app.route("/staff")
def staff():
    return render_template("staff_list.html", staff=staff_core.get_all_staff())

@app.route("/staff/profile/<user_id>")
def staff_profile(user_id):
    staff = staff_core.get_staff(user_id)
    if not staff:
        return render_template("error.html", message="Staff member not found")
    return render_template(
        "staff_profile.html",
        staff=staff,
        feedback=staff.get("feedback", []),
        activity_log=staff.get("activity", []),
        tickets_month=staff.get("tickets_month", 0),
        tickets_total=staff.get("tickets_total", 0),
        rating_avg=staff.get("rating_avg", 0),
        rating_count=staff.get("rating_count", 0),
    )

@app.route("/staff/activity/<user_id>")
def staff_activity_page(user_id):
    staff = staff_core.get_staff(user_id)
    if not staff:
        return render_template("error.html", message="Staff member not found")
    data = staff_core.get_staff_activity(user_id)
    return render_template(
        "staff_activity.html",
        staff=staff,
        activity=data["activity"],
        tickets=data["tickets"],
        mod_actions=data["mod_actions"],
    )

@app.route("/departments")
def departments_page():
    deps = ["Support Department", "Engagement Department", "Multi Department"]
    data = [{"name": d, "count": staff_col.count_documents({"department": d})} for d in deps]
    return render_template("departments.html", departments=data)

@app.route("/support")
def support_page():
    return render_template("support.html")

@app.route("/tickets")
def tickets_page():
    all_tickets = support_tickets.get_all_tickets()
    for t in all_tickets:
        opened_date = t.get("opened_date", datetime.utcnow().strftime("%Y-%m-%d"))
        t["sla"] = calculate_sla(opened_date)
    return render_template("tickets.html", tickets=all_tickets)

@app.route("/tickets/view/<ticket_id>", methods=["GET", "POST"])
def ticket_view(ticket_id):
    ticket = support_tickets.get_ticket(ticket_id)
    if not ticket:
        return render_template("error.html", message="Ticket not found")

    if request.method == "POST":
        action = request.form.get("action")
        if action == "reply":
            support_tickets.add_reply(ticket_id, request.form["message"], author="Staff")
            feed(tickets_feed, f"Reply added to ticket #{ticket_id}", "tickets_feed")
        elif action == "status":
            new_status = request.form.get("status")
            support_tickets.update_status(ticket_id, new_status)
            feed(tickets_feed, f"Status for ticket #{ticket_id} set to {new_status}", "tickets_feed")
            feed(sla_feed, f"SLA updated for ticket #{ticket_id}", "sla_feed")
        return redirect(f"/tickets/view/{ticket_id}")

    return render_template(
        "ticket_view.html",
        ticket=ticket,
        messages=support_tickets.get_messages(ticket_id),
        evidence=support_tickets.get_evidence(ticket_id),
    )

@app.route("/tickets/transcript/<ticket_id>")
def ticket_transcript(ticket_id):
    return jsonify(fix_ids(support_tickets.generate_transcript(ticket_id)))

@app.route("/appeals")
def appeals_page():
    return render_template("appeals.html", appeals=support_appeals.get_all_appeals())

@app.route("/appeals/view/<appeal_id>", methods=["GET", "POST"])
def appeal_view(appeal_id):
    appeal = support_appeals.get_appeal(appeal_id)
    if not appeal:
        return render_template("error.html", message="Appeal not found")

    if request.method == "POST":
        action = request.form.get("action")
        if action == "reply":
            support_appeals.add_reply(appeal_id, request.form["message"], author="Staff")
            feed(appeals_feed, f"Reply added to appeal #{appeal_id}", "appeals_feed")
        elif action == "status":
            new_status = request.form.get("status")
            support_appeals.update_status(appeal_id, new_status)
            feed(appeals_feed, f"Status for appeal #{appeal_id} set to {new_status}", "appeals_feed")
        return redirect(f"/appeals/view/{appeal_id}")

    return render_template("appeal_view.html", appeal=appeal, messages=appeal.get("messages", []))

@app.route("/staff-reports")
def staff_reports_page():
    return render_template("staff_reports.html", reports=staff_core.get_all_reports())

@app.route("/staff-reports/view/<report_id>", methods=["GET", "POST"])
def staff_report_view(report_id):
    report = staff_core.get_report(report_id)
    if not report:
        return render_template("error.html", message="Staff report not found")

    if request.method == "POST":
        action = request.form.get("action")
        if action == "note":
            staff_core.add_report_note(report_id, request.form["note"], author="HeadOfStaff+")
            feed(staff_reports_feed, f"Note added to staff report #{report_id}", "staff_reports_feed")
        elif action == "status":
            new_status = request.form.get("status")
            staff_core.update_report_status(report_id, new_status)
            feed(staff_reports_feed, f"Status for staff report #{report_id} set to {new_status}", "staff_reports_feed")
        return redirect(f"/staff-reports/view/{report_id}")

    return render_template("staff_report_view.html", report=report, notes=report.get("notes", []))

@app.route("/settings")
def settings():
    return render_template("settings.html", settings=settings_col.find_one() or {})

@app.route("/settings/update", methods=["POST"])
def settings_update():
    new_settings = {
        "prefix": request.form["prefix"],
        "log_channel": request.form["log_channel"],
        "staff_role": request.form["staff_role"],
        "ticket_category": request.form["ticket_category"],
    }
    settings_col.update_one({}, {"$set": new_settings}, upsert=True)
    return redirect("/settings")

# ===== LIVE API FEEDS (patched) =====
@app.route("/api/live/dashboard")
def api_dashboard():
    return jsonify(fix_ids(fetch_feed(dashboard_feed)))

@app.route("/api/live/tickets")
def api_tickets():
    return jsonify(fix_ids(fetch_feed(tickets_feed)))

@app.route("/api/live/ticket")
def api_ticket():
    return jsonify(fix_ids(fetch_feed(ticket_messages_col)))

@app.route("/api/live/qna")
def api_qna():
    return jsonify(fix_ids(fetch_feed(qna_feed)))

@app.route("/api/live/autorole")
def api_autorole():
    return jsonify(fix_ids(fetch_feed(autorole_feed)))

@app.route("/api/live/announcement")
def api_announcement():
    return jsonify(fix_ids(fetch_feed(announcement_feed)))

@app.route("/api/live/ping")
def api_ping():
    return jsonify(fix_ids(fetch_feed(ping_feed)))

@app.route("/api/live/appeals")
def api_appeals():
    return jsonify(fix_ids(fetch_feed(appeals_feed)))

@app.route("/api/live/staff-reports")
def api_staff_reports():
    return jsonify(fix_ids(fetch_feed(staff_reports_feed)))

@app.route("/api/live/sla")
def api_sla():
    return jsonify(fix_ids(fetch_feed(sla_feed)))

@app.route("/api/live/priority")
def api_priority():
    return jsonify(fix_ids(fetch_feed(priority_feed)))

@app.route("/api/live/assignment")
def api_assignment():
    return jsonify(fix_ids(fetch_feed(assignment_feed)))

# ===== CONFIG API =====
@app.route("/api/config", methods=["GET"])
def api_get_config():
    return jsonify(fix_ids(settings_col.find_one() or {}))

@app.route("/api/config", methods=["POST"])
def api_save_config():
    payload = request.json or {}
    settings_col.update_one({}, {"$set": payload}, upsert=True)
    return jsonify({"status": "ok"})

# ===== ERROR =====
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", message="Page not found"), 404

# ===== RUN =====
def start_dashboard(host="0.0.0.0", port=None, debug=False):
    if port is None:
        port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host=host, port=port, debug=debug)

if __name__ == "__main__":
    start_dashboard(debug=True)
