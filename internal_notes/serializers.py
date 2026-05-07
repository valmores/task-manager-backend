from rest_framework import serializers
from .models import NoteRoom, InternalNote


class NoteRoomSerializer(serializers.ModelSerializer):
    created_by_email = serializers.CharField(
        source="created_by.email",
        read_only=True
    )

    class Meta:
        model = NoteRoom
        fields = "__all__"
        read_only_fields = ["created_by"]


class InternalNoteSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(
        source="author.email",
        read_only=True
    )

    class Meta:
        model = InternalNote
        fields = "__all__"
        read_only_fields = ["author", "created_at"]