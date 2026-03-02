import uuid
from django.db import models
from django.contrib.auth.models import User


class Meeting(models.Model):
    """
    A meeting room. UUID is the join code — share this with participants.
    The host is the creator; only the host can end the meeting for everyone.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="Untitled Meeting")
    host = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="hosted_meetings"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    max_participants = models.PositiveIntegerField(default=20)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} [{self.id}]"

    @property
    def active_participant_count(self):
        return self.participants.filter(is_active=True).count()


class Participant(models.Model):
    """
    Tracks who is (or was) in a meeting.
    is_active=True means they're currently connected.
    """
    ROLE_HOST = "host"
    ROLE_PARTICIPANT = "participant"
    ROLE_CHOICES = [(ROLE_HOST, "Host"), (ROLE_PARTICIPANT, "Participant")]

    meeting = models.ForeignKey(
        Meeting, on_delete=models.CASCADE, related_name="participants"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="meeting_sessions"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_PARTICIPANT)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        # A user can rejoin, but only one active session per meeting
        unique_together = [("meeting", "user")]
        indexes = [
            models.Index(fields=["meeting", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.username} in {self.meeting_id} ({self.role})"
