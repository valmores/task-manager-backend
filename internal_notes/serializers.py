from rest_framework import serializers
from .models import NoteRoom, InternalNote


class MemberInfoSerializer(serializers.Serializer):
    """Minimal read-only serializer for room member display."""
    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role = serializers.CharField()


class NoteRoomSerializer(serializers.ModelSerializer):
    created_by_email = serializers.CharField(
        source="created_by.email",
        read_only=True,
        allow_null=True
    )
    project_name = serializers.CharField(
        source="project.name",
        read_only=True,
        allow_null=True
    )
    members_detail = MemberInfoSerializer(
        source="members",
        many=True,
        read_only=True
    )

    class Meta:
        model = NoteRoom
        fields = "__all__"
        # members is now writable (PrimaryKeyRelatedField by default)
        read_only_fields = ["created_by", "created_at"]


class InternalNoteSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(
        source="author.email",
        read_only=True
    )

    class Meta:
        model = InternalNote
        fields = "__all__"
        read_only_fields = ["author", "created_at", "updated_at"]