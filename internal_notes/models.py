from django.db import models
from django.conf import settings


class RoomVisibility(models.TextChoices):
    ADMIN_ONLY = 'admin_only', 'Admin Only'
    INTERNAL = 'internal', 'Internal'
    PROJECT_SPECIFIC = 'project_specific', 'Project Specific'
    PRIVATE = 'private', 'Private'


class NoteRoom(models.Model):
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    visibility = models.CharField(
        max_length=20,
        choices=RoomVisibility.choices,
        default=RoomVisibility.INTERNAL
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_note_rooms'
    )
    project = models.ForeignKey(
        'tasks.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='note_rooms'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='private_note_rooms'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
        
class InternalNote(models.Model):
    room = models.ForeignKey(
        NoteRoom,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author} - {self.content[:30]}"