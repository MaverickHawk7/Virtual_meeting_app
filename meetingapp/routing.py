from django.urls import re_path
from meetings import consumers

# WebSocket URL patterns only.
# Pattern: ws/meeting/<uuid>/
websocket_urlpatterns = [
    re_path(
        r"^ws/meeting/(?P<meeting_id>[0-9a-f-]{36})/$",
        consumers.MeetingConsumer.as_asgi(),
    ),
]
