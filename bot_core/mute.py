# ============================================================
# MUTE SYSTEM — Matches EXACTLY what app.py expects
# ============================================================

from pymongo import MongoClient
import os

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["veilmodwebsite"]

mute_config_col = db["mute_config"]
mute_roles_col = db["mute_roles"]


# ============================================================
# Get Muted Role
# ============================================================

def get_muted_role(guild_id: int):
    """
    Returns the muted role name for the guild.
    """
    cfg = mute_config_col.find_one({"guild_id": guild_id})
    if cfg:
        return cfg.get("muted_role")
    return None


# ============================================================
# Set Muted Role
# ============================================================

def set_muted_role(guild_id: int, role_name: str):
    """
    Sets the muted role name for the guild.
    """
    mute_config_col.update_one(
        {"guild_id": guild_id},
        {"$set": {"muted_role": role_name}},
        upsert=True
    )


# ============================================================
# Save User Roles (before muting)
# ============================================================

def save_user_roles(guild_id: int, user_id: str, roles: list):
    """
    Saves the user's current roles before muting.
    """
    mute_roles_col.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"roles": roles}},
        upsert=True
    )


# ============================================================
# Restore User Roles (after unmuting)
# ============================================================

def restore_user_roles(guild_id: int, user_id: str):
    """
    Restores the user's roles after unmuting.
    Returns the list of roles to restore.
    """
    entry = mute_roles_col.find_one({"guild_id": guild_id, "user_id": user_id})
    if entry:
        return entry.get("roles", [])
    return []
