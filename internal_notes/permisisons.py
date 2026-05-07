# internal_notes/permissions.py


# =========================
# ROOM PERMISSIONS
# =========================

def can_view_rooms(user):
    """Any authenticated user can view rooms."""
    return user.is_authenticated


def can_create_room(user):
    """
    Only Admin and Project Owner can create rooms.
    """
    return user.is_authenticated and user.role in ["admin", "project_owner"]


def can_delete_room(user, room):
    """
    Only Admin can delete rooms.
    Default rooms are protected (cannot be deleted unless admin).
    """
    if not user.is_authenticated:
        return False

    if room.is_default:
        return user.role == "admin"

    return user.role == "admin"


def can_update_room(user, room):
    """
    Only Admin can update rooms.
    """
    return user.is_authenticated and user.role == "admin"


# =========================
# MESSAGE PERMISSIONS
# =========================

def can_view_messages(user, room):
    """
    Any authenticated user can view messages inside rooms.
    """
    return user.is_authenticated


def can_send_message(user, room):
    """
    Any authenticated user can send messages.
    """
    return user.is_authenticated


def can_delete_message(user, message):
    """
    Admin:
        - can delete all messages

    Project Owner:
        - can moderate messages (optional business rule)

    User:
        - can delete only their own messages
    """
    if not user.is_authenticated:
        return False

    if user.role == "admin":
        return True

    if user.role == "project_owner":
        return True

    return message.author == user


def can_edit_message(user, message):
    """
    Optional but useful:
    Users can edit only their own messages.
    Admin can edit anything.
    """
    if not user.is_authenticated:
        return False

    if user.role == "admin":
        return True

    return message.author == user