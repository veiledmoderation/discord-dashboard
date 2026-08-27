import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
from pymongo import MongoClient

# ============================
# Load Environment Variables
# ============================

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
mongo_uri = os.getenv("MONGO_URI")

guild_id_raw = os.getenv("RITUALS_GUILD_ID")
if guild_id_raw is None:
    raise ValueError("RITUALS_GUILD_ID is missing from .env")
RITUALS_ID = int(guild_id_raw)

QUESTIONS_CHANNEL_ID = os.getenv("QUESTIONS_CHANNEL_ID")
UNANSWERED_CHANNEL_ID = os.getenv("UNANSWERED_CHANNEL_ID")
PING_CHANNEL_ID = os.getenv("PING_CHANNEL_ID")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")

STAFF_ROLE_ID = os.getenv("STAFF_ROLE_ID")
AUTOROLE_ROLE_ID = os.getenv("AUTOROLE_ROLE_ID")
TICKET_CATEGORY_ID = os.getenv("TICKET_CATEGORY_ID")

# ============================
# MongoDB
# ============================

client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

def get_config():
    return db["config"].find_one({"server_id": str(RITUALS_ID)}) or {}

# ============================
# Bot Setup
# ============================

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# ============================
# Events
# ============================

@bot.event
async def on_ready():
    print(f"[BOT] Online as {bot.user}")

    # Sync slash commands to guild only (instant)
    try:
        guild = discord.Object(id=RITUALS_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"[BOT] Synced {len(synced)} slash commands to guild.")
    except Exception as e:
        print(f"[BOT] Slash sync error: {e}")

    # Save guild channels for dashboard dropdown
    guild_obj = bot.get_guild(RITUALS_ID)
    if guild_obj:
        channels = [{"id": ch.id, "name": ch.name} for ch in guild_obj.text_channels]
        db["settings"].update_one({}, {"$set": {"guild_channels": channels}}, upsert=True)
        print("[BOT] Synced guild channels to dashboard.")

@bot.event
async def on_member_join(member):
    cfg = get_config()
    channel_id = cfg.get("welcome_channel")
    message = cfg.get("welcome_message")

    if channel_id and message:
        channel = member.guild.get_channel(int(channel_id))
        if channel:
            await channel.send(message.replace("{user}", member.mention))

    auto_role = cfg.get("auto_role") or AUTOROLE_ROLE_ID
    if auto_role:
        role = member.guild.get_role(int(auto_role))
        if role:
            await member.add_roles(role)

# ============================
# Moderation Logging
# ============================

async def log_action(action, staff, target, reason):
    db["moderation_logs"].insert_one({
        "action": action,
        "staff_name": staff,
        "target_user_id": target.id,
        "reason": reason,
        "timestamp": discord.utils.utcnow()
    })

# ============================
# Prefix Commands (!)
# ============================

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await log_action("ban", ctx.author.name, member, reason)
    await ctx.send(f"{member} has been banned.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await log_action("kick", ctx.author.name, member, reason)
    await ctx.send(f"{member} has been kicked.")

@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    await log_action("warn", ctx.author.name, member, reason)
    await ctx.send(f"{member.mention} has been warned: {reason}")

# ============================
# Announcements (Prefix)
# ============================

@bot.command()
async def announce(ctx, *, message):
    cfg = get_config()
    channel_id = cfg.get("announcement_channel")

    if not channel_id:
        return await ctx.send("Announcement channel not set in dashboard.")

    channel = ctx.guild.get_channel(int(channel_id))
    if not channel:
        return await ctx.send("Announcement channel not found.")

    await channel.send(message)
    await ctx.send("Announcement sent.")

# ============================
# Ping Everyone (Prefix)
# ============================

@bot.command()
async def pingall(ctx, *, message):
    cfg = get_config()
    channel_id = cfg.get("ping_channel")

    if not channel_id:
        return await ctx.send("Ping channel not set in dashboard.")

    channel = ctx.guild.get_channel(int(channel_id))
    if not channel:
        return await ctx.send("Ping channel not found.")

    await channel.send(f"@everyone {message}")
    await ctx.send("Ping sent.")

# ============================
# Slash Commands (/)
# ============================

@bot.tree.command(name="ping", description="Ping test")
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!", ephemeral=True)

@bot.tree.command(name="announce", description="Send an announcement")
@app_commands.describe(message="Announcement message")
async def announce_slash(interaction: discord.Interaction, message: str):
    cfg = get_config()
    channel_id = cfg.get("announcement_channel")

    if not channel_id:
        return await interaction.response.send_message("Announcement channel not set.", ephemeral=True)

    channel = interaction.guild.get_channel(int(channel_id))
    if not channel:
        return await interaction.response.send_message("Announcement channel not found.", ephemeral=True)

    await channel.send(message)
    await interaction.response.send_message("Announcement sent.", ephemeral=True)

@bot.tree.command(name="pingall", description="Ping everyone in the selected channel")
@app_commands.describe(message="Message to send")
async def pingall_slash(interaction: discord.Interaction, message: str):
    cfg = get_config()
    channel_id = cfg.get("ping_channel")

    if not channel_id:
        return await interaction.response.send_message("Ping channel not set.", ephemeral=True)

    channel = interaction.guild.get_channel(int(channel_id))
    if not channel:
        return await interaction.response.send_message("Ping channel not found.", ephemeral=True)

    await channel.send(f"@everyone {message}")
    await interaction.response.send_message("Ping sent.", ephemeral=True)

# ============================
# QnA System
# ============================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    try:
        if QUESTIONS_CHANNEL_ID and str(message.channel.id) == QUESTIONS_CHANNEL_ID:
            db["qa"].insert_one({
                "id": str(message.id),
                "question": message.content,
                "answer": "",
                "user": message.author.name,
                "timestamp": discord.utils.utcnow().isoformat()
            })

            if UNANSWERED_CHANNEL_ID:
                ch = message.guild.get_channel(int(UNANSWERED_CHANNEL_ID))
                if ch:
                    await ch.send(f"New question from **{message.author.name}**:\n{message.content}")
    except Exception as e:
        print(f"[BOT] on_message error: {e}")

    await bot.process_commands(message)

# ============================
# Run Bot
# ============================

if TOKEN is None:
    raise ValueError("DISCORD_BOT_TOKEN is missing from .env")

bot.run(TOKEN)
