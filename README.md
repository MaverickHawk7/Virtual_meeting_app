# Virtual Meeting Platform

A full-stack real-time video conferencing application built with Django, WebRTC, and LiveKit.

## Features

- **Video & Audio Conferencing** — Real-time media streaming powered by LiveKit SFU
- **User Authentication** — Secure JWT-based registration and login
- **Meeting Management** — Create, join, and end meetings with unique UUIDs
- **Real-Time Chat** — In-meeting text messaging via WebSocket
- **Hand Raise** — Signal to speak during meetings
- **WebRTC Signaling** — Peer-to-peer offer/answer/ICE candidate exchange
- **Participant Tracking** — Live join/leave notifications and presence management
- **Host Controls** — Meeting hosts can end meetings for all participants
- **Participant Limits** — Configurable max participants per meeting (default: 20)

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Django 4.2+ | Web framework & REST API |
| Django REST Framework | API endpoints |
| Django Channels | WebSocket support |
| Daphne | ASGI server (HTTP + WebSocket) |
| PostgreSQL 15 | Production database |
| Redis 7 | Channel layer message broker |
| LiveKit | SFU media server |
| SimpleJWT | JWT authentication |

### Frontend
| Technology | Purpose |
|---|---|
| HTML/CSS/JavaScript | Single-page application |
| LiveKit Web SDK | Video/audio streaming |
| WebSocket API | Real-time communication |

### Infrastructure
| Technology | Purpose |
|---|---|
| Docker Compose | Service orchestration |
| Nginx | Reverse proxy (production) |

## Project Structure

```
Virtual_meeting_platform/
├── frontend/
│   └── index.html              # Single-page frontend app
├── meetingapp/                  # Django project configuration
│   ├── asgi.py                 # ASGI entry point
│   ├── settings.py             # Production settings
│   ├── settings_dev.py         # Dev settings (SQLite, no Docker)
│   ├── urls.py                 # URL routing
│   ├── middleware.py           # WebSocket JWT auth middleware
│   └── routing.py              # WebSocket URL patterns
├── meetings/                   # Core Django app
│   ├── models.py               # Meeting & Participant models
│   ├── views.py                # REST API views
│   ├── consumers.py            # WebSocket consumer
│   ├── services.py             # LiveKit token generation
│   └── urls.py                 # API URL routing
├── docker-compose.yml          # PostgreSQL + Redis + LiveKit
├── requirements.txt            # Python dependencies
├── manage.py                   # Django CLI
└── .env.example                # Environment variable template
```

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- pip

### Quick Start (Development — No Docker Required)

```bash
# Clone the repository
git clone https://github.com/MaverickHawk7/virtual_meeting_app.git
cd virtual_meeting_app

# Install dependencies
pip install -r requirements.txt

# Run migrations
DJANGO_SETTINGS_MODULE=meetingapp.settings_dev python manage.py migrate

# Start the backend server
DJANGO_SETTINGS_MODULE=meetingapp.settings_dev python manage.py runserver 8000

# In another terminal, serve the frontend
python -m http.server 5500 --directory frontend
```

Then open `http://localhost:5500` in your browser.

### Full Setup (with Docker)

```bash
# Start infrastructure services
docker-compose up -d

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your settings

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a superuser (optional, for Django admin)
python manage.py createsuperuser

# Start the ASGI server
daphne -b 0.0.0.0 -p 8000 meetingapp.asgi:application

# Serve frontend
python -m http.server 5500 --directory frontend
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Create a new account |
| POST | `/api/auth/login/` | Login and get JWT tokens |
| POST | `/api/auth/refresh/` | Refresh access token |

### Meetings
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/meetings/` | List hosted meetings |
| POST | `/api/meetings/` | Create a new meeting |
| POST | `/api/meetings/<id>/join/` | Join a meeting |
| POST | `/api/meetings/<id>/leave/` | Leave a meeting |
| POST | `/api/meetings/<id>/end/` | End meeting (host only) |
| GET | `/api/meetings/<id>/participants/` | List active participants |

### WebSocket
Connect to `ws://host/ws/meeting/<uuid>/?token=<jwt>` for real-time features.

**Message Types:**
```json
{ "type": "chat",          "message": "Hello everyone!" }
{ "type": "hand_raise",    "raised": true }
{ "type": "webrtc_signal", "to": 1, "signal": { ... } }
```

## Database Models

### Meeting
- `id` (UUID) — Unique meeting identifier / join code
- `title` — Meeting display name
- `host` — Creator of the meeting
- `is_active` — Whether the meeting is currently live
- `max_participants` — Capacity limit (default: 20)

### Participant
- `meeting` — Associated meeting
- `user` — Associated user
- `role` — "host" or "participant"
- `is_active` — Currently in the meeting

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | `dev-secret-key-...` |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hostnames | `localhost,127.0.0.1` |
| `DB_NAME` | PostgreSQL database name | `meetingdb` |
| `DB_USER` | PostgreSQL user | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `postgres` |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `LIVEKIT_API_KEY` | LiveKit API key | `devkey` |
| `LIVEKIT_API_SECRET` | LiveKit API secret | `secret` |
| `LIVEKIT_URL` | LiveKit server URL | `ws://localhost:7880` |

## Production Deployment

1. Set `DEBUG=False` and generate a strong `SECRET_KEY`
2. Configure `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
3. Use HTTPS/WSS (required for browser camera/mic access)
4. Deploy behind Nginx as a reverse proxy
5. Use LiveKit Cloud or a dedicated LiveKit server
6. Add rate limiting to authentication endpoints
7. Run with Daphne or Uvicorn as the ASGI server

## License

This project is provided as-is for educational and development purposes.
