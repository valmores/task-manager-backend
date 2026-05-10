# internal_notes/permissions.py


# =========================
# ROOM PERMISSIONS
# =========================

def can_view_room(user, room):
    """
    Check if user can view a room based on STRICT MEMBERSHIP.
    - Admins and Room Creators can view any room.
    - For all other users: Must be in the room.members list.
    """
    if not user.is_authenticated:
        return False

    # 1. Admin or Creator Bypass
    if user.role == "admin" or room.created_by == user:
        return True

    # 2. Strict Membership Check
    # This covers Internal, Project-Specific, and Private rooms.
    return room.members.filter(id=user.id).exists()


def can_post_in_room(user, room):
    """
    Check if user can post in a room. Same as can_view_room (symmetric).
    """
    return can_view_room(user, room)


def can_create_room(user):
    """
    Only Admin and Project Owner can create rooms.
    """
    return user.is_authenticated and user.role in ["admin", "project_owner"]


def can_delete_room(user, room):
    """
    Only Admin or the Creator can delete rooms.
    Default rooms are protected (cannot be deleted unless admin).
    """
    if not user.is_authenticated:
        return False

    if user.role == "admin":
        return True

    if room.is_default:
        return False

    return room.created_by == user


def can_update_room(user, room):
    """
    Admin OR the room creator can update rooms.
    """
    if not user.is_authenticated:
        return False

    return user.role == "admin" or room.created_by == user


def can_manage_members(user, room):
    """
    Admin OR the room creator can manage room members.
    """
    if not user.is_authenticated:
        return False

    if user.role == "admin":
        return True

    # Room creator can manage their own room's members
    return room.created_by == user


# =========================
# MESSAGE PERMISSIONS
# =========================

def can_view_messages(user, room):
    """
    Check if user can view messages in a room. Delegates to can_view_room.
    """
    return can_view_room(user, room)


def can_send_message(user, room):
    """
    Check if user can send messages in a room. Delegates to can_post_in_room.
    """
    return can_post_in_room(user, room)


def can_edit_message(user, message):
    """
    Users can edit only their own messages. Admin can edit anything.
    """
    if not user.is_authenticated:
        return False

    if user.role == "admin":
        return True

    return message.author == user


def can_delete_message(user, message):
    """
    Admin: Can delete all messages
    Project Owner: Can delete messages in project-scoped rooms
    User: Can delete only their own messages
    """
    if not user.is_authenticated:
        return False

    if user.role == "admin":
        return True

    # Project owner can delete messages in PROJECT_SPECIFIC rooms
    if user.role == "project_owner" and message.room.visibility == "project_specific":
        return True

    # Users can delete their own messages
    return message.author == user