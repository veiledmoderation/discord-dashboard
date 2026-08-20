def detect_rank(member, roles):
    """
    Determines a user's rank based on their Discord roles.
    Returns a string rank name.
    """

    if not member or "roles" not in member:
        return "Member"

    role_names = [r["name"].lower() for r in member["roles"]]

    # Highest → Lowest
    rank_order = [
        "owner",
        "co-owner",
        "head admin",
        "admin",
        "head mod",
        "senior mod",
        "moderator",
        "support",
        "engagement",
        "manager",
        "staff",
        "helper",
        "member"
    ]

    for rank in rank_order:
        if rank in role_names:
            return rank.title()

    return "Member"
