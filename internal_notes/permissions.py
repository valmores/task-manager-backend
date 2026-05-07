# internal_notes/permissions.py


# =========================
# ROOM PERMISSIONS
# =========================

def can_view_room(user, room):
    """
    Check if user can view a room based on visibility level.
    
    - ADMIN_ONLY: Only admins
    - INTERNAL: All authenticated users
    - PROJECT_SPECIFIC: Project members + admins
    - PRIVATE: Room members + admins
    """
    if not user.is_authenticated:
        return False

    # Admin can always view
    if user.role == "admin":
        return True

    visibility = room.visibility

    if visibility == "admin_only":
        return False

    if visibility == "internal":
        return True

    if visibility == "project_specific":
        # Check if user is a member of the project or project owner
        if room.project is None:
            return False
        # Allow project owner or if user created the project
        return user.role == "project_owner" or room.project.created_by == user

    if visibility == "private":
        # Check if user is in room members
        return room.members.filter(id=user.id).exists()

    return False


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