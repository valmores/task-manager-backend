from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Task
from .serializers import TaskSerializer, TaskStatusUpdateSerializer
from users.permissions import IsAdminOrProjectOwner
from users.models import UserRole


class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET  — All users can list tasks (filtered by role).
    POST — Only Admin and Project Owners can create tasks.
    """
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in [UserRole.ADMIN, UserRole.PROJECT_OWNER]:
            return Task.objects.all()
        # Regular users only see tasks assigned to them
        return Task.objects.filter(assigned_to=user)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrProjectOwner()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    — All authenticated users (scope enforced by get_object).
    PUT    — Admin and Project Owners only.
    PATCH  — All authenticated users, but regular users can only update status.
    DELETE — Admin, Project Owners, and the assigned regular user.
    """
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in [UserRole.ADMIN, UserRole.PROJECT_OWNER]:
            return Task.objects.all()
        return Task.objects.filter(assigned_to=user)

    def get_serializer_class(self):
        user = self.request.user
        # Regular users only get the restricted status-only serializer for PATCH
        if self.request.method == 'PATCH' and user.role == UserRole.USER:
            return TaskStatusUpdateSerializer
        return TaskSerializer

    def get_permissions(self):
        if self.request.method in ['PUT']:
            return [IsAdminOrProjectOwner()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        user = request.user
        # Admin and Project Owners can delete any task
        # Regular users can only delete tasks assigned to them
        if user.role == UserRole.USER and task.assigned_to != user:
            raise PermissionDenied("You can only delete tasks assigned to you.")
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
