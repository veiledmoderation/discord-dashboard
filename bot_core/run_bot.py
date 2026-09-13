# bot_core/run_bot.py

def get_rank(member):
    """
    Determine staff rank based on roles.
    """
    rank_order = [
        "Owner/Founder",
        "Same Permissions as owner/Red Lady",
        "Community Manager",
        "Head Director",
        "Director",
        "Head Of Staff",
        "Head Of Support",
        "Head Of Engagement",
        "Senior Administrator",
        "Administrator",
        "Senior Moderator",
        "Moderator",
        "Trial Moderator"
    ]

    for role in member.roles:
        if role.name in rank_order:
            return role.name

    return "Member"


def get_department(member):
    """
    Determine department based on roles.
    """
    departments = [
        "Support Department",
        "Engagement Department",
        "Multi Department"
    ]

    for role in member.roles:
        if role.name in departments:
            return role.name

    return "None"
