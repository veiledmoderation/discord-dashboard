# ============================================================
# PERMISSIONS SYSTEM FOR RITUALS DASHBOARD
# Matches EXACTLY what app.py imports and expects.
# ============================================================

# These permission functions receive a Discord "member" object.
# Your member object looks like:
# {
#     "user": {"id": "...", "username": "..."},
#     "roles": [{"id": "...", "name": "Mod+"}, ...]
# }
#
# So we check role names directly.


# ============================================================
# Helper: check if member has a role by name
# ============================================================

def has_role(member, role_name: str):
    if not member or "roles" not in member:
        return False

    for role in member["roles"]:
        if role.get("name") == role_name:
            return True

    return False


# ============================================================
# Dashboard Access
# ============================================================

def can_access_dashboard(member):
    """
    Dashboard access = Mod+ or Admin
    """
    return (
        has_role(member, "Mod+") or
        has_role(member, "Admin") or
        has_role(member, "Manager")
    )


# ============================================================
# Support Tools Access
# ============================================================

def can_access_support(member):
    """
    Support tools access = Support Team, Mod+, Admin
    """
    return (
        has_role(member, "Support") or
        has_role(member, "Mod+") or
        has_role(member, "Admin")
    )


# ============================================================
# Engagement Tools Access
# ============================================================

def can_access_engagement(member):
    """
    Engagement tools access = Engagement Team, Manager, Admin
    """
    return (
        has_role(member, "Engagement") or
        has_role(member, "Manager") or
        has_role(member, "Admin")
    )


# ============================================================
# Moderation Tools Access
# ============================================================

def can_access_moderation(member):
    """
    Moderation tools access = Mod+, Admin
    """
    return (
        has_role(member, "Mod+") or
        has_role(member, "Admin")
    )


# ============================================================
# Q&A Manager Access
# ============================================================

def can_access_qna(member):
    """
    Q&A access = Manager, Admin
    """
    return (
        has_role(member, "Manager") or
        has_role(member, "Admin")
    )
