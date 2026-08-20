import os
import requests
from flask import Flask, redirect, request, session, render_template
from pymongo import MongoClient

from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, BOT_TOKEN

from bot_core.discord_api import (
    get_user,
    get_guild_roles,
    get_member,
    get_guild_members,
)

from bot_core.permissions import (
    can_access_support,
    can_access_engagement,
    can_access_moderation,
    can_access_dashboard,
    can_access_qna,
)

from bot_core.support import create_ticket, load_tickets, close_ticket
from bot_core.support_logs import log_support_action
from bot_core.support_activity import record_activity

from bot_core.engagement import create_event, load_events, close_event
from bot_core.engagement_logs import log_engagement_action
from bot_core.engagement_activity import record_engagement_activity

from bot_core.moderation import add_action
from bot_core.moderation_logs import log_mod_action
from bot_core.moderation_activity import record_mod_activity

from bot_core.mute import (
    get_muted_role,
    set_muted_role,
    save_user_roles,
    restore_user_roles,
)

app = Flask(__name__)
app.secret_key = "super-secret-key"

RITUALS_ID = int(os.getenv("RITUALS_GUILD_ID", "0"))

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]
config_col = db["config"]

# Q&A collections
questions_col = db["questions"]
answers_col = db["answers"]


# ============================
# Helpers
# ============================

def require_login():
    if "user" not in session:
        return redirect("/login")
    return None


def ensure_rituals(guild_id):
    if str(guild_id) != str(RITUALS_ID):
        return render_template("unauthorized.html", title="Unauthorized")
    return None


def get_member_for_session(guild_id):
    return get_member(guild_id, session["user"]["id"])


def get_config():
    cfg = config_col.find_one({"server_id": RITUALS_ID})
    if not cfg:
        cfg = {"server_id": RITUALS_ID}
        config_col.insert_one(cfg)
    return cfg


# ============================
# Auth routes
# ============================

@app.route("/login")
def login():
    return render_template("login.html", title="Login")


@app.route("/auth/discord")
def discord_auth():
    return redirect(
        "https://discord.com/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&scope=identify%20guilds"
    )


@app.route("/callback")
def callback():
    code = request.args.get("code")

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify guilds",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    resp = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    token = resp.json().get("access_token")

    session["token"] = token
    session["user"] = get_user(token)

    return redirect("/dashboard")


# ============================
# Core navigation
# ============================

@app.route("/")
def home():
    return redirect("/login")


@app.route("/dashboard")
def dashboard():
    if require_login():
        return require_login()

    member = get_member_for_session(RITUALS_ID)
    if not member or not can_access_dashboard(member):
        return render_template("unauthorized.html", title="Unauthorized")

    guilds = [{"id": RITUALS_ID, "name": "Rituals"}]

    cfg = get_config()

    return render_template(
        "dashboard.html",
        guilds=guilds,
        user=session["user"],
        config=cfg,
        title="Dashboard",
    )


@app.route("/servers")
def servers():
    if require_login():
        return require_login()

    member = get_member_for_session(RITUALS_ID)
    if not member or not can_access_dashboard(member):
        return render_template("unauthorized.html", title="Unauthorized")

    guilds = [{"id": RITUALS_ID, "name": "Rituals"}]

    return render_template(
        "servers.html",
        guilds=guilds,
        user=session["user"],
        title="Servers",
    )


@app.route("/commands")
def commands():
    if require_login():
        return require_login()

    member = get_member_for_session(RITUALS_ID)
    if not member or not can_access_dashboard(member):
        return render_template("unauthorized.html", title="Unauthorized")

    return render_template(
        "commands.html",
        user=session["user"],
        title="Commands",
    )


@app.route("/settings")
def settings():
    if require_login():
        return require_login()

    member = get_member_for_session(RITUALS_ID)
    if not member or not can_access_dashboard(member):
        return render_template("unauthorized.html", title="Unauthorized")

    cfg = get_config()

    return render_template(
        "settings.html",
        user=session["user"],
        config=cfg,
        title="Settings",
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/server/<guild_id>")
def server_page(guild_id):
    if require_login():
        return require_login()

    if ensure_rituals(guild_id):
        return ensure_rituals(guild_id)

    member = get_member_for_session(guild_id)
    if not member or not can_access_dashboard(member):
        return render_template("unauthorized.html", title="Unauthorized")

    return render_template(
        "server.html",
        guild_id=guild_id,
        title="Server Dashboard",
    )


# ============================
# Support tools
# ============================

@app.route("/server/<guild_id>/support")
def support_tools(guild_id):
    if require_login():
        return require_login()

    if ensure_rituals(guild_id):
        return ensure_rituals(guild_id)

    member = get_member_for_session(guild_id)
    if not member or not can_access_support(member):
        return render_template("unauthorized.html", title="Unauthorized")

    tickets = load_tickets()

    return render_template(
        "support_tools.html",
        tickets=tickets,
        guild_id=guild_id,
        title="Support Tools",
    )


@app.route("/server/<guild_id>/support/create", methods=["POST"])
def support_create(guild_id):
    if require_login():
        return require_login()

    if ensure_rituals(guild_id):
        return ensure_rituals(guild_id)

    member = get_member_for_session(guild_id)
    if not member or not can_access_support(member):
        return render_template("unauthorized.html", title="Unauthorized")

    issue_type = request.form.get("issue_type")
    description = request.form.get("description")

    user = session["user"]

    ticket = create_ticket(
        user_id=user["id"],
        username=user["username"],
        issue_type=issue_type,
        description=description,
    )

    log_support_action(user["username"], "Created Ticket", ticket["id"])
    record_activity(user["username"], "Created Ticket")

    return redirect(f"/server/{guild_id}/support")


@app.route("/server/<guild_id>/support/close/<ticket_id>")
def support_close(guild_id, ticket_id):
    if require_login():
        return require_login()

    if ensure_rituals(guild_id):
        return ensure_rituals(guild_id)

    member = get_member_for_session(guild_id)
    if not member or not can_access_support(member):
        return render_template("unauthorized.html", title="Unauthorized")

    user = session["user"]

    close_ticket(int(ticket_id))
    log_support_action(user["username"], "Closed Ticket", ticket_id)
    record_activity(user["username"], "Closed Ticket")

    return redirect(f"/server/{guild_id}/support")


# ============================
# Engagement tools
# ============================

@app.route("/server/<guild_id>/engagement")
def engagement_tools(guild_id):
    if require_login():
        return require_login()

    if ensure_rituals(guild_id):
        return ensure_rituals(guild_id)

    member = get_member_for_session(guild_id)
    if not member or not can_access_engagement(member):
        return render_template("unauthorized.html", title="Unauthorized")

    events = load_events()

    return render_template(
        "engagement_tools.html",
        events=events,
        guild_id=guild_id,
        title="Engagement Tools",
    )


@app.route("/server/<guild_id>/engagement/create", methods=["POST"])
def engagement_create(guild_id):
    if require_login():
        return require_login()

    if ensure_rituals(guild_id):
        return ensure_rituals(guild_id)

    member = get_member_for_session(guild_id)
    if not member or not can_access_engagement(member):
        return render_template("unauthorized.html", title="Unauthorized")

    event_type = request.form.get("event_type")
    description = request.form.get("description")

    user = session["user"]

    event = create_event(
        staff_name=user["username"],
        event_type=event_type,
        description=description,
    )

    log_engagement_action(user["username"], "Created Event", event["id"])
    record_engagement_activity(user["username"], "Created Event")

    return redirect(f"/server/{guild_id}/engagement")


@app.route("/server/<guild_id>/engagement/close/<event_id>")
def engagement_close(guild_id, event_id):
    if require_login():
        return require_login()

    if ensure_rituals(guild_id):
        return ensure_rituals(guild_id)

    member = get_member_for_session(guild_id)
    if not member or not can_access_engagement(member):
        return render_template("unauthorized.html", title="Unauthorized")

    user = session["user"]

    close_event(int(event_id))
    log_engagement_action(user["username"], "Closed Event", event_id)
    record_engagement_activity(user["username"], "Closed Event")

    return redirect(f"/server/{guild_id}/engagement")


# ============================
# Moderation tools
# ============================

@app.route("/server/<guild_id>/moderation")
def moderation_tools(guild_id):
    if require_login():
        return require_login()

    if ensure_rituals(guild_id):
        return ensure_rituals(guild_id)

    member = get_member_for_session(guild_id)
    if not member or not can_access_moderation(member):
        return render_template("unauthorized.html", title="Unauthorized")

    guild_members = get_guild_members(guild_id)
    muted_role = get_muted_role(guild_id)

    return render_template(
        "moderation_tools.html",
        guild_id=guild_id,
        members=guild_members,
        muted_role=muted_role,
        title="Moderation Tools",
    )


@app.route("/server/<guild_id>/moderation/set-muted-role", methods=["POST"])
def moderation_set_muted_role(guild_id):
    if require_login():
        return require_login()

    if ensure_rituals(guild_id):
        return ensure_rituals(guild_id)

    member = get_member_for_session(guild_id)
    if not member or not can_access_moderation(member):
        return render_template("unauthorized.html", title="Unauthorized")

    role_name = request.form.get("role_name")
    set_muted_role(guild_id, role_name)

    return redirect(f"/server/{guild_id}/moderation")


@app.route("/server/<guild_id>/moderation/warn/<user_id>", methods=["POST"])
def moderation_warn(guild_id, user_id):
    if require_login():
        return require_login()

    if ensure_rituals(guild_id):
        return ensure_rituals(guild_id)

    member = get_member_for_session(guild_id)
    if not member or not can_access_moderation(member):
        return render_template("unauthorized.html", title="Unauthorized")

    reason = request.form.get("reason")
    user = session["user"]

    add_action(user["username"], "Warn", user_id, reason)
    log_mod_action(user["username"], "Warned User", user_id)
    record_mod_activity(user["username"], "Warned User")

    return redirect(f"/server/{guild_id}/moderation")


@app.route("/server/<guild_id>/moderation/kick/<user_id>", methods=["POST"])
def moderation_kick(guild_id, user_id):
    if require_login():
        return require_login()

    if ensure_rituals(guild_id):
        return ensure_rituals(guild_id)

    member = get_member_for_session(guild_id)
    if not member or not can_access_moderation(member):
        return render_template("unauthorized.html", title="Unauthorized")

    reason = request.form.get("reason")
    user = session["user"]

    add_action(user["username"], "Kick", user_id, reason)
    log_mod_action(user["username"], "Kicked User", user_id)
    record_mod_activity(user["username"], "Kicked User")

    return redirect(f"/server/{guild_id}/moderation")


@app.route("/server/<guild_id>/moderation/ban/<user_id>", methods=["POST"])
def moderation_ban(guild_id, user_id):
    if require_login():
        return require_login()

    if ensure_rituals(guild_id):
        return ensure_rituals(guild_id)

    member = get_member_for_session(guild_id)
    if not member or not can_access_moderation(member):
        return render_template("unauthorized.html", title="Unauthorized")

    reason = request.form.get("reason")
    user = session["user"]

    add_action(user["username"], "Ban", user_id, reason)
    log_mod_action(user["username"], "Banned User", user_id)
    record_mod_activity(user["username"], "Banned User")

    return redirect(f"/server/{guild_id}/moderation")


@app.route("/server/<guild_id>/moderation/mute/<user_id>", methods=["POST"])
def moderation_mute(guild_id, user_id):
    if require_login():
        return require_login()

    if ensure_rituals(guild_id):
        return ensure_rituals(guild_id)

    member = get_member_for_session(guild_id)
    if not member or not can_access_moderation(member):
        return render_template("unauthorized.html", title="Unauthorized")

    muted_role = get_muted_role(guild_id)
    if muted_role is None:
        return "Muted role not configured!", 400

    target = get_member(guild_id, user_id)
    current_roles = [r["name"] for r in target["roles"]]

    save_user_roles(guild_id, user_id, current_roles)

    for r in target["roles"]:
        requests.delete(
            f"https://discord.com/api/guilds/{guild_id}/members/{user_id}/roles/{r['id']}",
            headers={"Authorization": f"Bot {BOT_TOKEN}"},
        )

    guild_roles = get_guild_roles(guild_id)
    muted_role_id = next((r["id"] for r in guild_roles if r["name"] == muted_role), None)

    if muted_role_id:
        requests.put(
            f"https://discord.com/api/guilds/{guild_id}/members/{user_id}/roles/{muted_role_id}",
            headers={"Authorization": f"Bot {BOT_TOKEN}"},
        )

    user = session["user"]
    add_action(user["username"], "Mute", user_id, "Muted")
    log_mod_action(user["username"], "Muted User", user_id)
    record_mod_activity(user["username"], "Muted User")

    return redirect(f"/server/{guild_id}/moderation")


@app.route("/server/<guild_id>/moderation/unmute/<user_id>", methods=["POST"])
def moderation_unmute(guild_id, user_id):
    if require_login():
        return require_login()

    if ensure_rituals(guild_id):
        return ensure_rituals(guild_id)

    member = get_member_for_session(guild_id)
    if not member or not can_access_moderation(member):
        return render_template("unauthorized.html", title="Unauthorized")

    muted_role = get_muted_role(guild_id)
    guild_roles = get_guild_roles(guild_id)

    muted_role_id = next((r["id"] for r in guild_roles if r["name"] == muted_role), None)

    if muted_role_id:
        requests.delete(
            f"https://discord.com/api/guilds/{guild_id}/members/{user_id}/roles/{muted_role_id}",
            headers={"Authorization": f"Bot {BOT_TOKEN}"},
        )

    restored_roles = restore_user_roles(guild_id, user_id)

    if restored_roles:
        for role_name in restored_roles:
            role_id = next((r["id"] for r in guild_roles if r["name"] == role_name), None)
            if role_id:
                requests.put(
                    f"https://discord.com/api/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                    headers={"Authorization": f"Bot {BOT_TOKEN}"},
                )

    user = session["user"]
    add_action(user["username"], "Unmute", user_id, "Unmuted")
    log_mod_action(user["username"], "Unmuted User", user_id)
    record_mod_activity(user["username"], "Unmuted User")

    return redirect(f"/server/{guild_id}/moderation")


# ============================
# Q&A Manager (merged)
# ============================

@app.route("/qna")
def qna_home():
    if require_login():
        return require_login()

    member = get_member(RITUALS_ID, session["user"]["id"])
    if not member or not can_access_qna(member):
        return render_template("unauthorized.html", title="Unauthorized")

    questions = list(questions_col.find().sort("id", -1))

    return render_template(
        "qna.html",
        user=session["user"],
        questions=questions,
        title="Q&A Manager"
    )


@app.route("/qna/create", methods=["POST"])
def qna_create():
    if require_login():
        return require_login()

    member = get_member(RITUALS_ID, session["user"]["id"])
    if not member or not can_access_qna(member):
        return render_template("unauthorized.html", title="Unauthorized")

    question_text = request.form.get("question")

    question = {
        "id": questions_col.count_documents({}) + 1,
        "question": question_text,
        "author": session["user"]["username"],
        "answers": []
    }

    questions_col.insert_one(question)

    return redirect("/qna")


@app.route("/qna/answer/<qid>", methods=["POST"])
def qna_answer(qid):
    if require_login():
        return require_login()

    member = get_member(RITUALS_ID, session["user"]["id"])
    if not member or not can_access_qna(member):
        return render_template("unauthorized.html", title="Unauthorized")

    answer_text = request.form.get("answer")

    answer = {
        "question_id": int(qid),
        "answer": answer_text,
        "author": session["user"]["username"]
    }

    answers_col.insert_one(answer)

    questions_col.update_one(
        {"id": int(qid)},
        {"$push": {"answers": answer}}
    )

    return redirect("/qna")


@app.route("/qna/delete/<qid>")
def qna_delete(qid):
    if require_login():
        return require_login()

    member = get_member(RITUALS_ID, session["user"]["id"])
    if not member or not can_access_qna(member):
        return render_template("unauthorized.html", title="Unauthorized")

    questions_col.delete_one({"id": int(qid)})
    answers_col.delete_many({"question_id": int(qid)})

    return redirect("/qna")


# ============================
# Config API (channels + mod role)
# ============================

@app.route("/api/config")
def api_config():
    cfg = get_config()
    return {
        "knowledge_channel_id": cfg.get("knowledge_channel_id", ""),
        "questions_channel_id": cfg.get("questions_channel_id", ""),
        "mod_role_id": cfg.get("mod_role_id", "")
    }


@app.route("/api/config/channels", methods=["POST"])
def api_config_channels():
    if require_login():
        return require_login()

    member = get_member_for_session(RITUALS_ID)
    if not member or not can_access_qna(member):
        return render_template("unauthorized.html", title="Unauthorized")

    data = request.get_json() or {}
    knowledge_channel_id = data.get("knowledge_channel_id")
    questions_channel_id = data.get("questions_channel_id")

    config_col.update_one(
        {"server_id": RITUALS_ID},
        {"$set": {
            "knowledge_channel_id": knowledge_channel_id,
            "questions_channel_id": questions_channel_id
        }},
        upsert=True
    )

    return {"ok": True}


@app.route("/api/config/modrole", methods=["POST"])
def api_config_modrole():
    if require_login():
        return require_login()

    member = get_member_for_session(RITUALS_ID)
    if not member or not can_access_qna(member):
        return render_template("unauthorized.html", title="Unauthorized")

    data = request.get_json() or {}
    mod_role_id = data.get("mod_role_id")

    config_col.update_one(
        {"server_id": RITUALS_ID},
        {"$set": {"mod_role_id": mod_role_id}},
        upsert=True
    )

    return {"ok": True}


# ============================
# Dashboard startup
# ============================

def start_dashboard(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    start_dashboard()
