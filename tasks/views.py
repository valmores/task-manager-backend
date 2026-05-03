from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Task, Project
from .serializers import (
    TaskSerializer, 
    TaskStatusUpdateSerializer, 
    ProjectSerializer,
    TaskAssignmentSerializer
)
from users.permissions import IsAdminOrProjectOwner, IsAdmin
from users.models import UserRole


class ProjectListCreateView(generics.ListCreateAPIView):
    """
    GET  — Admin/Owner see all; Users see projects of their tasks.
    POST — Admin and Project Owners only.
    """
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.ADMIN:
            return Project.objects.all()
        if user.role == UserRole.PROJECT_OWNER:
            return Project.objects.filter(created_by=user)
        # Regular users only see projects where they have an assigned task
        return Project.objects.filter(tasks__assigned_to=user).distinct()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrProjectOwner()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    — Authenticated users (scoped).
    PUT/PATCH — Admin only (Strict RBAC).
    DELETE — Admin only (Strict RBAC).
    """
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.ADMIN:
            return Project.objects.all()
        if user.role == UserRole.PROJECT_OWNER:
            return Project.objects.filter(created_by=user)
        return Project.objects.filter(tasks__assigned_to=user).distinct()

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]


class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET  — All users can list tasks (filtered by role).
    POST — Only Admin and Project Owners can create tasks.
    """
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.ADMIN:
            return Task.objects.all()
        if user.role == UserRole.PROJECT_OWNER:
            return Task.objects.filter(project__created_by=user)
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
    GET    — All authenticated users (scope enforced).
    PUT    — Admin only (Strict RBAC).
    PATCH  — Admin can update all; Users can update status only; Owner blocked from edit.
    DELETE — Admin only (Strict RBAC).
    """
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.ADMIN:
            return Task.objects.all()
        if user.role == UserRole.PROJECT_OWNER:
            return Task.objects.filter(project__created_by=user)
        return Task.objects.filter(assigned_to=user)

    def get_serializer_class(self):
        user = self.request.user
        # Regular users only get the restricted status-only serializer for PATCH
        if self.request.method == 'PATCH' and user.role == UserRole.USER:
            return TaskStatusUpdateSerializer
        # Project Owners can only reassign tasks via PATCH
        if self.request.method == 'PATCH' and user.role == UserRole.PROJECT_OWNER:
            return TaskAssignmentSerializer
        return TaskSerializer

    def get_permissions(self):
        if self.request.method in ['PUT']:
            return [IsAdmin()]
        if self.request.method == 'PATCH':
            # We allow the method here, but restrict logic in perform_update if needed
            # or rely on serializer + custom logic.
            return [permissions.IsAuthenticated()]
        if self.request.method == 'DELETE':
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_update(self, serializer):
        user = self.request.user
        # Project Owners can Create/Assign (via TaskAssignmentSerializer) but NOT Edit other fields (Strict RBAC)
        # The serializer handles the field restriction.
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        user = request.user
        # Admin only for deletion (Strict RBAC)
        if user.role != UserRole.ADMIN:
            raise PermissionDenied("Only Admins can delete tasks.")
        
        task = self.get_object()
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
