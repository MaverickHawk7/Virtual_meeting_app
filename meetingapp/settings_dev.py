"""
Dev/test settings — no Docker required.
Uses SQLite instead of PostgreSQL.
Uses in-memory channel layer instead of Redis.
Everything else inherits from settings.py.

Usage:
  DJANGO_SETTINGS_MODULE=meetingapp.settings_dev daphne ...
  # or
  python manage.py runserver --settings=meetingapp.settings_dev
"""
from .settings import *  # noqa: F401, F403

BASE_DIR = BASE_DIR  # already set by parent  # noqa: F405

# ── SQLite (no Postgres needed) ───────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_dev.sqlite3",
    }
}

# ── In-memory channel layer (no Redis needed) ────────────────────────────────
# NOTE: in-memory layer does NOT work across multiple processes.
# For single-process dev (daphne single worker) this is fine.
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# ── Relaxed CORS for local file:// and localhost ─────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# Keep DEBUG on
DEBUG = True
ALLOWED_HOSTS = ["*"]
