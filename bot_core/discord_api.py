import requests
from config import BOT_TOKEN

BASE_URL = "https://discord.com/api"


# ============================
# USER INFO
# ============================

def get_user(access_token: str):
    """
    Returns the Discord user object for the logged-in user.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(f"{BASE_URL}/users/@me", headers=headers)
    return r.json()


# ============================
# GUILD MEMBER INFO
# ============================

def get_member(guild_id: int, user_id: int):
    """
    Returns a guild member object.
    """
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    r = requests.get(f"{BASE_URL}/guilds/{guild_id}/members/{user_id}", headers=headers)
    return r.json()


def get_guild_members(guild_id: int):
    """
    Returns a list of guild members.
    """
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    r = requests.get(f"{BASE_URL}/guilds/{guild_id}/members?limit=1000", headers=headers)
    return r.json()


# ============================
# GUILD ROLES
# ============================

def get_guild_roles(guild_id: int):
    """
    Returns all roles in the guild.
    """
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    r = requests.get(f"{BASE_URL}/guilds/{guild_id}/roles", headers=headers)
    return r.json()
