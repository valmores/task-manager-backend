from rest_framework import serializers
from .models import Task, Project


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model."""
    created_by = serializers.ReadOnlyField(source='created_by.email')
    task_count = serializers.IntegerField(source='tasks.count', read_only=True)

    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'created_by', 
            'task_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class TaskSerializer(serializers.ModelSerializer):
    """Full task serializer for Admin and Project Owners."""
    created_by = serializers.ReadOnlyField(source='created_by.email')
    assigned_to_email = serializers.ReadOnlyField(source='assigned_to.email')
    project_name = serializers.ReadOnlyField(source='project.name')

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'project', 'project_name',
            'status', 'priority', 'due_date', 'assigned_to', 
            'assigned_to_email', 'created_by', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    """Restricted serializer — regular users can only update status."""
    class Meta:
        model = Task
        fields = ('id', 'status',)
