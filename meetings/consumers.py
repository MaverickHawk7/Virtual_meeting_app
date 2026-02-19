"""
MeetingConsumer — Django Channels WebSocket consumer.

Handles two concerns:
  1. Presence  — join/leave notifications, chat, hand-raise
  2. Signaling — relays WebRTC offer/answer/ICE candidates between peers
                 (peer-to-peer media, no SFU required for local dev)

On connect the server sends a `room_state` event listing existing participants.
Tiebreaker for offer initiation: the client with the HIGHER user_id creates the offer.

WebSocket URL: ws/meeting/<meeting_id>/?token=<jwt>
Auth: validated in meetingapp/middleware.py before this consumer runs.

--- Message reference ---

Client → Server:
  { type: "chat",           message: "..." }
  { type: "hand_raise",     raised: true|false }
  { type: "webrtc_signal",  to: <user_id>, signal: { type: "offer"|"answer"|"ice", ... } }

Server → Client:
  { type: "room_state",         participants: [{user_id, username}, ...] }
  { type: "participant_joined",  user_id, username }
  { type: "participant_left",    user_id, username }
  { type: "chat",               user_id, username, message }
  { type: "hand_raise",         user_id, username, raised }
  { type: "webrtc_signal",      from: user_id, from_username, signal }
  { type: "meeting_ended" }
  { type: "error",              message }
"""
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser


class MeetingConsumer(AsyncWebsocketConsumer):

    # ── Lifecycle ────────────────────────────────────────────────────────────

    async def connect(self):
        self.meeting_id = self.scope["url_route"]["kwargs"]["meeting_id"]
        self.group_name = f"meeting_{self.meeting_id}"
        self.user = self.scope.get("user")

        if not self.user or isinstance(self.user, AnonymousUser):
            await self.close(code=4001)
            return

        ok = await self._check_access()
        if not ok:
            await self.close(code=4003)
            return

        # Join the meeting group (broadcast channel)
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # Join a personal group so others can send signals directly to us
        self.user_group = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)

        await self.accept()

        # Send current room state to the new joiner (so they know who's here)
        participants = await self._get_active_participants()
        await self.send(json.dumps({
            "type": "room_state",
            "participants": participants,
        }))

        # Broadcast join to everyone else
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "participant.joined",
                "user_id": self.user.id,
                "username": self.user.username,
            },
        )

    async def disconnect(self, close_code):
        if not hasattr(self, "group_name"):
            return

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "participant.left",
                "user_id": self.user.id,
                "username": self.user.username,
            },
        )
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

        if hasattr(self, "user_group"):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self._send_error("invalid JSON")
            return

        msg_type = data.get("type")

        if msg_type == "chat":
            message = str(data.get("message", "")).strip()[:500]
            if not message:
                return
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.message",
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "message": message,
                },
            )

        elif msg_type == "hand_raise":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "hand.raise",
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "raised": bool(data.get("raised", False)),
                },
            )

        elif msg_type == "webrtc_signal":
            # Unicast: relay only to the target user's personal group
            to_user_id = data.get("to")
            if not to_user_id:
                return
            await self.channel_layer.group_send(
                f"user_{to_user_id}",
                {
                    "type": "webrtc.relay",
                    "from_user_id": self.user.id,
                    "from_username": self.user.username,
                    "signal": data.get("signal"),
                },
            )

    # ── Group message handlers ────────────────────────────────────────────────

    async def participant_joined(self, event):
        await self.send(json.dumps({
            "type": "participant_joined",
            "user_id": event["user_id"],
            "username": event["username"],
        }))

    async def participant_left(self, event):
        await self.send(json.dumps({
            "type": "participant_left",
            "user_id": event["user_id"],
            "username": event["username"],
        }))

    async def chat_message(self, event):
        await self.send(json.dumps({
            "type": "chat",
            "user_id": event["user_id"],
            "username": event["username"],
            "message": event["message"],
        }))

    async def hand_raise(self, event):
        await self.send(json.dumps({
            "type": "hand_raise",
            "user_id": event["user_id"],
            "username": event["username"],
            "raised": event["raised"],
        }))

    async def webrtc_relay(self, event):
        # Forward the signal payload to our WebSocket client
        await self.send(json.dumps({
            "type": "webrtc_signal",
            "from": event["from_user_id"],
            "from_username": event["from_username"],
            "signal": event["signal"],
        }))

    async def meeting_ended(self, event):
        await self.send(json.dumps({"type": "meeting_ended"}))
        await self.close()

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _send_error(self, message: str):
        await self.send(json.dumps({"type": "error", "message": message}))

    @database_sync_to_async
    def _check_access(self):
        from .models import Meeting
        meeting = Meeting.objects.filter(id=self.meeting_id, is_active=True).first()
        if not meeting:
            return False
        if meeting.host_id == self.user.id:
            return True
        return meeting.participants.filter(user=self.user, is_active=True).exists()

    @database_sync_to_async
    def _get_active_participants(self):
        """Returns all OTHER active participants in this meeting (not self)."""
        from .models import Participant
        parts = (
            Participant.objects
            .filter(meeting_id=self.meeting_id, is_active=True)
            .exclude(user_id=self.user.id)
            .select_related("user")
        )
        return [{"user_id": p.user_id, "username": p.user.username} for p in parts]
