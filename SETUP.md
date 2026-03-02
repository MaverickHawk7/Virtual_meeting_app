# Setup Instructions

## Prerequisites
- Python 3.11+
- Docker + Docker Compose (for Postgres, Redis, LiveKit)
- pip

---

## 1. Start infrastructure

```bash
docker-compose up -d
```

This starts:
- PostgreSQL on 5432
- Redis on 6379
- LiveKit SFU on 7880 (dev mode, keys: devkey / secret)

---

## 2. Python environment

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 3. Environment variables

```bash
cp .env.example .env
# Edit .env if you changed any Docker defaults
```

---

## 4. Database migrations

```bash
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin
```

---

## 5. Run the server

**Development** (Daphne serves both HTTP + WebSocket):
```bash
daphne -b 0.0.0.0 -p 8000 meetingapp.asgi:application
```

Or with Django's built-in server (HTTP only, no WebSocket):
```bash
python manage.py runserver        # channels falls back to in-memory layer
```

Use Daphne for proper WebSocket support.

---

## 6. Open the frontend

Open `frontend/index.html` in your browser directly (file://) or serve it:
```bash
python -m http.server 5500 --directory frontend
```
Then open http://localhost:5500

---

## 7. Test end-to-end

1. Open two browser tabs at http://localhost:5500
2. Tab A: Register → Create Meeting → note the meeting ID
3. Tab B: Register (different user) → Join Meeting → paste the UUID
4. Both tabs should see each other's video

---

## Production notes

| Concern | What to do |
|---|---|
| ASGI server | Run Daphne or Uvicorn behind Nginx |
| Static files | `python manage.py collectstatic`, serve from Nginx |
| HTTPS/WSS | Required for camera/mic (browser security policy) |
| LiveKit | Use LiveKit Cloud instead of local container |
| `SECRET_KEY` | Generate a real random 50-char key |
| `DEBUG` | Set to False |
| `ALLOWED_HOSTS` | Your domain |
| `CORS_ALLOWED_ORIGINS` | Your frontend domain only |
| Rate limiting | Add django-ratelimit or put Nginx rate limits on /api/auth/ |
| Token in WS URL | Consider one-time nonce endpoint to avoid JWT in access logs |

---

## API Reference

```
POST /api/auth/register/        { username, email, password }
POST /api/auth/login/           { username, password }
POST /api/auth/refresh/         { refresh }

GET  /api/meetings/             → list my meetings
POST /api/meetings/             { title } → create meeting
POST /api/meetings/<id>/join/   → { sfu_token, sfu_url, is_host }
POST /api/meetings/<id>/leave/
POST /api/meetings/<id>/end/    (host only)
GET  /api/meetings/<id>/participants/

WS   ws://host/ws/meeting/<id>/?token=<jwt>
```

## WebSocket message protocol

Client → server:
```json
{ "type": "chat",       "message": "hello" }
{ "type": "hand_raise", "raised": true }
```

Server → client:
```json
{ "type": "participant_joined", "user_id": 1, "username": "alice" }
{ "type": "participant_left",   "user_id": 1, "username": "alice" }
{ "type": "chat",               "user_id": 1, "username": "alice", "message": "hello" }
{ "type": "hand_raise",         "user_id": 1, "username": "alice", "raised": true }
{ "type": "meeting_ended" }
```

WS close codes:
- 4001 = unauthenticated (bad/missing token)
- 4003 = forbidden (not a participant in this meeting)
