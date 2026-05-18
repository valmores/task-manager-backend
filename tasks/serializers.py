from rest_framework import serializers
from .models import Task, Project, TaskNote


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



class TaskNoteSerializer(serializers.ModelSerializer):
    """Serializer for internal task notes."""
    author_email = serializers.ReadOnlyField(source='author.email')
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = TaskNote
        fields = ('id', 'task', 'author', 'author_email', 'author_name', 'content', 'created_at')
        read_only_fields = ('author', 'created_at')

    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}"


class TaskSerializer(serializers.ModelSerializer):
    """Full task serializer for Admin and Project Owners."""
    created_by = serializers.ReadOnlyField(source='created_by.email')
    assigned_to_email = serializers.ReadOnlyField(source='assigned_to.email')
    project_name = serializers.ReadOnlyField(source='project.name')
    notes = TaskNoteSerializer(many=True, read_only=True)
    due_date = serializers.DateField(
        allow_null=True, 
        required=False,
        error_messages={'invalid': 'Please provide a valid date.'}
    )
    signature = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'project', 'project_name',
            'status', 'priority', 'due_date', 'assigned_to', 
            'assigned_to_email', 'notes', 'created_by', 'created_at', 'updated_at',
            'signature', 'signed_at'
        )
        read_only_fields = ('created_by', 'created_at', 'updated_at')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['signature'] = instance.signature.image if instance.signature else None
        return ret

    def update(self, instance, validated_data):
        signature_data = validated_data.pop('signature', None)
        if signature_data is not None:
            if signature_data == "":
                instance.signature = None
            else:
                from .models import Signature
                request_user = self.context.get('request').user if 'request' in self.context else (instance.assigned_to or instance.created_by)
                sig = Signature.objects.create(
                    image=signature_data,
                    created_by=request_user
                )
                instance.signature = sig
        return super().update(instance, validated_data)


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    """Restricted serializer — regular users can only update status and signature."""
    signature = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ('id', 'status', 'signature', 'signed_at')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['signature'] = instance.signature.image if instance.signature else None
        return ret

    def update(self, instance, validated_data):
        signature_data = validated_data.pop('signature', None)
        if signature_data is not None:
            if signature_data == "":
                instance.signature = None
            else:
                from .models import Signature
                request_user = self.context.get('request').user if 'request' in self.context else (instance.assigned_to or instance.created_by)
                sig = Signature.objects.create(
                    image=signature_data,
                    created_by=request_user
                )
                instance.signature = sig
        return super().update(instance, validated_data)


class TaskAssignmentSerializer(serializers.ModelSerializer):
    """Restricted serializer — Project Owners can only update assignment."""
    class Meta:
        model = Task
        fields = ('id', 'assigned_to',)
