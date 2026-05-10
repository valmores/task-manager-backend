from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()

from .models import NoteRoom, InternalNote
from .serializers import NoteRoomSerializer, InternalNoteSerializer

from .permissions import (
    can_view_room,
    can_create_room,
    can_update_room,
    can_delete_room,
    can_view_messages,
    can_send_message,
    can_manage_members,
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
        return NoteRoom.objects.filter(id__in=accessible_ids).select_related('created_by', 'project').prefetch_related('members')

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

        # Extract members from validated data (M2M is handled separately)
        initial_members = serializer.validated_data.pop('members', [])

        # Set created_by to current user
        room = serializer.save(created_by=user)
        
        # Add creator to members list + initial members (regardless of visibility)
        room.members.add(user)
        
        # If Internal: Automatically add all active users in the system
        if room.visibility == 'internal':
            all_active_users = User.objects.filter(is_active=True)
            room.members.add(*all_active_users)
        elif initial_members:
            room.members.add(*initial_members)

class RoomDeleteView(generics.DestroyAPIView):
    queryset = NoteRoom.objects.all()
    serializer_class = NoteRoomSerializer

    def perform_destroy(self, instance):
        user = self.request.user

        if not can_delete_room(user, instance):
            raise PermissionDenied("Not allowed to delete room")

        instance.delete()

class RoomUpdateView(generics.UpdateAPIView):
    queryset = NoteRoom.objects.all()
    serializer_class = NoteRoomSerializer

    def perform_update(self, serializer):
        user = self.request.user
        room = self.get_object()

        if not can_update_room(user, room):
            raise PermissionDenied("Not allowed to update room")

        # Validate visibility + project field consistency if they are being updated
        visibility = serializer.validated_data.get('visibility', room.visibility)
        project = serializer.validated_data.get('project', room.project)

        if visibility == 'project_specific' and project is None:
            raise PermissionDenied("PROJECT_SPECIFIC rooms require a project to be specified")

        if visibility != 'project_specific' and project is not None:
            # Only raise if project is explicitly being set or was already set
            if serializer.validated_data.get('project'):
                 raise PermissionDenied(f"{visibility.upper()} rooms cannot have an associated project")

        serializer.save()

        # If visibility was changed to internal, add everyone
        if visibility == 'internal':
            all_active_users = User.objects.filter(is_active=True)
            room.members.add(*all_active_users)


class RoomMembersView(generics.GenericAPIView):
    """
    PATCH /api/internal/rooms/<pk>/members/
    Payload: { "add": [user_id, ...], "remove": [user_id, ...] }

    Only allowed on PRIVATE rooms.
    Permitted by: Admin OR room creator.
    """
    queryset = NoteRoom.objects.prefetch_related('members').all()
    serializer_class = NoteRoomSerializer

    def patch(self, request, pk):
        room = get_object_or_404(NoteRoom, pk=pk)
        user = request.user

        if not can_manage_members(user, room):
            raise PermissionDenied("Only admins or the room creator can manage members.")

        add_ids = request.data.get("add", [])
        remove_ids = request.data.get("remove", [])

        if add_ids:
            room.members.add(*add_ids)
        if remove_ids:
            room.members.remove(*remove_ids)

        serializer = self.get_serializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)


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