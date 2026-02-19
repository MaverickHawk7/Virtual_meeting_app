"""
Generates the technical documentation PDF for the Videocall Platform codebase.
Run: python generate_pdf.py
Output: VideocallPlatform_TechDoc.pdf
"""

from fpdf import FPDF
from fpdf.enums import XPos, YPos

# Colour palette
DARK_BG     = (15,  23,  42)
ACCENT      = (37,  99,  235)
ACCENT_LITE = (219, 234, 254)
BODY_CLR    = (30,  41,  59)
MUTED_CLR   = (100, 116, 139)
CODE_BG     = (241, 245, 249)
CODE_FG     = (51,  65,  85)
DIVIDER     = (203, 213, 225)
WHITE       = (255, 255, 255)


def S(text):
    """Replace Unicode chars not supported by Helvetica (latin-1 only)."""
    return (str(text)
        .replace('\u2014', '--').replace('\u2013', '-')
        .replace('\u2022', '*').replace('\u2018', "'").replace('\u2019', "'")
        .replace('\u201c', '"').replace('\u201d', '"').replace('\u2026', '...')
        .replace('\u2192', '->').replace('\u2190', '<-').replace('\u00a0', ' ')
        .replace('\u2500', '-').replace('\u2550', '=').replace('\u2502', '|')
        .replace('\u251c', '+').replace('\u2514', '+').replace('\u252c', '+')
        .replace('\u2560', '+').replace('\u2588', '#').replace('\u00b7', '.')
        .replace('\u2713', 'v').replace('\u2718', 'x').replace('\u25cf', '*')
        .replace('\u2550', '=').replace('\u255e', '+').replace('\u2561', '+')
    )


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(auto=True, margin=22)
        self._current_section = ""

    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*DARK_BG)
        self.rect(0, 0, 210, 12, "F")
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*MUTED_CLR)
        self.set_xy(10, 3)
        self.cell(0, 6, "Videocall Platform -- Technical Documentation", align="L")
        self.set_xy(10, 3)
        self.cell(0, 6, self._current_section, align="R")
        self.ln(6)

    def footer(self):
        self.set_y(-14)
        self.set_draw_color(*DIVIDER)
        self.set_line_width(0.3)
        self.line(20, self.get_y(), 190, self.get_y())
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MUTED_CLR)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")

    def section(self, title):
        self._current_section = S(title)
        self.ln(6)
        self.set_fill_color(*ACCENT)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 9, f"  {S(title)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(3)
        self.set_text_color(*BODY_CLR)

    def subsection(self, title):
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*ACCENT)
        self.cell(0, 7, S(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*BODY_CLR)
        self.ln(1)

    def body(self, text, indent=0):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*BODY_CLR)
        self.set_x(20 + indent)
        self.multi_cell(170 - indent, 5.5, S(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def bullet(self, text, indent=4):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*BODY_CLR)
        self.set_x(20 + indent)
        self.set_fill_color(*ACCENT)
        self.ellipse(20 + indent, self.get_y() + 2, 1.5, 1.5, "F")
        self.set_x(20 + indent + 4)
        self.multi_cell(166 - indent, 5.5, S(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def code_block(self, text, label=""):
        self.ln(2)
        if label:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*MUTED_CLR)
            self.cell(0, 5, S(label), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        x, y = self.get_x(), self.get_y()
        lines = S(text).split("\n")
        h = len(lines) * 4.5 + 4
        self.set_fill_color(*CODE_BG)
        self.set_draw_color(*DIVIDER)
        self.set_line_width(0.3)
        self.rect(x, y, 170, h, "DF")
        self.set_font("Courier", "", 8.5)
        self.set_text_color(*CODE_FG)
        self.set_y(y + 2)
        for line in lines:
            self.set_x(x + 3)
            self.cell(164, 4.5, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        self.set_text_color(*BODY_CLR)

    def flow_step(self, num, actor, action, detail=""):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(*ACCENT_LITE)
        self.set_text_color(*ACCENT)
        self.set_x(20)
        self.cell(7, 6, str(num), align="C", fill=True)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*DARK_BG)
        self.cell(28, 6, f" {S(actor)}")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*BODY_CLR)
        self.multi_cell(135, 6, S(action), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if detail:
            self.set_font("Helvetica", "I", 8.5)
            self.set_text_color(*MUTED_CLR)
            self.set_x(55)
            self.multi_cell(135, 5, S(detail), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def kv_table(self, rows, col1=50, col2=120):
        for i, (k, v) in enumerate(rows):
            fill = i % 2 == 0
            self.set_fill_color(248, 250, 252) if fill else self.set_fill_color(*WHITE)
            self.set_text_color(*ACCENT)
            self.set_font("Helvetica", "B", 9.5)
            self.cell(col1, 6.5, f"  {S(k)}", fill=fill)
            self.set_text_color(*BODY_CLR)
            self.set_font("Helvetica", "", 9.5)
            self.multi_cell(col2, 6.5, S(v), fill=fill, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def callout(self, text, color=None):
        color = color or ACCENT_LITE
        self.set_fill_color(*color)
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.5)
        x, y = self.get_x(), self.get_y()
        self.set_font("Helvetica", "I", 9.5)
        self.set_text_color(*BODY_CLR)
        self.multi_cell(170, 6, f"  {S(text)}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.line(20, y, 20, self.get_y() - 1)
        self.ln(3)
        self.set_text_color(*BODY_CLR)

    def divider(self):
        self.ln(2)
        self.set_draw_color(*DIVIDER)
        self.set_line_width(0.3)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(4)


# =============================================================================
#  BUILD PDF
# =============================================================================
pdf = PDF()

# ---------------------------------------------------------------------------
# COVER PAGE
# ---------------------------------------------------------------------------
pdf.add_page()
pdf.set_fill_color(*DARK_BG)
pdf.rect(0, 0, 210, 297, "F")

pdf.set_y(60)
pdf.set_font("Helvetica", "B", 32)
pdf.set_text_color(*WHITE)
pdf.cell(0, 14, "Videocall Platform", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

pdf.set_font("Helvetica", "", 16)
pdf.set_text_color(*ACCENT_LITE)
pdf.cell(0, 10, "Technical Architecture & Codebase Guide", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

pdf.ln(8)
pdf.set_draw_color(*ACCENT)
pdf.set_line_width(1)
pdf.line(60, pdf.get_y(), 150, pdf.get_y())
pdf.ln(10)

pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(148, 163, 184)
for line in [
    "Django 5  |  Django REST Framework  |  Django Channels",
    "Native WebRTC (P2P)  |  WebSockets  |  JWT Auth",
    "SQLite (dev)  |  PostgreSQL (prod)  |  Redis",
]:
    pdf.cell(0, 8, line, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

pdf.ln(60)
pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(*ACCENT_LITE)
pdf.cell(0, 7, "For internal use -- written for junior engineers joining the team",
         align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "", 9)
pdf.set_text_color(100, 116, 139)
pdf.cell(0, 6, "February 2026", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)


# ---------------------------------------------------------------------------
# 1. WHAT WE BUILT
# ---------------------------------------------------------------------------
pdf.add_page()
pdf.section("1. What We Built -- and Why")

pdf.body(
    "This is an MVP video-calling platform -- think a stripped-down Zoom. Two or more people "
    "can open a browser tab, register, create or join a meeting room, and see and hear each other "
    "through their webcam and microphone. There is also a live chat panel and hand-raise signalling."
)
pdf.body(
    "The project is intentionally minimal. No React, no Redux, no microservices. Every architectural "
    "decision was made to maximise clarity and correctness, not to impress on a resume. If you "
    "understand this codebase end-to-end, you understand the foundations of real-time web applications."
)

pdf.subsection("The hard problem: real-time audio and video")
pdf.body(
    "Traditional web apps are request-response: the browser asks, the server answers, done. "
    "Video calling breaks that model completely. You need:"
)
for b in [
    "Continuous, low-latency streams of audio and video data flowing between browsers.",
    "A way for two browsers to discover each other and negotiate a direct connection.",
    "A fallback channel that works even when browsers are behind firewalls or NAT.",
    "A signalling mechanism to coordinate before the direct connection is established.",
]:
    pdf.bullet(b)

pdf.body(
    "The industry solution is WebRTC -- a set of browser APIs that handle all the hard parts of "
    "peer-to-peer media. Django handles everything else: identity, meeting state, access control, "
    "and acting as the signalling relay."
)

pdf.subsection("Scope decisions")
pdf.kv_table([
    ("In scope",    "Auth, meeting CRUD, 2+ participant video/audio, chat, hand-raise, clean leave/end."),
    ("Out of scope","Recording, screen share, virtual backgrounds, mobile apps, >10 participant scale."),
    ("Dev mode",    "SQLite + in-memory channel layer. Zero Docker required to run locally."),
    ("Prod mode",   "PostgreSQL + Redis + LiveKit SFU. Swap settings_dev.py for settings.py."),
])

# ---------------------------------------------------------------------------
# 2. ARCHITECTURE OVERVIEW
# ---------------------------------------------------------------------------
pdf.add_page()
pdf.section("2. Architecture Overview")

pdf.body(
    "The system has three runtime components and three infrastructure dependencies. "
    "Here is how they relate to each other:"
)

pdf.code_block(
    "BROWSER (index.html -- vanilla JS)\n"
    "  |\n"
    "  |-- REST (HTTP/JSON + JWT) ---------> Django REST API (port 8000)\n"
    "  |                                       meetingapp/urls.py -> meetings/views.py\n"
    "  |                                            |\n"
    "  |                                       PostgreSQL / SQLite\n"
    "  |                                       (users, meetings, participants)\n"
    "  |\n"
    "  |-- WebSocket (ws://host/ws/meeting/<id>/?token=JWT)\n"
    "  |     Django Channels Consumer (meetings/consumers.py)\n"
    "  |     Channel Layer: Redis (prod) / InMemory (dev)\n"
    "  |     Handles: presence, chat, hand-raise, WebRTC signalling relay\n"
    "  |\n"
    "  |-- WebRTC (DTLS/SRTP -- direct P2P between browsers)\n"
    "        Signalling (offer/answer/ICE) relayed through the WebSocket above\n"
    "        Media (audio/video) flows directly browser-to-browser\n"
    "        STUN: stun.l.google.com (NAT traversal for non-localhost)",
    "System diagram"
)

pdf.callout(
    "Key insight: Django never sees a single byte of audio or video data. "
    "Once the WebRTC connection is established, media flows directly between browsers. "
    "Django's job is done at that point -- it was only ever the matchmaker."
)

pdf.subsection("Component responsibilities")
pdf.kv_table([
    ("Django REST API",    "Auth (register/login/JWT refresh), meeting CRUD, join/leave/end logic, "
                            "SFU token issuance, participant tracking."),
    ("Django Channels",    "WebSocket connections, presence broadcast (joined/left), chat relay, "
                            "hand-raise relay, WebRTC signalling relay (offer/answer/ICE)."),
    ("Channel Layer",      "In-memory (dev) or Redis (prod). Lets multiple consumers communicate. "
                            "Required for group broadcasts across WebSocket connections."),
    ("Native WebRTC",      "Browser-native API. Handles SDP negotiation, ICE candidate gathering, "
                            "DTLS handshake, SRTP media encryption and transmission."),
    ("SQLite/PostgreSQL",  "Stores User, Meeting, Participant records. Django ORM abstracts the driver."),
    ("Redis (prod only)",  "Channel layer backend. Also suitable for caching and session storage later."),
])

# ---------------------------------------------------------------------------
# 3. TECH STACK
# ---------------------------------------------------------------------------
pdf.add_page()
pdf.section("3. Tech Stack -- Every Piece Explained")

pdf.subsection("Django 5 + Django REST Framework")
pdf.body(
    "Django is a batteries-included Python web framework. It gives us the ORM, migrations, "
    "admin panel, auth system, and URL router out of the box. Django REST Framework (DRF) "
    "adds serialisation, authentication classes, and view helpers for building APIs."
)
pdf.body(
    "We use class-based APIViews rather than ViewSets because the API surface is small and "
    "explicit views are easier to reason about. Each view maps to exactly one URL and does one thing."
)
pdf.code_block(
    "# meetings/views.py -- typical DRF view\n"
    "class MeetingJoinView(APIView):\n"
    "    permission_classes = [IsAuthenticated]   # JWT required\n"
    "\n"
    "    def post(self, request, meeting_id):\n"
    "        meeting = Meeting.objects.get(id=meeting_id, is_active=True)\n"
    "        # ... business logic ...\n"
    "        return Response({'sfu_token': token, 'is_host': True})"
)

pdf.subsection("JWT Authentication (djangorestframework-simplejwt)")
pdf.body(
    "JSON Web Tokens are stateless signed tokens. When a user logs in, the server creates "
    "an access token (1 hour) and a refresh token (7 days). The access token travels with "
    "every API request in the Authorization header:"
)
pdf.code_block("Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
pdf.body(
    "The server validates the signature using SECRET_KEY -- no database lookup needed. "
    "This is why JWTs are fast. The refresh token is used to obtain a new access token "
    "when the old one expires, without re-entering a password."
)
pdf.callout(
    "WebSocket connections cannot send custom headers in browsers, so the JWT is passed "
    "as a query parameter: ws://host/ws/meeting/<id>/?token=<jwt>. "
    "Our JWTAuthMiddleware (meetingapp/middleware.py) reads and validates it before "
    "the consumer's connect() method is even called."
)

pdf.subsection("Django Channels")
pdf.body(
    "Standard Django is synchronous and stateless -- perfect for HTTP but useless for WebSockets, "
    "which are long-lived persistent connections. Django Channels extends Django with an ASGI "
    "(Asynchronous Server Gateway Interface) layer that handles both HTTP and WebSocket protocols."
)
pdf.body(
    "The key abstraction is a Consumer -- think of it as a Django view for WebSocket connections. "
    "Our MeetingConsumer has three lifecycle methods:"
)
pdf.kv_table([
    ("connect()",    "Called when browser opens the WebSocket. Validates JWT, checks meeting access, "
                     "joins the channel group, sends room_state to the new participant."),
    ("receive()",    "Called for every message the browser sends. Dispatches to chat, hand_raise, "
                     "or webrtc_signal handlers."),
    ("disconnect()", "Called when the browser closes the tab or leaves. Broadcasts participant_left "
                     "and removes from the channel group."),
])

pdf.subsection("Channel Layer (InMemory / Redis)")
pdf.body(
    "A channel layer is a message broker between consumers. Without it, Consumer A (Alice's tab) "
    "cannot send a message to Consumer B (Bob's tab) because they are separate Python coroutines "
    "with no shared memory."
)
pdf.code_block(
    "# How a chat message travels from Alice to Bob:\n"
    "\n"
    "Alice browser  --[WS send]--> AliceConsumer.receive()\n"
    "                                    |\n"
    "                          channel_layer.group_send(\n"
    "                              'meeting_<uuid>',\n"
    "                              {'type': 'chat.message', ...}\n"
    "                          )\n"
    "                                    |\n"
    "                          BobConsumer.chat_message(event)\n"
    "                                    |\n"
    "Bob browser  <--[WS send]-- BobConsumer"
)

# ---------------------------------------------------------------------------
# 4. WEBRTC
# ---------------------------------------------------------------------------
pdf.add_page()
pdf.section("4. WebRTC -- How Browsers Connect Directly")

pdf.body(
    "WebRTC (Web Real-Time Communication) is a collection of browser APIs and protocols that "
    "enable browsers to exchange audio, video, and data directly without a server in the media path. "
    "This is the most complex part of the system. Read this section carefully."
)

pdf.subsection("The three problems WebRTC solves")
pdf.kv_table([
    ("Media capture",  "navigator.mediaDevices.getUserMedia() -- access camera and microphone."),
    ("NAT traversal",  "ICE + STUN -- find a network path between two browsers that may be behind routers."),
    ("Secure transport","DTLS handshake (like TLS but for UDP) + SRTP -- all media is encrypted end-to-end."),
])

pdf.subsection("SDP -- Session Description Protocol")
pdf.body(
    "Before any media can flow, two peers must agree on: what codecs they support (H.264? VP8? Opus?), "
    "what network addresses they can be reached at, and what direction the streams will flow. "
    "They exchange this information as SDP blobs -- large text documents. "
    "You never write SDP manually. The browser generates it. Your job as the developer "
    "is simply to relay it between the two peers -- exactly what our Django Channels consumer does."
)

pdf.subsection("The full signalling flow -- step by step")
pdf.body(
    "The user with the HIGHER numeric user_id always creates the offer. "
    "This avoids 'glare' -- the situation where both sides try to offer simultaneously, "
    "which would cause the connection to fail."
)

pdf.flow_step(1, "Alice",    "Registers (user_id=3), creates a meeting via REST.",
              "POST /api/meetings/ -> {id: 'uuid...', title: 'Standup'}")
pdf.flow_step(2, "Alice",    "Calls POST /api/meetings/<id>/join/ -- Participant row created in DB.",
              "Response: {is_host: true, meeting_id: '...'}")
pdf.flow_step(3, "Alice",    "Opens WebSocket: ws://host/ws/meeting/<id>/?token=<jwt>",
              "MeetingConsumer.connect() fires. Alice joins groups 'meeting_<uuid>' and 'user_3'.")
pdf.flow_step(4, "Server",   "Sends room_state to Alice: {participants: []}",
              "Room is empty. Alice waits.")
pdf.flow_step(5, "Bob",      "Registers (user_id=4), joins the same meeting via REST.",
              "POST /api/meetings/<id>/join/ -> is_host=false")
pdf.flow_step(6, "Bob",      "Opens WebSocket. Server sends Bob room_state: [{user_id:3, username:'alice'}]",
              "Bob sees Alice is already here. Since Bob's id (4) > Alice's id (3), Bob creates the offer.")
pdf.flow_step(7, "Bob",      "pc.createOffer() -> SDP blob. pc.setLocalDescription(offer).",
              "Sends: {type:'webrtc_signal', to:3, signal:{type:'offer', sdp:{...}}}")
pdf.flow_step(8, "Server",   "MeetingConsumer relays the signal to Alice's personal group 'user_3'.",
              "channel_layer.group_send('user_3', {type:'webrtc.relay', ...})")
pdf.flow_step(9, "Alice",    "Receives the offer. pc.setRemoteDescription(offer). pc.createAnswer().",
              "Sends back: {type:'webrtc_signal', to:4, signal:{type:'answer', sdp:{...}}}")
pdf.flow_step(10, "Bob",     "pc.setRemoteDescription(answer). SDP negotiation complete.",
              "Both sides now know what codecs to use.")
pdf.flow_step(11, "Both",    "ICE candidate gathering begins. Each browser finds its own network addresses.",
              "Each candidate is sent via WS to the other peer.")
pdf.flow_step(12, "Both",    "pc.addIceCandidate() for each received candidate.",
              "The browsers try every candidate pair until one works.")
pdf.flow_step(13, "Both",    "DTLS handshake completes over the best network path.",
              "Encrypted SRTP media stream begins. Audio and video now flow directly P2P.")

pdf.callout(
    "On localhost, step 12 resolves immediately to a loopback (127.0.0.1) candidate. "
    "No STUN server is needed. Over the internet, STUN helps discover the public IP. "
    "TURN (not implemented) relays media when P2P is blocked by a corporate firewall."
)

# ---------------------------------------------------------------------------
# 5. CODEBASE WALKTHROUGH
# ---------------------------------------------------------------------------
pdf.add_page()
pdf.section("5. Codebase Walkthrough")

pdf.subsection("Project layout")
pdf.code_block(
    "Django/\n"
    "|-- manage.py                   # Django CLI entry point\n"
    "|-- requirements.txt            # Python dependencies\n"
    "|-- .env.example                # Copy to .env and fill in secrets\n"
    "|-- docker-compose.yml          # Postgres + Redis + LiveKit (prod)\n"
    "|-- SETUP.md                    # How to run the project\n"
    "|\n"
    "|-- meetingapp/                 # Django project config\n"
    "|   |-- settings.py             # Production settings\n"
    "|   |-- settings_dev.py         # Dev overrides (SQLite, in-memory)\n"
    "|   |-- asgi.py                 # ASGI entry -- routes HTTP vs WebSocket\n"
    "|   |-- middleware.py           # JWT auth for WebSocket connections\n"
    "|   |-- routing.py              # WebSocket URL patterns\n"
    "|   +-- urls.py                 # HTTP URL patterns\n"
    "|\n"
    "|-- meetings/                   # The only Django app\n"
    "|   |-- models.py               # Meeting + Participant DB models\n"
    "|   |-- views.py                # 6 REST API views\n"
    "|   |-- consumers.py            # WebSocket consumer (presence + signalling)\n"
    "|   |-- services.py             # SFU token abstraction (LiveKit)\n"
    "|   |-- urls.py                 # REST URL patterns\n"
    "|   +-- migrations/             # Auto-generated DB schema\n"
    "|\n"
    "+-- frontend/\n"
    "    +-- index.html              # Entire frontend -- ~500 lines vanilla JS"
)

pdf.subsection("meetingapp/asgi.py -- the front door")
pdf.body(
    "Every connection enters the system here. Daphne (the ASGI server) calls this module "
    "for every incoming connection. ProtocolTypeRouter inspects the connection type:"
)
pdf.code_block(
    "application = ProtocolTypeRouter({\n"
    "    'http':      get_asgi_application(),         # -> Django views\n"
    "    'websocket': AllowedHostsOriginValidator(\n"
    "                     JWTAuthMiddlewareStack(\n"
    "                         URLRouter(websocket_urlpatterns)  # -> consumers\n"
    "                     )\n"
    "                 ),\n"
    "})"
)
pdf.body(
    "The middleware chain runs before any consumer code: AllowedHostsOriginValidator blocks "
    "connections from unknown origins. JWTAuthMiddleware reads ?token=, validates the JWT, "
    "and attaches the User to scope['user']. By the time connect() runs, scope['user'] is set."
)

pdf.subsection("meetings/models.py -- the data layer")
pdf.body("Two models. That is all the persistent state the application needs:")
pdf.kv_table([
    ("Meeting",     "id (UUID PK), title, host (FK User), is_active, created_at, ended_at, "
                     "max_participants. The UUID is the join code shared with participants."),
    ("Participant", "meeting (FK), user (FK), role ('host'/'participant'), joined_at, left_at, "
                     "is_active. Unique together on (meeting, user). is_active=False means left."),
])

pdf.subsection("meetings/views.py -- the API layer")
pdf.body("Six views, one responsibility each:")
pdf.kv_table([
    ("RegisterView",          "POST /api/auth/register/ -- create user, return JWT pair."),
    ("LoginView",             "POST /api/auth/login/ -- authenticate, return JWT pair."),
    ("MeetingListCreateView", "GET list | POST create meeting."),
    ("MeetingJoinView",       "Validate access, create/reactivate Participant row, return SFU token."),
    ("MeetingLeaveView",      "Mark Participant inactive. If host leaves, end the meeting entirely."),
    ("MeetingEndView",        "Host only. End meeting, mark all participants as left."),
])

pdf.subsection("meetings/consumers.py -- the real-time layer")
pdf.body(
    "The most important file in the backend. One consumer does two distinct jobs "
    "over the same WebSocket connection:"
)
pdf.kv_table([
    ("Presence broadcast", "participant_joined, participant_left, chat, hand_raise go to the "
                            "whole meeting group (every connected user receives them)."),
    ("Signalling relay",   "webrtc_signal messages (offer/answer/ICE) are unicast -- delivered only "
                            "to the target user's personal group 'user_<id>'."),
])
pdf.body(
    "Each connected user joins TWO channel groups: the meeting group for broadcasts, "
    "and a personal group for direct messages. This is how WebRTC signals are routed "
    "to specific peers without broadcasting them to everyone in the room."
)

pdf.subsection("frontend/index.html -- everything the user sees")
pdf.body(
    "The entire frontend is a single file. Three logical sections: "
    "Auth (register/login), Lobby (create or join a meeting), and the Meeting room (video + chat). "
    "Vanilla JS, no framework. The key state objects:"
)
pdf.code_block(
    "const state = { access, refresh, user, meetingId, presenceWs, ... };\n"
    "let localStream = null;        // MediaStream from getUserMedia()\n"
    "const connections = {};        // { userId: RTCPeerConnection }"
)

# ---------------------------------------------------------------------------
# 6. REQUEST FLOWS
# ---------------------------------------------------------------------------
pdf.add_page()
pdf.section("6. Complete Request Flows")

pdf.subsection("Login flow")
pdf.code_block(
    "Browser                          Django\n"
    "  |\n"
    "  |-- POST /api/auth/login/ ------>\n"
    "  |   {username, password}           authenticate(username, password)\n"
    "  |                                  RefreshToken.for_user(user)\n"
    "  |<-- 200 {access, refresh, user} --\n"
    "  |\n"
    "  |  access token stored in JS memory (state.access)\n"
    "  |  refresh token stored in JS memory (state.refresh)"
)

pdf.subsection("Join meeting + WebRTC connection (condensed)")
pdf.code_block(
    "Browser A (Alice, id=3)          Django                    Browser B (Bob, id=4)\n"
    "\n"
    "POST /meetings/<id>/join/ ------> creates Participant row\n"
    "<-- {is_host:true, ...} --------\n"
    "\n"
    "WS connect /?token=alice_jwt ---> consumer.connect()\n"
    "                                  group_add('meeting_<id>')\n"
    "                                  group_add('user_3')\n"
    "<-- room_state {participants:[]}  (room empty, Alice waits)\n"
    "\n"
    "                                 <--- WS connect /?token=bob_jwt\n"
    "                                      group_add('meeting_<id>')\n"
    "                                      group_add('user_4')\n"
    "<-- participant_joined (Bob)          room_state {participants:[alice]}\n"
    "                                      Bob: id(4) > id(3) -> create offer\n"
    "                                 <--- {webrtc_signal, to:3, signal:{offer}}\n"
    "<-- {webrtc_signal, from:4}  ----     relay to 'user_3'\n"
    "Alice: setRemoteDesc, createAnswer\n"
    "--> {webrtc_signal, to:4, signal:{answer}} -> relay to 'user_4'\n"
    "ICE candidates exchanged via WS <---+---> ICE candidates\n"
    "\n"
    "DTLS handshake + SRTP media A <=========================> B (direct P2P)"
)

pdf.subsection("Chat message flow")
pdf.code_block(
    "Bob types 'hello' and hits Send\n"
    "\n"
    "Bob browser  -> WS send {type:'chat', message:'hello'}\n"
    "             -> BobConsumer.receive()\n"
    "             -> channel_layer.group_send('meeting_<id>', {type:'chat.message', ...})\n"
    "             -> AliceConsumer.chat_message(event)  [and BobConsumer too]\n"
    "             -> Alice WS: {type:'chat', username:'bob', message:'hello'}\n"
    "             -> Bob   WS: {type:'chat', username:'bob', message:'hello'}\n"
    "\n"
    "Both browsers render the message in the chat panel."
)

# ---------------------------------------------------------------------------
# 7. SETTINGS
# ---------------------------------------------------------------------------
pdf.add_page()
pdf.section("7. Settings -- Dev vs Production")

pdf.body(
    "settings_dev.py inherits everything from settings.py and overrides just three things. "
    "This means you can develop with zero external services running."
)
pdf.code_block(
    "# meetingapp/settings_dev.py\n"
    "from .settings import *\n"
    "\n"
    "DATABASES = {\n"
    "    'default': {\n"
    "        'ENGINE': 'django.db.backends.sqlite3',\n"
    "        'NAME': BASE_DIR / 'db_dev.sqlite3',   # single file, no server needed\n"
    "    }\n"
    "}\n"
    "\n"
    "CHANNEL_LAYERS = {\n"
    "    'default': {\n"
    "        'BACKEND': 'channels.layers.InMemoryChannelLayer'  # no Redis needed\n"
    "    }\n"
    "}\n"
    "\n"
    "CORS_ALLOW_ALL_ORIGINS = True  # allow localhost:5500 during dev"
)
pdf.body("For production, set these environment variables in a .env file:")
pdf.kv_table([
    ("SECRET_KEY",         "50-character random string. Never commit this."),
    ("DB_*",               "PostgreSQL connection details."),
    ("REDIS_HOST/PORT",    "Redis instance for the channel layer."),
    ("LIVEKIT_*",          "LiveKit Cloud credentials for the SFU (replaces P2P for scale)."),
    ("CORS_ALLOWED_ORIGINS","Comma-separated list of allowed frontend origins."),
    ("ALLOWED_HOSTS",      "Comma-separated list of domain names the server responds to."),
])

# ---------------------------------------------------------------------------
# 8. SECURITY
# ---------------------------------------------------------------------------
pdf.section("8. Security Model")

pdf.kv_table([
    ("API endpoints",     "All except /register/ and /login/ require a valid JWT. "
                           "DRF validates the token on every request via JWTAuthentication."),
    ("WebSocket",         "JWT validated in JWTAuthMiddleware before connect() runs. "
                           "Bad/missing token -> close(code=4001). Not in meeting -> close(code=4003)."),
    ("Meeting access",    "consumers.py._check_access() verifies the user is host or active participant."),
    ("Meeting IDs",       "UUIDv4. 2^122 possible values. Not guessable by enumeration."),
    ("Participant cap",   "max_participants enforced in MeetingJoinView. Prevents room flooding."),
    ("XSS prevention",    "All user content is HTML-escaped via escHtml() before DOM insertion."),
    ("CORS",              "Allowed origins configured explicitly -- not wildcard '*' in production."),
    ("WebRTC media",      "DTLS + SRTP. All audio/video is encrypted end-to-end by the browser."),
])

pdf.subsection("Known limitations in this MVP")
for b in [
    "JWT in WebSocket query parameter appears in server access logs. Production fix: issue a "
    "short-lived one-time nonce via POST /api/ws-ticket/ and exchange it in the WS handshake.",
    "No rate limiting on /api/auth/ endpoints. Add django-ratelimit before going live.",
    "P2P WebRTC does not scale beyond ~4 participants gracefully. Above that, switch to the "
    "LiveKit SFU path -- services.py is already wired for it.",
    "Refresh tokens stored in JS memory -- lost on page reload. Production apps use httpOnly "
    "cookies for refresh tokens to prevent XSS theft.",
]:
    pdf.bullet(b)

# ---------------------------------------------------------------------------
# 9. HOW TO RUN
# ---------------------------------------------------------------------------
pdf.add_page()
pdf.section("9. How to Run Locally")

pdf.code_block(
    "# Terminal 1 -- Backend\n"
    "cd C:/Users/AB/Desktop/Django\n"
    "pip install -r requirements.txt\n"
    "set DJANGO_SETTINGS_MODULE=meetingapp.settings_dev\n"
    "python manage.py makemigrations meetings\n"
    "python manage.py migrate\n"
    "python -m daphne -b 127.0.0.1 -p 8000 meetingapp.asgi:application\n"
    "\n"
    "# Terminal 2 -- Frontend\n"
    "python -m http.server 5500 --directory frontend\n"
    "\n"
    "# Browser\n"
    "# Tab 1: http://localhost:5500 -> Register alice, Create meeting, copy UUID\n"
    "# Tab 2: http://localhost:5500 -> Register bob,   Join meeting,   paste UUID"
)

pdf.section("10. How to Extend This")

pdf.subsection("Adding screen share")
pdf.body(
    "Replace getUserMedia with getDisplayMedia for the screen share track. "
    "Add a new RTCPeerConnection per participant with the display stream, "
    "or re-negotiate the existing connection to add a third track. "
    "No backend changes needed -- the signalling channel already handles arbitrary signals."
)

pdf.subsection("Scaling beyond 4 participants")
pdf.body(
    "P2P WebRTC creates N*(N-1)/2 connections. At 4 participants that is 6 connections per browser. "
    "Switch to the LiveKit SFU: set LIVEKIT_* env vars, run docker-compose up livekit, "
    "and restore the LiveKit JS SDK in index.html. The backend token issuance in services.py "
    "is already implemented and tested."
)

pdf.subsection("Adding chat history")
pdf.body(
    "Create a ChatMessage model (meeting FK, user FK, message, sent_at). "
    "In MeetingConsumer.receive(), after group_send, call "
    "await database_sync_to_async(ChatMessage.objects.create)(...). "
    "Add GET /api/meetings/<id>/messages/ to load history on join."
)

pdf.subsection("Deploying to production")
pdf.kv_table([
    ("ASGI server",  "Run Daphne with Nginx as a reverse proxy. Or Uvicorn + Gunicorn."),
    ("HTTPS/WSS",    "Required for camera/mic access in production. Use Let's Encrypt (Certbot)."),
    ("Static files", "python manage.py collectstatic, serve from Nginx or S3 + CloudFront."),
    ("LiveKit",      "Use LiveKit Cloud (cloud.livekit.io) or self-host on a VM with UDP ports open."),
    ("Secrets",      "Use a real secrets manager (AWS SSM, HashiCorp Vault) instead of .env files."),
])

# ---------------------------------------------------------------------------
# 11. QUICK REFERENCE
# ---------------------------------------------------------------------------
pdf.add_page()
pdf.section("11. Quick Reference")

pdf.subsection("API Endpoints")
pdf.code_block(
    "POST   /api/auth/register/                  { username, email, password }\n"
    "POST   /api/auth/login/                     { username, password }\n"
    "POST   /api/auth/refresh/                   { refresh }\n"
    "\n"
    "GET    /api/meetings/                        list my meetings   [auth required]\n"
    "POST   /api/meetings/                        { title }          [auth required]\n"
    "POST   /api/meetings/<uuid>/join/        ->  { sfu_token, is_host, title }\n"
    "POST   /api/meetings/<uuid>/leave/\n"
    "POST   /api/meetings/<uuid>/end/             host only\n"
    "GET    /api/meetings/<uuid>/participants/"
)

pdf.subsection("WebSocket Message Protocol")
pdf.code_block(
    "# Client -> Server\n"
    '{ "type": "chat",         "message": "hello" }\n'
    '{ "type": "hand_raise",   "raised": true }\n'
    '{ "type": "webrtc_signal","to": 4, "signal": { "type": "offer",  "sdp": {...} } }\n'
    '{ "type": "webrtc_signal","to": 4, "signal": { "type": "answer", "sdp": {...} } }\n'
    '{ "type": "webrtc_signal","to": 4, "signal": { "type": "ice", "candidate": {...} } }\n'
    "\n"
    "# Server -> Client\n"
    '{ "type": "room_state",        "participants": [{user_id, username}, ...] }\n'
    '{ "type": "participant_joined", "user_id": 4, "username": "bob" }\n'
    '{ "type": "participant_left",   "user_id": 4, "username": "bob" }\n'
    '{ "type": "chat",              "user_id": 4, "username": "bob", "message": "hi" }\n'
    '{ "type": "hand_raise",        "user_id": 4, "raised": true }\n'
    '{ "type": "webrtc_signal",     "from": 4, "signal": { "type": "offer", ... } }\n'
    '{ "type": "meeting_ended" }'
)

pdf.subsection("File to Responsibility Map")
pdf.kv_table([
    ("meetingapp/asgi.py",       "Entry point. Routes HTTP vs WebSocket. Applies middleware chain."),
    ("meetingapp/middleware.py", "Validates JWT from WS query param. Populates scope['user']."),
    ("meetingapp/settings.py",   "Production config. Read via python-decouple from .env."),
    ("meetingapp/settings_dev.py","Dev overrides: SQLite + InMemoryChannelLayer."),
    ("meetingapp/routing.py",    "Maps ws/meeting/<uuid>/ -> MeetingConsumer."),
    ("meetings/models.py",       "Meeting + Participant ORM models."),
    ("meetings/views.py",        "6 REST views: auth, meeting CRUD, join, leave, end."),
    ("meetings/consumers.py",    "WebSocket consumer: presence, chat, WebRTC relay."),
    ("meetings/services.py",     "SFU token generation (LiveKit). Swap to change provider."),
    ("meetings/urls.py",         "REST URL patterns for the meetings app."),
    ("frontend/index.html",      "Complete frontend: auth + lobby + meeting room + WebRTC."),
    ("docker-compose.yml",       "PostgreSQL + Redis + LiveKit for production-like local dev."),
    ("requirements.txt",         "All Python dependencies."),
    (".env.example",             "Template for environment variables. Copy to .env."),
])

# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------
output = "VideocallPlatform_TechDoc.pdf"
pdf.output(output)
print(f"PDF written: {output}  ({pdf.page} pages)")
