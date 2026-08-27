import os
from flask import Flask
from flask_socketio import SocketIO
from pymongo import MongoClient

mongo_uri = os.getenv("MONGO_URI")

def get_db():
    client = MongoClient(mongo_uri)
    return client["veilmodwebsite"]

db = get_db()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET", "dev_secret")

socketio = SocketIO(app, cors_allowed_origins="*")

# ============================
# Emit Functions (used by bot + dashboard)
# ============================

def emit_ticket_update(ticket):
    socketio.emit("ticket_update", ticket, broadcast=True)

def emit_moderation_log(log):
    socketio.emit("moderation_log", log, broadcast=True)

def emit_qna_update(question):
    socketio.emit("qna_update", question, broadcast=True)

def emit_server_stats(stats):
    socketio.emit("server_stats", stats, broadcast=True)

# ============================
# Socket Events
# ============================

@socketio.on("connect")
def on_connect():
    print("Client connected")

@socketio.on("disconnect")
def on_disconnect():
    print("Client disconnected")

# ============================
# Run
# ============================

if __name__ == "__main__":
    socketio.run(app, debug=True)
