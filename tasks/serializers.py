from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Full task serializer for Admin and Project Owners."""
    created_by = serializers.ReadOnlyField(source='created_by.email')
    assigned_to_email = serializers.ReadOnlyField(source='assigned_to.email')

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'assigned_to', 'assigned_to_email',
            'created_by', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    """Restricted serializer — regular users can only update status."""
    class Meta:
        model = Task
        fields = ('id', 'status',)
