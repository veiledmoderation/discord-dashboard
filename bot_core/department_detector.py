from department_store import get_department

def detect_department(member, rank):
    """
    Detects a user's department based on stored assignments.
    """
    if not member:
        return None

    user_id = member["user"]["id"]
    dept = get_department(user_id)

    return dept
