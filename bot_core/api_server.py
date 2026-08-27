import os
import hmac
import hashlib
import asyncio
from flask import Flask, request, jsonify
import discord
from discord.ext import commands

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_SECRET = os.getenv("API_SECRET")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

app = Flask(__name__)

def verify_signature(payload, signature):
    mac = hmac.new(API_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, signature)

def run_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, bot.loop)

@app.route("/api/moderation/mute", methods=["POST"])
def mute_user():
    payload = request.data
    signature = request.headers.get("X-Signature")

    if not verify_signature(payload, signature):
        return jsonify({"error": "Invalid signature"}), 403

    data = request.json
    guild_id = int(data["guild_id"])
    user_id = int(data["user_id"])
    role_name = data["role_name"]

    async def do_mute():
        guild = bot.get_guild(guild_id)
        member = guild.get_member(user_id)
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            await member.add_roles(role)

    run_async(do_mute())
    return jsonify({"ok": True})

@app.route("/api/moderation/unmute", methods=["POST"])
def unmute_user():
    payload = request.data
    signature = request.headers.get("X-Signature")

    if not verify_signature(payload, signature):
        return jsonify({"error": "Invalid signature"}), 403

    data = request.json
    guild_id = int(data["guild_id"])
    user_id = int(data["user_id"])
    role_name = data["role_name"]

    async def do_unmute():
        guild = bot.get_guild(guild_id)
        member = guild.get_member(user_id)
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            await member.remove_roles(role)

    run_async(do_unmute())
    return jsonify({"ok": True})

@app.route("/api/moderation/kick", methods=["POST"])
def kick_user():
    payload = request.data
    signature = request.headers.get("X-Signature")

    if not verify_signature(payload, signature):
        return jsonify({"error": "Invalid signature"}), 403

    data = request.json
    guild_id = int(data["guild_id"])
    user_id = int(data["user_id"])
    reason = data.get("reason", "No reason provided")

    async def do_kick():
        guild = bot.get_guild(guild_id)
        member = guild.get_member(user_id)
        await member.kick(reason=reason)

    run_async(do_kick())
    return jsonify({"ok": True})

@app.route("/api/moderation/ban", methods=["POST"])
def ban_user():
    payload = request.data
    signature = request.headers.get("X-Signature")

    if not verify_signature(payload, signature):
        return jsonify({"error": "Invalid signature"}), 403

    data = request.json
    guild_id = int(data["guild_id"])
    user_id = int(data["user_id"])
    reason = data.get("reason", "No reason provided")

    async def do_ban():
        guild = bot.get_guild(guild_id)
        member = guild.get_member(user_id)
        await member.ban(reason=reason)

    run_async(do_ban())
    return jsonify({"ok": True})

@app.route("/api/moderation/warn", methods=["POST"])
def warn_user():
    payload = request.data
    signature = request.headers.get("X-Signature")

    if not verify_signature(payload, signature):
        return jsonify({"error": "Invalid signature"}), 403

    return jsonify({"ok": True})

def run_api():
    app.run(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    import threading
    threading.Thread(target=run_api).start()
    bot.run(BOT_TOKEN)
