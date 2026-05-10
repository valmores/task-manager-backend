from django.urls import path, include
from .views import (
    RoomListView,
    RoomCreateView,
    RoomUpdateView,
    RoomDeleteView,
    RoomMembersView,
    RoomMessagesView,
)

urlpatterns = [
    # Rooms
    path("rooms/", RoomListView.as_view(), name="room-list"),
    path("rooms/create/", RoomCreateView.as_view(), name="room-create"),
    path("rooms/<int:pk>/update/", RoomUpdateView.as_view(), name="room-update"),
    path("rooms/<int:pk>/delete/", RoomDeleteView.as_view(), name="room-delete"),
    path("rooms/<int:pk>/members/", RoomMembersView.as_view(), name="room-members"),

    # Messages
    path("rooms/<int:room_id>/messages/", RoomMessagesView.as_view(), name="room-messages"),
]