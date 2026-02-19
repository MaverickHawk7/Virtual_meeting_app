from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Meeting, Participant
from .services import SFUTokenService


# ─── Auth ────────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username", "").strip()
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")

        if not username or not password:
            return Response({"error": "username and password required"}, status=400)

        if len(password) < 8:
            return Response({"error": "password must be at least 8 characters"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "username already taken"}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": {"id": user.id, "username": user.username},
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=201,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "invalid credentials"}, status=401)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": {"id": user.id, "username": user.username},
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )


# ─── Meetings ─────────────────────────────────────────────────────────────────

class MeetingListCreateView(APIView):
    """
    GET  /api/meetings/   — list caller's hosted meetings
    POST /api/meetings/   — create a new meeting
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        meetings = Meeting.objects.filter(host=request.user, is_active=True)
        return Response(
            [
                {
                    "id": str(m.id),
                    "title": m.title,
                    "created_at": m.created_at,
                    "active_participants": m.active_participant_count,
                }
                for m in meetings
            ]
        )

    def post(self, request):
        title = request.data.get("title", "Untitled Meeting").strip()[:255]
        meeting = Meeting.objects.create(host=request.user, title=title)
        return Response(
            {"id": str(meeting.id), "title": meeting.title},
            status=201,
        )


class MeetingJoinView(APIView):
    """
    POST /api/meetings/<id>/join/

    1. Validates the meeting exists and is active.
    2. Enforces participant cap.
    3. Creates/re-activates the Participant record.
    4. Issues a LiveKit SFU token scoped to this room.
    5. Returns token + LiveKit server URL so the browser can connect directly.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, meeting_id):
        try:
            meeting = Meeting.objects.get(id=meeting_id, is_active=True)
        except (Meeting.DoesNotExist, ValueError):
            return Response({"error": "meeting not found"}, status=404)

        # Check cap (host doesn't count against the limit)
        active_count = meeting.participants.filter(is_active=True).count()
        is_host = meeting.host == request.user
        if not is_host and active_count >= meeting.max_participants:
            return Response({"error": "meeting is full"}, status=403)

        # Upsert participant record
        role = Participant.ROLE_HOST if is_host else Participant.ROLE_PARTICIPANT
        participant, created = Participant.objects.get_or_create(
            meeting=meeting,
            user=request.user,
            defaults={"role": role, "is_active": True},
        )
        if not created:
            # Rejoin: reset state
            participant.is_active = True
            participant.left_at = None
            participant.joined_at = timezone.now()
            participant.save()

        # Generate SFU token — browser sends this directly to LiveKit
        sfu_token = SFUTokenService.generate_token(
            room_name=str(meeting.id),
            participant_identity=str(request.user.id),
            participant_name=request.user.username,
            is_host=is_host,
        )

        return Response(
            {
                "meeting_id": str(meeting.id),
                "title": meeting.title,
                "is_host": is_host,
                "sfu_token": sfu_token,       # browser passes to LiveKit SDK
                "sfu_url": SFUTokenService.get_server_url(),  # LiveKit WS URL
            }
        )


class MeetingLeaveView(APIView):
    """
    POST /api/meetings/<id>/leave/

    Marks participant inactive.
    If the host leaves, the meeting is ended for everyone.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, meeting_id):
        try:
            meeting = Meeting.objects.get(id=meeting_id)
        except (Meeting.DoesNotExist, ValueError):
            return Response({"error": "meeting not found"}, status=404)

        # Mark participant as left
        Participant.objects.filter(
            meeting=meeting, user=request.user, is_active=True
        ).update(is_active=False, left_at=timezone.now())

        # If host leaves → end meeting, kick everyone
        if meeting.host == request.user:
            meeting.is_active = False
            meeting.ended_at = timezone.now()
            meeting.save()
            Participant.objects.filter(meeting=meeting, is_active=True).update(
                is_active=False, left_at=timezone.now()
            )
            return Response({"status": "meeting ended"})

        return Response({"status": "left"})


class MeetingParticipantsView(APIView):
    """
    GET /api/meetings/<id>/participants/

    Returns active participants. Caller must be in the meeting.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, meeting_id):
        try:
            meeting = Meeting.objects.get(id=meeting_id)
        except (Meeting.DoesNotExist, ValueError):
            return Response({"error": "meeting not found"}, status=404)

        # Access check: must be host or active participant
        is_host = meeting.host == request.user
        is_participant = meeting.participants.filter(
            user=request.user, is_active=True
        ).exists()

        if not is_host and not is_participant:
            return Response({"error": "forbidden"}, status=403)

        participants = meeting.participants.filter(is_active=True).select_related("user")
        return Response(
            [
                {
                    "user_id": p.user.id,
                    "username": p.user.username,
                    "role": p.role,
                    "joined_at": p.joined_at,
                }
                for p in participants
            ]
        )


class MeetingEndView(APIView):
    """
    POST /api/meetings/<id>/end/   — host only
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, meeting_id):
        try:
            meeting = Meeting.objects.get(id=meeting_id, host=request.user)
        except (Meeting.DoesNotExist, ValueError):
            return Response({"error": "not found or not your meeting"}, status=404)

        if not meeting.is_active:
            return Response({"error": "meeting already ended"}, status=400)

        meeting.is_active = False
        meeting.ended_at = timezone.now()
        meeting.save()

        Participant.objects.filter(meeting=meeting, is_active=True).update(
            is_active=False, left_at=timezone.now()
        )
        return Response({"status": "ended"})
