from django.contrib import admin
from .models import Meeting, Participant


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "host", "is_active", "created_at", "active_participant_count")
    list_filter = ("is_active",)
    readonly_fields = ("id", "created_at")


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("user", "meeting", "role", "is_active", "joined_at", "left_at")
    list_filter = ("is_active", "role")
