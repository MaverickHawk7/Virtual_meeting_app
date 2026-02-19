"""
SFU token service — abstraction layer over the media provider.

To swap providers, implement the same interface here.
Current implementation: LiveKit (livekit-api Python SDK).

Alternatives you could drop in:
  - Twilio Video: use twilio.jwt.access_token.AccessToken + VideoGrant
  - Daily.co: POST https://api.daily.co/v1/meeting-tokens (HTTP API)
  - Agora: use agora_token_builder.RtcTokenBuilder
"""
from django.conf import settings


class SFUTokenService:
    @staticmethod
    def generate_token(
        room_name: str,
        participant_identity: str,
        participant_name: str,
        is_host: bool = False,
    ) -> str:
        """
        Returns a signed JWT the browser passes to the LiveKit server.
        room_name     — meeting UUID string
        identity      — user.id as string (must be unique per room)
        name          — display name shown in the room
        is_host       — grants room_admin (can mute/remove others)
        """
        from livekit.api import AccessToken, VideoGrants

        grants = VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,   # data channel (chat via LiveKit, optional)
            room_admin=is_host,      # host can call admin RPC
        )

        token = (
            AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
            .with_identity(participant_identity)
            .with_name(participant_name)
            .with_grants(grants)
        )
        return token.to_jwt()

    @staticmethod
    def get_server_url() -> str:
        """WebSocket URL the browser connects to for media."""
        return settings.LIVEKIT_URL
