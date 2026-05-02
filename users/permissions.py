from rest_framework import permissions
from .models import UserRole

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.ADMIN

class IsProjectOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.PROJECT_OWNER

class IsRegularUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.USER

class IsAdminOrProjectOwner(permissions.BasePermission):
    """Grants access to both Admin and Project Owner roles."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            UserRole.ADMIN,
            UserRole.PROJECT_OWNER
        ]
