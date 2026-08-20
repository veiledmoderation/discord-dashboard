import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# -----------------------------------
# MongoDB Setup
# -----------------------------------
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

questions_col = db["questions"]
answers_col = db["answers"]
config_col = db["config"]

# -----------------------------------
# Discord Bot Setup
# -----------------------------------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="?", intents=intents)

# Rituals server ID from .env
RITUALS_ID = int(os.getenv("RITUALS_GUILD_ID"))


# -----------------------------------
# Helpers
# -----------------------------------

def get_config():
    """Load Rituals server config from MongoDB."""
    return config_col.find_one({"server_id": RITUALS_ID})


def is_mod_plus(member):
    """Check if user has the Mod+ role."""
    cfg = get_config()
    if not cfg or "mod_role_id" not in cfg:
        return False

    mod_role_id = int(cfg["mod_role_id"])
    return discord.utils.get(member.roles, id=mod_role_id) is not None


def get_answer(keyword):
    """Find answer for a keyword."""
    return answers_col.find_one({
        "server_id": RITUALS_ID,
        "keyword": keyword.lower()
    })


# -----------------------------------
# Bot Ready
# -----------------------------------
@bot.event
async def on_ready():
    print(f"[BOT] Logged in as {bot.user}")
    print("[BOT] Rituals Q&A system active.")


# -----------------------------------
# Message Listener
# -----------------------------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.guild.id != RITUALS_ID:
        return

    cfg = get_config()
    if not cfg:
        return

    knowledge_channel = int(cfg.get("knowledge_channel_id", 0))
    questions_channel = int(cfg.get("questions_channel_id", 0))

    content = message.content.lower()
    channel_id = message.channel.id

    # -----------------------------
    # Knowledge channel (Managers+)
    # -----------------------------
    if channel_id == knowledge_channel:
        if is_mod_plus(message.author):
            await message.add_reaction("🧠")
        await bot.process_commands(message)
        return

    # -----------------------------
    # Questions channel (Mod+)
    # -----------------------------
    if channel_id == questions_channel:
        if not is_mod_plus(message.author):
            await message.reply("You must be Mod+ to ask questions here.")
            return

        answer_doc = get_answer(content)

        if answer_doc:
            await message.reply(answer_doc["answer"])
        else:
            questions_col.insert_one({
                "server_id": RITUALS_ID,
                "question": content,
                "channel": "questions",
                "user": message.author.id
            })
            await message.add_reaction("🧠")

        await bot.process_commands(message)
        return

    # -----------------------------
    # Other channels: ignore Q&A
    # -----------------------------
    await bot.process_commands(message)


# -----------------------------------
# Manager Commands
# -----------------------------------

@bot.command()
@commands.has_permissions(administrator=True)
async def setmodrole(ctx, role: discord.Role):
    """Set the Mod+ role."""
    config_col.update_one(
        {"server_id": RITUALS_ID},
        {"$set": {"mod_role_id": role.id}},
        upsert=True
    )
    await ctx.send(f"Mod+ role set to {role.name}")


@bot.command()
@commands.has_permissions(administrator=True)
async def setknowledge(ctx, channel: discord.TextChannel):
    """Set the knowledge channel."""
    config_col.update_one(
        {"server_id": RITUALS_ID},
        {"$set": {"knowledge_channel_id": channel.id}},
        upsert=True
    )
    await ctx.send(f"Knowledge channel set to {channel.mention}")


@bot.command()
@commands.has_permissions(administrator=True)
async def setquestions(ctx, channel: discord.TextChannel):
    """Set the questions channel."""
    config_col.update_one(
        {"server_id": RITUALS_ID},
        {"$set": {"questions_channel_id": channel.id}},
        upsert=True
    )
    await ctx.send(f"Questions channel set to {channel.mention}")


@bot.command()
@commands.has_permissions(administrator=True)
async def setmutedrole(ctx, role: discord.Role):
    """Set the muted role."""
    config_col.update_one(
        {"server_id": RITUALS_ID},
        {"$set": {"muted_role_id": role.id}},
        upsert=True
    )
    await ctx.send(f"Muted role set to {role.name}")


# -----------------------------------
# Mod+ Commands
# -----------------------------------

@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    if not is_mod_plus(ctx.author):
        return await ctx.send("You must be Mod+ to use this.")
    await ctx.send(f"{member.mention} has been warned: {reason}")


@bot.command()
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    if not is_mod_plus(ctx.author):
        return await ctx.send("You must be Mod+ to use this.")
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} has been kicked.")


@bot.command()
async def mute(ctx, member: discord.Member):
    if not is_mod_plus(ctx.author):
        return await ctx.send("You must be Mod+ to use this.")

    cfg = get_config()
    muted_role_id = int(cfg.get("muted_role_id", 0))
    muted_role = ctx.guild.get_role(muted_role_id)

    if not muted_role:
        return await ctx.send("Muted role is not set.")

    await member.add_roles(muted_role)
    await ctx.send(f"{member.mention} has been muted.")


@bot.command()
async def unmute(ctx, member: discord.Member):
    if not is_mod_plus(ctx.author):
        return await ctx.send("You must be Mod+ to use this.")

    cfg = get_config()
    muted_role_id = int(cfg.get("muted_role_id", 0))
    muted_role = ctx.guild.get_role(muted_role_id)

    if not muted_role:
        return await ctx.send("Muted role is not set.")

    await member.remove_roles(muted_role)
    await ctx.send(f"{member.mention} has been unmuted.")


@bot.command()
async def afk(ctx, *, reason="AFK"):
    if not is_mod_plus(ctx.author):
        return await ctx.send("You must be Mod+ to use this.")
    await ctx.send(f"{ctx.author.mention} is now AFK: {reason}")


# -----------------------------------
# Expose bot to Flask
# -----------------------------------
import builtins
builtins.bot = bot
