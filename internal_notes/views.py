from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from .models import NoteRoom, InternalNote
from .serializers import NoteRoomSerializer, InternalNoteSerializer

from .permissions import (
    can_view_room,
    can_create_room,
    can_delete_room,
    can_view_messages,
    can_send_message,
)

class RoomListView(generics.ListAPIView):
    serializer_class = NoteRoomSerializer

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied("Not allowed")

        # Get all rooms and filter by what user can view
        all_rooms = NoteRoom.objects.select_related('created_by', 'project').all()
        accessible_rooms = [room for room in all_rooms if can_view_room(user, room)]
        
        # Return queryset of accessible room IDs
        accessible_ids = [room.id for room in accessible_rooms]
        return NoteRoom.objects.filter(id__in=accessible_ids).select_related('created_by', 'project')

class RoomCreateView(generics.CreateAPIView):
    serializer_class = NoteRoomSerializer

    def perform_create(self, serializer):
        user = self.request.user

        if not can_create_room(user):
            raise PermissionDenied("Not allowed to create rooms")

        # Validate visibility + project field consistency
        visibility = serializer.validated_data.get('visibility', 'internal')
        project = serializer.validated_data.get('project')

        if visibility == 'project_specific' and project is None:
            raise PermissionDenied("PROJECT_SPECIFIC rooms require a project to be specified")

        if visibility != 'project_specific' and project is not None:
            raise PermissionDenied(f"{visibility.upper()} rooms cannot have an associated project")

        # Set created_by to current user
        room = serializer.save(created_by=user)
        
        # If PRIVATE room, auto-add creator to members
        if room.visibility == 'private':
            room.members.add(user)

class RoomDeleteView(generics.DestroyAPIView):
    queryset = NoteRoom.objects.all()
    serializer_class = NoteRoomSerializer

    def perform_destroy(self, instance):
        user = self.request.user

        if not can_delete_room(user, instance):
            raise PermissionDenied("Not allowed to delete room")

        instance.delete()

class RoomMessagesView(generics.ListCreateAPIView):
    serializer_class = InternalNoteSerializer

    def get_queryset(self):
        room = get_object_or_404(NoteRoom, id=self.kwargs["room_id"])

        if not can_view_messages(self.request.user, room):
            raise PermissionDenied("Not allowed to view messages")

        return InternalNote.objects.filter(room=room)

    def perform_create(self, serializer):
        room = get_object_or_404(NoteRoom, id=self.kwargs["room_id"])
        user = self.request.user

        if not can_send_message(user, room):
            raise PermissionDenied("Not allowed to send message")

        serializer.save(author=user, room=room)